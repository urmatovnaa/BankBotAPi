#!/usr/bin/env python3
"""
Test script to verify the updated gemini_service with MCP integration
"""

import os
from dotenv import load_dotenv
load_dotenv()

from app import app
from models import User
from gemini_service import banking_chatbot

def test_gemini_mcp_integration():
    """Test the Gemini service with MCP integration"""
    print("Testing Gemini service with MCP integration...")
    
    with app.app_context():
        # Get a test user
        user = User.query.get(1)
        if not user:
            print("No user found in database. Please ensure you have test data.")
            return
        
        print(f"Testing with user: {user.name}")
        
        # Test queries that should trigger MCP function calls
        test_queries = [
            "Менин балансымды көрсөт",
            "Акыркы 3 транзакциямды көрсөт",
            "Акыркы кирген транзакция тууралуу маалымат бер",
        ]
        
        for query in test_queries:
            print(f"\n--- Testing query: {query} ---")
            try:
                response = banking_chatbot.get_response(query, user=user)
                print(f"Response: {response}")
            except Exception as e:
                print(f"Error: {e}")
                import traceback
                traceback.print_exc()

if __name__ == "__main__":
    test_gemini_mcp_integration() 