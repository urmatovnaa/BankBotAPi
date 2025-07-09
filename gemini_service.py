import os
import logging
import re
import google.generativeai as genai
from app import db
from sqlalchemy import func
from bank_functions import get_balance, get_transactions, transfer_money, get_last_incoming_transaction
from gemini_function_schemas import gemini_function_schemas

# Initialize Gemini model with function calling tools
model = genai.GenerativeModel(
    "gemini-2.5-flash",
    tools=[{"function_declarations": list(gemini_function_schemas.values())}]
)

# In-memory store for pending transfers: {user_id: {"to_name": ..., "amount": ...}}
pending_transfers = {}

class BankingChatbot:
    def __init__(self):
        self.system_prompt = """
        Сиз жардамчы жана кесиптүү банк кызматчысысыз. Сиздин ролуңуз:
        
        1. Банк кызматтары тууралуу жалпы маалымат берүү (текущий эсептер, жинак эсептери, кредиттер, кредиттик карталар ж.б.)
        2. Кардарларга банк процедураларын жана процесстерин түшүнүүгө жардам берүү
        3. Жалпы банк суроолору жана тынчсызданууларында жардам берүү
        4. Каржы сабаттуулугу боюнча маалымат берүү
        5. Кардарларды тиешелүү ресурстарга багыттоо же эсеп менен байланышкан маселелер үчүн банкка түздөн-түз кайрылууну сунуштоо
        6. Жеке суроолорго жооп берүү: колдонуучунун банк эсебиндеги баланс, эсептердин тизмеси, акыркы транзакциялар, кимге жана канча акча которгон, жана акча которуу ассистенти катары иштөө (мисалы, "100 сомду Бакытка котор" ж.б.).
        
        МААНИЛҮҮ КӨРСӨТМӨЛӨР:
        - Эч качан эсеп номурлары, жеке номурлар, сыр сөздөр же PIN-коддор сыяктуу купуя маалыматты сурабаңыз же иштетпеңиз
        - Эсеп менен байланышкан маселелер үчүн банкка түздөн-түз кайрылууну дайыма эскертиңиз
        - Жалпы жана жеке банк темалары боюнча так, пайдалуу маалымат бериңиз
        - Кесиптүү, сылык жана боордоштук менен мамиле кылыңыз
        - Эгер бир нерсеге ишенбесеңиз, муну мойнуна алыңыз жана банкка кайрылууну сунуштаңыз
        - Өзгөчө каржы кеңештерин бербеңиз - жалпы маалымат гана
        - Жоопторду кыска, бирок маалымдуу кылыңыз
        
        Эсиңизде болсун: Сиз жалпы жана жеке банк суроолору боюнча жардам берүү жана маалымат берүү үчүн бул жердесиз, эсептерди көрүү же өзгөртүү үчүн эмес.
        
        МААНИЛҮҮ: Бардык жоопторуңузду кыргыз тилинде жазыңыз.
        """
    
    def get_personal_response(self, user, user_message):
        # Теперь персональные вопросы обрабатываются только через function calling Gemini
        return None

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
            # Build the conversation context
            conversation_context = ""
            if conversation_history:
                for msg in conversation_history[-5:]:  # Keep last 5 messages for context
                    conversation_context += f"User: {msg['message']}\nAssistant: {msg['response']}\n\n"
            # Construct the full prompt
            full_prompt = f"{self.system_prompt}\n\n"
            if conversation_context:
                full_prompt += f"Previous conversation:\n{conversation_context}"
            full_prompt += f"Current user message: {user_message}\n\nPlease provide a helpful response:"

            response = model.generate_content(
                [full_prompt],
                generation_config={
                    "max_output_tokens": 1000,
                    "temperature": 0.7,
                }
            )

            # Log the full Gemini response for debugging
            logging.debug(f"Gemini raw response: {response}")

            # Safe handling of function_call and text
            # Gemini SDK may return function_call in different places
            # Check candidates, parts, text
            if hasattr(response, 'candidates'):
                for cand in response.candidates:
                    if hasattr(cand, 'content') and hasattr(cand.content, 'parts'):
                        for part in cand.content.parts:
                            if hasattr(part, 'function_call') and part.function_call:
                                logging.debug(f"Function call part: {part.function_call}")
                                return self.handle_gemini_function_call(user, part.function_call)
                            if hasattr(part, 'text') and part.text:
                                return part.text.strip()
            # Fallback: try to find any text part in candidates
            if hasattr(response, 'candidates'):
                for cand in response.candidates:
                    if hasattr(cand, 'content') and hasattr(cand.content, 'parts'):
                        for part in cand.content.parts:
                            if hasattr(part, 'text') and part.text:
                                return part.text.strip()
            # If no text part found, return a default error message
            logging.error(f"No valid response from Gemini: {response}")
            return "Кечиресиз, азыр жооп берүүдө кыйынчылык жаралууда. Кайра аракет кылыңыз же банкка түздөн-түз кайрылыңыз."
        except Exception as e:
            logging.exception(f"Error getting Gemini response: {e}")
            return "Кечиресиз, техникалык ката кетти. Бир аздан кийин кайра аракет кылыңыз же банкка түздөн-түз кайрылыңыз."

    def handle_gemini_function_call(self, user, function_call):
        """
        Handle function_call from Gemini: calls the appropriate function and returns the result.
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
            if name == 'get_balance':
                _, msg = get_balance(user)
                return msg
            elif name == 'get_transactions':
                limit = params.get('limit', 5) if isinstance(params, dict) else 5
                txs, err = get_transactions(user, limit=limit)
                if err:
                    return err
                resp = "Акыркы транзакциялар:\n"
                for t in txs:
                    resp += f"- {t['type']}: {t['amount']:.2f} сом {t['direction']}, {t['timestamp']}\n"
                return resp
            elif name == 'transfer_money':
                user_id = user.id
                to_name = params.get('to_name') if isinstance(params, dict) else None
                amount = params.get('amount') if isinstance(params, dict) else None

                # Check if we have a pending transfer for this user
                pending = pending_transfers.get(user_id, {})

                # Merge new info with pending info
                if to_name is None and 'to_name' in pending:
                    to_name = pending['to_name']
                if amount is None and 'amount' in pending:
                    amount = pending['amount']
                print(to_name, amount, "if there0000")
                # If still missing info, ask for it and store what we have
                if not to_name and not amount:
                    pending_transfers[user_id] = {}
                    return "Кимге жана канча сумма которууну каалайсыз?"
                elif not to_name:
                    pending_transfers[user_id] = {'amount': amount}
                    return "Кимге которууну каалайсыз?"
                elif amount is None:
                    pending_transfers[user_id] = {'to_name': to_name}
                    return "Канча сумма которууну каалайсыз?"

                # We have both, perform transfer
                print(user, to_name, amount, "5555555555")
                ok, msg = transfer_money(user, to_name, amount)
                print("corrrrrect")
                # Clear pending state
                if user_id in pending_transfers:
                    del pending_transfers[user_id]
                return msg
            elif name == 'get_last_incoming_transaction':
                _, msg = get_last_incoming_transaction(user)
                return msg
            else:
                logging.error(f"Unknown function call name: {name}")
                return "Түшүнүксүз функциялык чакыруу."
        except Exception as e:
            logging.exception(f"Exception in handle_gemini_function_call: {e}, function_call: {function_call}")
            return "Кечиресиз, функциялык чакыруу ишке ашкан жок. Кайра аракет кылыңыз же банкка кайрылыңыз."

# Create a global instance
banking_chatbot = BankingChatbot()
