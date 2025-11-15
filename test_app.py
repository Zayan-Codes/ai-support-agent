#!/usr/bin/env python3
"""
Test Script for AI Support Agent
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_api_health():
    """Test if API is running"""
    try:
        response = requests.get(f"{BASE_URL}/")
        print("✅ API Health Check:", response.json())
        return True
    except Exception as e:
        print("❌ API is not running:", e)
        return False

def test_chat_endpoint():
    """Test chat functionality with sample messages"""
    test_messages = [
        "How to reset my password?",
        "I have payment issue",
        "Can't login to my account",
        "Where is my order?"
    ]
    
    for message in test_messages:
        payload = {
            "message": message,
            "user_id": "test_user_001"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/chat", json=payload)
            data = response.json()
            print(f"✅ Chat Test '{message}': {data['response'][:50]}...")
        except Exception as e:
            print(f"❌ Chat Test Failed: {e}")

def main():
    print("🚀 Testing AI Support Agent Application...")
    print("=" * 50)
    
    if test_api_health():
        print("\n🧪 Testing Chat Endpoints...")
        test_chat_endpoint()
        print("\n🎉 All tests completed successfully!")
        print("\n📋 Next Steps:")
        print("1. Start Backend: cd backend && uvicorn main:app --reload")
        print("2. Start Frontend: cd frontend && npm run dev")
        print("3. Open: http://localhost:3000")
    else:
        print("\n💥 Please start the backend server first!")
        print("Run: cd backend && uvicorn main:app --reload")

if __name__ == "__main__":
    main()
