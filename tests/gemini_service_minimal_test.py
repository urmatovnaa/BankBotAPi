import google.generativeai as genai
import os
from dotenv import load_dotenv
load_dotenv()
import logging
from gemini_function_schemas import gemini_function_schemas

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY environment variable not set!")

genai.configure(api_key=api_key)

schemas = list(gemini_function_schemas.values())

model = genai.GenerativeModel(
    "gemini-2.0-flash",
    tools=[{"function_declarations": schemas}]
)

class MinimalBankingChatbot:
    def __init__(self):
        self.system_prompt = (
            "Сен банк ассистентисиң. Эгер колдонуучу сураса, дайыма function calling колдон. "
            "Мисалы: баланс, транзакциялар, акча которуу."
        )

    def get_response(self, user_message: str) -> str:
        messages = [
            {"role": "user", "parts": [self.system_prompt + '\n' + user_message]}
        ]
        logging.debug(f"Prompt sent to Gemini: {messages}")
        response = model.generate_content(
            messages,
            generation_config={
                "max_output_tokens": 100,
                "temperature": 0.2,
            }
        )
        logging.debug(f"Gemini raw response: {response}")
        # Prioritize function call
        if hasattr(response, 'candidates'):
            for cand in response.candidates:
                if hasattr(cand, 'content') and hasattr(cand.content, 'parts'):
                    for part in cand.content.parts:
                        if hasattr(part, 'function_call') and part.function_call:
                            print("Function call part:", part.function_call)
                            return f"Function call: {part.function_call}"
        # Fallback to text
        if hasattr(response, 'candidates'):
            for cand in response.candidates:
                if hasattr(cand, 'content') and hasattr(cand.content, 'parts'):
                    for part in cand.content.parts:
                        if hasattr(part, 'text') and part.text:
                            print("Text part:", part.text)
                            return part.text.strip()
        print("No valid response from Gemini.")
        return "No valid response from Gemini."

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    bot = MinimalBankingChatbot()
    # Test in English
    print("ENGLISH TESTS:")
    print(bot.get_response("Show my balance"))
    print(bot.get_response("Show my last 3 transactions"))
    print(bot.get_response("Send 100 som to Bakyt"))
    # Test in Kyrgyz
    print("KYRGYZ TESTS:")
    print(bot.get_response("Менин балансымды көрсөт"))
    print(bot.get_response("Акыркы 3 транзакциямды көрсөт"))
    print(bot.get_response("100 сомду Бакытка котор")) 