#!/usr/bin/env python3
"""
Test script to verify personalized responses with user names
"""

import os
from dotenv import load_dotenv
load_dotenv()

from app import app
from models import User
from gemini_service import banking_chatbot

def test_personalized_responses():
    """Test the personalized responses with user names"""
    print("Testing personalized responses with user names...")
    
    with app.app_context():
        # Get a test user
        user = User.query.get(1)
        if not user:
            print("No user found in database. Please ensure you have test data.")
            return
        
        print(f"Testing with user: {user.name}")
        
        # Test queries that should trigger personalized responses
        test_queries = [
            "Менин балансымды көрсөт",
            "Акыркы транзакцияларымды көрсөт",
            "Канча акча бар?",
            "Акыркы кирген транзакция тууралуу маалымат бер",
        ]
        
        for query in test_queries:
            print(f"\n--- Testing query: {query} ---")
            try:
                response = banking_chatbot.get_response(query, user=user)
                print(f"Response: {response}")
                
                # Check if response contains user name
                if user.name and user.name.lower() in response.lower():
                    print("✅ Response contains user name!")
                else:
                    print("❌ Response does not contain user name")
                    
            except Exception as e:
                print(f"Error: {e}")
                import traceback
                traceback.print_exc()

if __name__ == "__main__":
    test_personalized_responses() 