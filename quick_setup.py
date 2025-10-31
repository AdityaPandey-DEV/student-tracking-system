#!/usr/bin/env python3
"""
Quick Setup Script for Student Tracking System
This script helps you set up OpenAI API key step by step
"""

import os
import webbrowser
from time import sleep

def print_header():
    print("🚀 Student Tracking System - Quick Setup")
    print("=" * 60)
    print("This script will help you set up your OpenAI API key step by step")
    print()

def setup_openai_key():
    print("🔑 OpenAI API Key Setup")
    print("-" * 30)
    print()
    
    choice = input("Do you already have an OpenAI API key? (y/n): ").lower().strip()
    
    if choice != 'y':
        print("\n📝 Let's get you an OpenAI API key with $5 free credits!")
        print("\nSteps:")
        print("1. I'll open the OpenAI sign-up page")
        print("2. Create account and verify your phone number")
        print("3. Go to API Keys section")
        print("4. Create a new secret key")
        print("5. Copy the key and come back here")
        
        proceed = input("\nPress Enter to open OpenAI platform...")
        webbrowser.open("https://platform.openai.com/signup")
        
        print("\nAfter signing up:")
        print("1. Go to: https://platform.openai.com/api-keys")
        print("2. Click 'Create new secret key'")
        print("3. Name it: 'Enhanced-Timetable-System'")
        print("4. Copy the key (starts with 'sk-...')")
        
        proceed = input("\nPress Enter when you have your API key...")
    
    print("\n🔐 Enter your OpenAI API key:")
    print("(It should start with 'sk-' and be about 48-51 characters long)")
    
    while True:
        api_key = input("API Key: ").strip()
        
        if not api_key:
            print("❌ Please enter your API key")
            continue
            
        if not api_key.startswith('sk-'):
            print("❌ API key should start with 'sk-'")
            continue
            
        if len(api_key) < 40:
            print("❌ API key seems too short")
            continue
            
        break
    
    return api_key

def update_env_file(api_key):
    """Update .env file with the API key"""
    print("\n💾 Updating .env file...")
    
    try:
        with open('.env', 'r') as f:
            content = f.read()
        
        # Replace the OpenAI API key line
        lines = content.split('\n')
        updated_lines = []
        
        for line in lines:
            if line.startswith('OPENAI_API_KEY='):
                updated_lines.append(f'OPENAI_API_KEY={api_key}')
            else:
                updated_lines.append(line)
        
        with open('.env', 'w') as f:
            f.write('\n'.join(updated_lines))
        
        print("✅ .env file updated successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error updating .env file: {e}")
        return False

def test_setup():
    """Test the setup"""
    print("\n🧪 Testing your setup...")
    print("Running test_openai_setup.py...")
    print("-" * 40)
    
    os.system("python test_openai_setup.py")

def show_final_instructions():
    """Show final instructions"""
    print("\n🎉 Setup Complete!")
    print("-" * 30)
    print("Your Student Tracking System is now ready!")
    print()
    print("🚀 Next Steps:")
    print("1. Start the server: python manage.py runserver")
    print("2. Open: http://127.0.0.1:8000/")
    print("3. Register as a student or admin")
    print("4. Try the AI chat feature!")
    print()
    print("📚 Need help?")
    print("- Check OPENAI_SETUP_GUIDE.md for detailed info")
    print("- Run 'python test_openai_setup.py' to test anytime")
    print()
    print("💡 Pro tip: Your $5 free credits are enough for thousands of AI queries!")

def main():
    print_header()
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("Please make sure you're in the project directory.")
        return
    
    # Setup OpenAI key
    api_key = setup_openai_key()
    
    # Update .env file
    if update_env_file(api_key):
        # Test the setup
        test_setup()
        
        # Show final instructions
        show_final_instructions()
    else:
        print("❌ Setup failed. Please try again or set up manually.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Please try manual setup using OPENAI_SETUP_GUIDE.md")
