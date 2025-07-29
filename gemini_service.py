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
            "Баланс, транзакциялар, акча которуу сыяктуу динамикалык маалымат үчүн function calling колдон. Жоопту кыргызча бер. "
            "Карта, депозит, насыялар же башка жөнүндө информация же суроого жооп керек болсо function calling колдон. Жоопту кыргызча бер."
            "Эгер function_call жооп катары Сырой JSON кайтарса, аны адамча тилде, жыйнактап, пунктирлеп түшүндүр. Сырой JSON кайтарба. Текст кайтар."
            "МААНИЛҮҮ: Жоопторуңда колдонуучунун атын колдон. Мисалы: 'Ооба, {user_name}, балансыңыз 1000 сом', 'Жакшы, {user_name}, акча которуу ийгиликтүү болду' ж.б. "
            "Колдонуучунун атын жоопторуңда жумшак жана досчолуктуу жол менен колдон."
            "ДАЙЫМА ТЕКСТ МЕНЕН ЖООП БЕР, JSON, LIST, DICT ЖАНА БАШКА ЖӨНӨТСӨ БОЛБОЙТ"
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

    async def translate_text(self, text: str, target_lang: str = "ky") -> str:
        prompt = [f"translate my meaning to {target_lang} and return only translation, also format text to easy-read to person:\n\n{text}"]
        try:
            config = types.GenerateContentConfig(
                max_output_tokens=2000,
                temperature=0.6,
            )
            print("promt", prompt)
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
            The AI's response (Kyrgyz)
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
            for candidate in response.candidates:
                content = candidate.content
                for part in content.parts:
                    if hasattr(part, 'function_call') and part.function_call:
                        logging.debug(f"Function call part: {part.function_call}")
                        return self.handle_gemini_function_call(user, part.function_call)
            for candidate in response.candidates:
                content = candidate.content
                for part in content.parts:
                    if hasattr(part, 'text') and part.text:
                        return part.text.strip()
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
            print("до server_params -----------------------------------------")
            async with stdio_client(server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    await session.initialize()
                    print("до initialize -----------------------------------------")
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
                        else:
                            mcp_params[key] = str(value)
                result = asyncio.run(self.call_mcp_tool(name, **mcp_params))
                return result  
            elif name in [
                'list_all_card_names', 'get_card_details', 'compare_cards', 'get_card_limits', 'get_card_benefits'
            ]:  
                result = asyncio.run(self.call_mcp_tool(name, **params))
                print("result", result)
                result = asyncio.run(self.translate_text(result, "kyrgyz"))
                print("result", result)
                return result
            else:
                logging.error(f"Unknown function call name: {name}")
                return "Түшүнүксүз функциялык чакыруу."
        except Exception as e:
            logging.exception(f"Exception in handle_gemini_function_call: {e}, function_call: {function_call}")
            return "Кечиресиз, функциялык чакыруу ишке ашкан жок. Кайра аракет кылыңыз же банкка кайрылыңыз."


# Create a global instance
banking_chatbot = BankingChatbot()
