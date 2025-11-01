#!/usr/bin/env python3
"""
Setup free AI using Hugging Face
No credit card or payment required!
"""

import os
import webbrowser
from dotenv import load_dotenv
import requests

load_dotenv()

def setup_huggingface():
    print("🤗 Setting up FREE Hugging Face AI")
    print("=" * 50)
    print("Hugging Face provides completely FREE AI APIs!")
    print()
    
    # Check if token already exists
    hf_token = os.getenv('HUGGINGFACE_API_KEY')
    
    if hf_token and hf_token.startswith('hf_'):
        print("✅ Hugging Face token found!")
        return test_huggingface(hf_token)
    
    print("📝 Let's get your FREE Hugging Face token:")
    print("1. I'll open the Hugging Face website")
    print("2. Sign up (completely free)")
    print("3. Go to Settings → Access Tokens")
    print("4. Create a new token")
    print("5. Copy the token")
    
    proceed = input("\nPress Enter to open Hugging Face...")
    webbrowser.open("https://huggingface.co/join")
    
    print("\nAfter signing up:")
    print("1. Go to: https://huggingface.co/settings/tokens")
    print("2. Click 'New token'")
    print("3. Name it: 'Enhanced-Timetable-AI'")
    print("4. Select 'Read' permissions")
    print("5. Copy the token (starts with 'hf_')")
    
    proceed = input("\nPress Enter when you have your token...")
    
    while True:
        token = input("Enter your Hugging Face token: ").strip()
        
        if not token:
            print("❌ Please enter your token")
            continue
        
        if not token.startswith('hf_'):
            print("❌ Token should start with 'hf_'")
            continue
            
        if test_huggingface(token):
            update_env_with_hf_token(token)
            return True
        else:
            print("❌ Token doesn't work. Please try again.")

def test_huggingface(token):
    """Test Hugging Face token"""
    try:
        print(f"🧪 Testing token: {token[:8]}...")
        
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get("https://huggingface.co/api/whoami", headers=headers)
        
        if response.status_code == 200:
            user_info = response.json()
            print(f"✅ Token works! User: {user_info.get('name', 'Unknown')}")
            return True
        else:
            print(f"❌ Token test failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing token: {e}")
        return False

def update_env_with_hf_token(token):
    """Add Hugging Face token to .env"""
    try:
        with open('.env', 'r') as f:
            content = f.read()
        
        # Add or update HuggingFace token
        if 'HUGGINGFACE_API_KEY=' in content:
            # Replace existing
            lines = content.split('\n')
            updated_lines = []
            for line in lines:
                if line.startswith('# HUGGINGFACE_API_KEY=') or line.startswith('HUGGINGFACE_API_KEY='):
                    updated_lines.append(f'HUGGINGFACE_API_KEY={token}')
                else:
                    updated_lines.append(line)
            content = '\n'.join(updated_lines)
        else:
            # Add new
            content += f'\nHUGGINGFACE_API_KEY={token}\n'
        
        with open('.env', 'w') as f:
            f.write(content)
        
        print("✅ .env file updated with Hugging Face token!")
        return True
    except Exception as e:
        print(f"❌ Error updating .env: {e}")
        return False

def test_free_ai():
    """Test the free AI setup"""
    print("\n🚀 Testing FREE AI...")
    
    # Reload environment
    load_dotenv()
    hf_token = os.getenv('HUGGINGFACE_API_KEY')
    
    if not hf_token:
        print("❌ No Hugging Face token found")
        return False
    
    try:
        # Test a simple AI request
        headers = {"Authorization": f"Bearer {hf_token}"}
        
        # Use a free conversational model
        payload = {
            "inputs": "Hello! How are you today?",
            "parameters": {
                "max_length": 50,
                "temperature": 0.7
            }
        }
        
        response = requests.post(
            "https://api-inference.huggingface.co/models/microsoft/DialoGPT-medium",
            headers=headers,
            json=payload
        )
        
        if response.status_code == 200:
            result = response.json()
            if isinstance(result, list) and len(result) > 0:
                ai_response = result[0].get('generated_text', 'AI response received!')
                print(f"✅ AI Response: {ai_response}")
                print("🎉 FREE AI is working perfectly!")
                return True
            else:
                print("✅ AI API working (model loading...)")
                print("🎉 FREE AI setup complete!")
                return True
        else:
            print(f"❌ AI test failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing AI: {e}")
        return False

def show_usage_instructions():
    """Show how to use the free AI in the project"""
    print("\n📚 How to use FREE AI in your project:")
    print("-" * 50)
    print("Your Student Tracking System will now use:")
    print("• Hugging Face instead of OpenAI")
    print("• Completely FREE (no credit card needed)")
    print("• Works great for chatbots and recommendations")
    print()
    print("🚀 Next steps:")
    print("1. Run: python manage.py runserver")
    print("2. Go to: http://127.0.0.1:8000/")
    print("3. Register and try the AI chat feature!")
    print()
    print("💡 The AI features will work the same way,")
    print("   but using free Hugging Face models instead!")

def main():
    print("🆓 Student Tracking System - FREE AI Setup")
    print("=" * 60)
    print("Your OpenAI credits are exhausted, but no worries!")
    print("Let's set up completely FREE AI using Hugging Face!")
    print()
    
    if setup_huggingface():
        if test_free_ai():
            show_usage_instructions()
            print("\n🎉 Setup complete! Enjoy your FREE AI-powered system!")
        else:
            print("❌ Setup completed but testing failed. Try again later.")
    else:
        print("❌ Setup failed. You can try again or add payment to OpenAI.")

if __name__ == "__main__":
    main()
