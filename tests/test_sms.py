#!/usr/bin/env python3
"""
Test script for Twilio SMS functionality
Run this script to test SMS sending before using in Django app
"""

import os
import django
from decouple import config

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'enhanced_timetable_system.settings')
django.setup()

def test_twilio_sms():
    """Test Twilio SMS sending functionality"""
    try:
        from twilio.rest import Client
        
        # Get Twilio credentials from environment
        account_sid = config('TWILIO_ACCOUNT_SID', default='')
        auth_token = config('TWILIO_AUTH_TOKEN', default='')
        twilio_phone = config('TWILIO_PHONE_NUMBER', default='')
        
        print("🔍 Testing Twilio SMS Configuration...")
        print(f"Account SID: {account_sid[:10]}..." if account_sid else "Account SID: NOT SET")
        print(f"Auth Token: {'SET' if auth_token else 'NOT SET'}")
        print(f"Phone Number: {twilio_phone}")
        
        if not all([account_sid, auth_token, twilio_phone]):
            print("\n❌ Twilio credentials not configured!")
            print("Please add your Twilio credentials to .env file:")
            print("TWILIO_ACCOUNT_SID=your-account-sid")
            print("TWILIO_AUTH_TOKEN=your-auth-token") 
            print("TWILIO_PHONE_NUMBER=+1234567890")
            return False
        
        # Test phone number for SMS (replace with your phone number)
        test_phone = input("\n📱 Enter your phone number to test (with country code, e.g., +919876543210): ").strip()
        
        if not test_phone.startswith('+'):
            test_phone = '+' + test_phone
        
        print(f"\n📤 Sending test SMS to {test_phone}...")
        
        # Initialize Twilio client
        client = Client(account_sid, auth_token)
        
        # Send test SMS
        message = client.messages.create(
            body="🎉 Test SMS from your Timetable System! SMS functionality is working correctly.",
            from_=twilio_phone,
            to=test_phone
        )
        
        print(f"✅ SMS sent successfully!")
        print(f"Message SID: {message.sid}")
        print(f"Status: {message.status}")
        print("Check your phone for the SMS message.")
        
        return True
        
    except ImportError:
        print("❌ Twilio library not installed. Run: pip install twilio")
        return False
    except Exception as e:
        print(f"❌ SMS sending failed: {str(e)}")
        print("\nCommon issues:")
        print("1. Invalid phone number format (should include country code)")
        print("2. Twilio trial account restrictions (verify phone numbers)")
        print("3. Insufficient account balance")
        print("4. Invalid credentials")
        return False

def test_django_sms():
    """Test Django SMS utility function"""
    try:
        from utils.notifications import send_sms_notification
        
        test_phone = input("\n📱 Enter your phone number for Django SMS test: ").strip()
        if not test_phone.startswith('+'):
            test_phone = '+' + test_phone
            
        print(f"\n📤 Testing Django SMS utility to {test_phone}...")
        
        success = send_sms_notification(
            phone_number=test_phone,
            message="🚀 Django SMS utility test successful!"
        )
        
        if success:
            print("✅ Django SMS utility working!")
        else:
            print("❌ Django SMS utility failed")
            
    except ImportError as e:
        print(f"⚠️  Django SMS utility not available: {e}")

if __name__ == '__main__':
    print("📱 Twilio SMS Testing Tool")
    print("=" * 40)
    
    # Test basic Twilio functionality
    twilio_works = test_twilio_sms()
    
    if twilio_works:
        print("\n" + "=" * 40)
        # Test Django integration
        test_django_sms()
    
    print("\n🎯 Next Steps:")
    print("1. If SMS works, update your .env file with real Twilio credentials")
    print("2. For production, add these credentials to Render environment variables")
    print("3. For Twilio trial accounts, verify recipient phone numbers in console")
    print("4. Restart your Django server to pick up new credentials")
