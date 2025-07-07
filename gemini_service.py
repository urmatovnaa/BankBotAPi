import os
import logging
from google import genai
from google.genai import types

# Initialize Gemini client
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY", "default_key"))

class BankingChatbot:
    def __init__(self):
        self.system_prompt = """
        You are a helpful and professional banking assistant chatbot. Your role is to:
        
        1. Provide general information about banking services (checking accounts, savings accounts, loans, credit cards, etc.)
        2. Help customers understand banking processes and procedures
        3. Assist with common banking questions and concerns
        4. Provide financial literacy information
        5. Guide customers to appropriate resources or suggest they contact their bank directly for account-specific matters
        
        IMPORTANT GUIDELINES:
        - Never ask for or process sensitive information like account numbers, SSNs, passwords, or PINs
        - Always remind users to contact their bank directly for account-specific issues
        - Provide accurate, helpful information about general banking topics
        - Be professional, courteous, and empathetic
        - If you're unsure about something, admit it and suggest they contact their bank
        - Do not provide specific financial advice - only general information
        - Keep responses concise but informative
        
        Remember: You are here to help with general banking questions and provide information, not to access or modify any accounts.
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
