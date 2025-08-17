#!/usr/bin/env python3
"""
Simple script to update Gmail App Password in .env file
"""

import re
from pathlib import Path

def update_gmail_password():
    print("🔐 Update Gmail App Password")
    print("=" * 40)
    print("Your email: adityapandey.dev.in@gmail.com")
    print()
    print("📋 Paste your 16-character Gmail App Password here:")
    print("(Format: abcd efgh ijkl mnop - spaces will be removed)")
    
    while True:
        app_password = input("\n📝 App Password: ").strip().replace(" ", "").replace("-", "")
        
        if len(app_password) == 16 and re.match(r'^[a-zA-Z0-9]+$', app_password):
            break
        else:
            print("❌ Invalid format!")
            print("App Password should be 16 characters (letters and numbers only)")
            print("Example: abcdefghijklmnop")
    
    # Update .env file
    env_file = Path('.env')
    if not env_file.exists():
        print("❌ .env file not found!")
        return False
    
    # Read and update
    with open(env_file, 'r') as f:
        content = f.read()
    
    # Replace password
    updated_content = re.sub(
        r'EMAIL_HOST_PASSWORD=.*',
        f'EMAIL_HOST_PASSWORD={app_password}',
        content
    )
    
    # Write back
    with open(env_file, 'w') as f:
        f.write(updated_content)
    
    print(f"✅ Password updated successfully!")
    print()
    
    # Test the configuration
    print("🧪 Testing email configuration...")
    try:
        import os
        import django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'enhanced_timetable_system.settings')
        django.setup()
        
        from django.core.mail import send_mail
        from django.conf import settings
        
        result = send_mail(
            subject='Enhanced Timetable System - Test Email ✅',
            message='Your Gmail configuration is working! You can now send real OTP emails.',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.EMAIL_HOST_USER],
            fail_silently=False
        )
        
        if result:
            print("✅ Test email sent successfully!")
            print(f"📬 Check your inbox: {settings.EMAIL_HOST_USER}")
            print("\n🎉 Email setup complete! You can now:")
            print("1. Start server: python manage.py runserver")
            print("2. Test registration at: http://127.0.0.1:8000")
            print("3. Real OTP emails will be sent to users!")
            return True
        else:
            print("❌ Test email failed")
            return False
            
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Test failed: {error_msg}")
        
        if "535" in error_msg:
            print("\n🔧 Authentication Error:")
            print("1. Make sure 2-Factor Authentication is enabled")
            print("2. Double-check your App Password is correct")
            print("3. Try generating a new App Password")
        else:
            print("\n🔧 Other error - check your internet connection")
        
        return False

if __name__ == "__main__":
    print("📧 Gmail Setup for Enhanced Timetable System")
    print("Follow these steps:")
    print("1. Go to: https://myaccount.google.com/security")
    print("2. Enable 2-Factor Authentication (if not done)")
    print("3. Go to: https://myaccount.google.com/apppasswords")
    print("4. Generate App Password for 'Mail' app")
    print("5. Come back and paste it here")
    print()
    
    choice = input("Ready to enter App Password? (y/n): ").lower()
    if choice == 'y':
        update_gmail_password()
    else:
        print("Run this script again when you have your App Password ready!")
