import os

import dotenv
dotenv.load_dotenv()

import logging
import re
import asyncio
import json
import httpx
from google import genai
from google.genai import types
from app import db
from sqlalchemy import func
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from gemini_function_schemas import gemini_function_schemas

# Initialize Gemini client and model name
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
MODEL_NAME = "gemini-2.5-flash"

# In-memory store for pending transfers: {user_id: {"to_name": ..., "amount": ...}}
pending_transfers = {}

class BankingChatbot:
    def __init__(self):
        self.system_prompt = (
            "Сен банк ассистентисиң. Төмөндө колдонуучунун профили (аты, аккаунттары) берилген — бул маалыматты дайыма эстеп жүр жана статикалык суроолорго (аты, аккаунт түрлөрү) ушул маалыматтан жооп бер. "
            "Баланс, транзакциялар, акча которуу сыяктуу динамикалык маалымат үчүн function calling колдон. "
            "Карта, депозит, насыялар же башка жөнүндө информация же суроого жооп керек болсо function calling колдон."
            "Эгер function_call жооп катары Сырой JSON кайтарса, аны адамча тилде, жыйнактап, пунктирлеп түшүндүр. Сырой JSON кайтарба. Текст кайтар."
            "МААНИЛҮҮ: Жоопторуңда колдонуучунун атын колдон. Мисалы: 'Ооба, {user_name}, балансыңыз 1000 сом', 'Жакшы, {user_name}, акча которуу ийгиликтүү болду' ж.б. "
            "Колдонуучунун атын жоопторуңда жумшак жана досчолуктуу жол менен колдон."
            "МААНИЛҮҮ: user кайсыл тилде жазса, ошол тилде жооп бер."
        )
    
    def build_prompt(self, conversation_history, user_message, user):
        prompt_lines = []
        # System prompt with MCP instruction and user name
        if user and user.name:
            system_prompt = self.system_prompt.format(user_name=user.name)
        else:
            system_prompt = self.system_prompt.format(user_name="колдонуучу")
        prompt_lines.append(system_prompt)
        # Structured static user profile
        if user:
            accounts = ", ".join([f"{a.account_type}" for a in user.accounts])
            user_profile = (
                f"Профиль колдонуучунун:\n"
                f"- Аты: {user.name}\n"
                f"- ID: {user.id}\n"
                f"- Аккаунттар: {accounts if accounts else 'жок'}"
            )
            prompt_lines.append(user_profile)
        # Conversation history
        if conversation_history:
            for msg in conversation_history[-2:]:
                prompt_lines.append(f"User: {msg['message']}")
                prompt_lines.append(f"Assistant: {msg['response']}")
        # Current user message
        prompt_lines.append(f"User: {user_message}")
        return prompt_lines

    async def translate_format_text(self, text: str, target_lang: str = "ky") -> str:
        # Маппинг кодов языков для Gemini
        lang_mapping = {
            'ky': 'kyrgyz',
            'ru': 'russian', 
            'en': 'english'
        }
        
        target_lang_name = lang_mapping.get(target_lang, target_lang)
        prompt = [
            f"translate my meaning to {target_lang_name} and return only 1 translation.",
            "Give the comparison only. No explanations, no introductions, no phrases like 'Below is...' or 'The following...",
            "also format text to easy-read to person:",
            "When formatting lists, dictionaries, or structured data:",
            "- Use bullet points (•) for lists",
            "- Use numbered lists (1., 2., 3.) for steps or rankings", 
            "- Use clear headings with emojis for sections",
            "- Format currency amounts clearly (e.g., '1,000 сом', '500 USD')",
            "- Use tables or structured format for comparisons",
            "- Add spacing between sections for better readability",
            "- Use bold text (**text**) for important information",
            "- Format percentages clearly (e.g., '15% жылдык')",
            f"Return only the formatted text without any additional explanations:\n\n{text}"
        ]
        try:
            config = types.GenerateContentConfig(
                max_output_tokens=2000,
                temperature=0.6,
            )
            print("prompt", prompt)
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=prompt,
                config=config
            )
            print("response", response)
            return response.text.strip()
        except Exception as e:
            print(f"Ошибка перевода: {e}")
            return text


    def get_response(self, user_message: str, conversation_history: list = None, user=None) -> str:
        """
        Get a response from Gemini for the banking chatbot
        Args:
            user_message: The user's message
            conversation_history: List of previous messages for context
            user: User object (for personal banking functions)
        Returns:
            The AI's response in user's language
        """
        try:
            messages = self.build_prompt(conversation_history, user_message, user)
            tools = [{"function_declarations": list(gemini_function_schemas.values())}]
            config = types.GenerateContentConfig(
                max_output_tokens=1000,
                temperature=0.7,
                tools=tools
            )
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=messages,
                config=config
            )
            logging.debug(f"Gemini raw response: {response}")
            
            # Сначала проверяем function calls
            for candidate in response.candidates:
                content = candidate.content
                for part in content.parts:
                    if hasattr(part, 'function_call') and part.function_call:
                        logging.debug(f"Function call part: {part.function_call}")
                        return self.handle_gemini_function_call(user, part.function_call)
            
            # Затем проверяем текстовые ответы
            for candidate in response.candidates:
                content = candidate.content
                for part in content.parts:
                    if hasattr(part, 'text') and part.text:
                        response_text = part.text.strip()
                        
                        # Пытаемся распарсить JSON ответ
                        try:
                            parsed_response = json.loads(response_text)
                            if 'language' in parsed_response and 'text' in parsed_response:
                                return parsed_response['text']
                        except json.JSONDecodeError:
                            # Если не JSON, возвращаем как есть
                            pass
                        
                        return response_text
            
            logging.error(f"No valid response from Gemini: {response}")
            return "Кечиресиз, азыр жооп берүүдө кыйынчылык жаралууда. Кайра аракет кылыңыз же банкка түздөн-түз кайрылыңыз."
        except Exception as e:
            logging.exception(f"Error getting Gemini response: {e}")
            return "Кечиресиз, техникалык ката кетти. Бир аздан кийин кайра аракет кылыңыз же банкка түздөн-түз кайрылыңыз."

    async def call_mcp_tool(self, tool_name: str, **kwargs):
        """
        Call an MCP tool using the standard MCP client
        """
        try:
            # Configure MCP server parameters
            server_params = StdioServerParameters(
                command="python",
                args=["banking_mcp_server.py"],
                env={}
            )
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    # Call the tool
                    result = await session.call_tool(tool_name, arguments=kwargs)
                    return result.content[0].text if result.content else "No result"
        except Exception as e:
            logging.exception(f"Error calling MCP tool {tool_name}: {e}")
            return f"Кечиресиз, {tool_name} функциясы ишке ашкан жок."

    def handle_gemini_function_call(self, user, function_call):
        """
        Handle function_call from Gemini: calls the appropriate MCP tool and returns the result.
        function_call: dict or object with keys 'name' and 'parameters' or 'args'.
        Returns a string response for the user.
        """
        try:
            logging.info(f"Function call received: {function_call}")
            # Try to extract function name robustly
            name = getattr(function_call, 'name', None) or (function_call.get('name') if isinstance(function_call, dict) else None)

            # Try to extract parameters robustly
            params = (
                getattr(function_call, 'parameters', None)
                or getattr(function_call, 'args', None)
                or (function_call.get('parameters') if isinstance(function_call, dict) else None)
                or (function_call.get('args') if isinstance(function_call, dict) else None)
                or {}
            )

            # Convert proto map to dict if needed
            if hasattr(params, 'items'):
                params = dict(params.items())

            logging.debug(f"Function name: {name}, params: {params}")

            # Extract language parameter
            target_language = params.get('language', 'ky')
            logging.info(f"Target language: {target_language}")

            # General tool-call block
            mcp_params = {}

            # Functions requiring user_id
            if name in [
                'get_balance', 'get_transactions', 'transfer_money',
                'get_last_incoming_transaction', 'get_accounts_info',
                'get_incoming_sum_for_period', 'get_outgoing_sum_for_period',
                'get_last_3_transfer_recipients', 'get_largest_transaction'
            ]:
                mcp_params['user_id'] = user.id
                if isinstance(params, dict):
                    for key, value in params.items():
                        if key in ['limit', 'user_id']:
                            mcp_params[key] = int(value)
                        elif key == 'amount':
                            mcp_params[key] = float(value)
                        elif key != 'language':  # Исключаем language из MCP параметров
                            mcp_params[key] = str(value)
                result = asyncio.run(self.call_mcp_tool(name, **mcp_params))
                # Переводим результат на целевой язык
                result = asyncio.run(self.translate_format_text(result, target_language))
                return result  
            elif name in [
                'list_all_card_names', 'get_card_details', 'compare_cards', 'get_card_limits', 'get_card_benefits',
                'get_card_instructions', 'get_card_conditions', 'get_cards_with_features', 'get_card_recommendations',
                'get_cards_by_type', 'get_cards_by_payment_system', 'get_cards_by_fee_range', 'get_cards_by_currency',
                'get_bank_info', 'get_bank_mission', 'get_bank_values', 'get_ownership_info', 'get_branch_network',
                'get_contact_info', 'get_complete_about_us', 'get_about_us_section'
            ]:  
                # Убираем language из параметров для MCP
                mcp_params = {k: v for k, v in params.items() if k != 'language'}
                result = asyncio.run(self.call_mcp_tool(name, **mcp_params))

                # Переводим результат на целевой язык
                result = asyncio.run(self.translate_format_text(result, target_language))
                return result
            else:
                logging.error(f"Unknown function call name: {name}")
                error_msg = "Түшүнүксүз функциялык чакыруу."
                if target_language != 'ky':
                    error_msg = asyncio.run(self.translate_format_text(error_msg, target_language))
                return error_msg
        except Exception as e:
            logging.exception(f"Exception in handle_gemini_function_call: {e}, function_call: {function_call}")
            error_msg = "Кечиресиз, функциялык чакыруу ишке ашкан жок. Кайра аракет кылыңыз же банкка кайрылыңыз."
            # Пытаемся получить язык из параметров
            try:
                params = getattr(function_call, 'parameters', None) or function_call.get('parameters', {})
                if hasattr(params, 'items'):
                    params = dict(params.items())
                target_language = params.get('language', 'ky')
                if target_language != 'ky':
                    error_msg = asyncio.run(self.translate_format_text(error_msg, target_language))
            except:
                pass
            return error_msg


# Create a global instance
banking_chatbot = BankingChatbot()
