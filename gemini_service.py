import os
import logging
from google import genai
from google.genai import types

# Initialize Gemini client
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY", "default_key"))

class BankingChatbot:
    def __init__(self):
        self.system_prompt = """
        Сиз жардамчы жана кесиптүү банк кызматчысысыз. Сиздин ролуңуз:
        
        1. Банк кызматтары тууралуу жалпы маалымат берүү (текущий эсептер, жинак эсептери, кредиттер, кредиттик карталар ж.б.)
        2. Кардарларга банк процедураларын жана процесстерин түшүнүүгө жардам берүү
        3. Жалпы банк суроолору жана тынчсызданууларында жардам берүү
        4. Каржы сабаттуулугу боюнча маалымат берүү
        5. Кардарларды тиешелүү ресурстарга багыттоо же эсеп менен байланышкан маселелер үчүн банкка түздөн-түз кайрылууну сунуштоо
        
        МААНИЛҮҮ КӨРСӨТМӨЛӨР:
        - Эч качан эсеп номурлары, жеке номурлар, сыр сөздөр же PIN-коддор сыяктуу купуя маалыматты сурабаңыз же иштетпеңиз
        - Эсеп менен байланышкан маселелер үчүн банкка түздөн-түз кайрылууну дайыма эскертиңиз
        - Жалпы банк темалары боюнча так, пайдалуу маалымат бериңиз
        - Кесиптүү, сылык жана боордоштук менен мамиле кылыңыз
        - Эгер бир нерсеге ишенбесеңиз, муну мойнуна алыңыз жана банкка кайрылууну сунуштаңыз
        - Өзгөчө каржы кеңештерин бербеңиз - жалпы маалымат гана
        - Жоопторду кыска, бирок маалымдуу кылыңыз
        
        Эсиңизде болсун: Сиз жалпы банк суроолору боюнча жардам берүү жана маалымат берүү үчүн бул жердесиз, эсептерди көрүү же өзгөртүү үчүн эмес.
        
        МААНИЛҮҮ: Бардык жоопторуңузду кыргыз тилинде жазыңыз.
        """
    
    def get_response(self, user_message: str, conversation_history: list = None) -> str:
        """
        Get a response from Gemini for the banking chatbot
        
        Args:
            user_message: The user's message
            conversation_history: List of previous messages for context
            
        Returns:
            The AI's response
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
            
            # Generate response using Gemini
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    types.Content(role="user", parts=[types.Part(text=full_prompt)])
                ],
                config=types.GenerateContentConfig(
                    max_output_tokens=1000,
                    temperature=0.7,
                )
            )
            
            if response.text:
                return response.text.strip()
            else:
                return "I apologize, but I'm having trouble responding right now. Please try again or contact your bank directly for assistance."
                
        except Exception as e:
            logging.error(f"Error getting Gemini response: {e}")
            return "I apologize, but I'm experiencing technical difficulties. Please try again in a moment or contact your bank directly for assistance."

# Create a global instance
banking_chatbot = BankingChatbot()
