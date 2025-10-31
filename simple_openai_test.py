#!/usr/bin/env python3
"""
Simple OpenAI API test
"""

import os
from dotenv import load_dotenv

load_dotenv()

def test_openai_api():
    api_key = os.getenv('OPENAI_API_KEY')
    
    if not api_key:
        print("❌ No API key found in .env")
        return False
    
    print(f"✅ API key loaded: {api_key[:15]}...")
    
    try:
        from openai import OpenAI
        
        # Initialize client
        client = OpenAI(api_key=api_key)
        
        print("✅ OpenAI client initialized")
        
        # Test API call
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Hello! Just say 'API working!'"}
            ],
            max_tokens=10,
            temperature=0
        )
        
        result = response.choices[0].message.content
        print(f"✅ API Response: {result}")
        print(f"💰 Tokens used: {response.usage.total_tokens}")
        print(f"💵 Estimated cost: ${response.usage.total_tokens * 0.002 / 1000:.6f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Testing OpenAI API...")
    print("=" * 40)
    
    success = test_openai_api()
    
    if success:
        print("\n🎉 OpenAI API is working perfectly!")
        print("Your Student Tracking System is ready for AI features!")
    else:
        print("\n❌ API test failed. Check your API key.")
