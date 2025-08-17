#!/usr/bin/env python3
"""
Gmail Setup Wizard for Enhanced Timetable System
This script will guide you through setting up Gmail SMTP for real email sending.
"""

import os
import sys
import webbrowser
from pathlib import Path

def print_header():
    print("📧 Gmail Setup Wizard for Enhanced Timetable System")
    print("=" * 60)
    print("This wizard will help you set up real email sending with Gmail.")
    print("Follow the steps below to get your Gmail App Password.\n")

def show_gmail_setup_steps():
    print("🔧 Step 1: Enable 2-Factor Authentication")
    print("-" * 40)
    print("1. Go to Google Account Security")
    print("2. Under 'Signing in to Google', find '2-Step Verification'")
    print("3. Click 'Get started' and follow the setup")
    print("4. You'll need your phone for SMS or call verification")
    
    choice = input("\n✅ Have you enabled 2-Factor Authentication? (y/n): ").lower()
    if choice != 'y':
        print("\n⚠️  You must enable 2-Factor Authentication first!")
        print("Opening Google Account Security page...")
        webbrowser.open("https://myaccount.google.com/security")
        return False
    
    print("\n🔑 Step 2: Generate App Password")
    print("-" * 40)
    print("1. In Google Account Security, find '2-Step Verification'")
    print("2. Scroll down to 'App passwords'")
    print("3. Click 'App passwords'")
    print("4. Select 'Mail' and 'Other (Custom name)'")
    print("5. Enter 'Enhanced Timetable System'")
    print("6. Click 'Generate'")
    print("7. Copy the 16-character password (format: abcd efgh ijkl mnop)")
    
    choice = input("\n📋 Ready to generate App Password? (y/n): ").lower()
    if choice == 'y':
        print("\nOpening App passwords page...")
        webbrowser.open("https://myaccount.google.com/apppasswords")
    
    return True

def get_app_password():
    print("\n🔐 Step 3: Enter Your App Password")
    print("-" * 40)
    print("Paste the 16-character App Password you just generated.")
    print("Format: abcd efgh ijkl mnop (spaces will be automatically removed)")
    
    while True:
        app_password = input("\n📝 App Password: ").strip().replace(" ", "")
        
        if len(app_password) == 16 and app_password.isalnum():
            return app_password
        else:
            print("❌ Invalid format! App Password should be 16 characters (letters and numbers only)")
            print("Example: abcdefghijklmnop")

def update_env_file(app_password):
    """Update .env file with the Gmail App Password."""
    env_file = Path('.env')
    
    if not env_file.exists():
        print("❌ .env file not found!")
        return False
    
    # Read current content
    with open(env_file, 'r') as f:
        content = f.read()
    
    # Replace the placeholder password
    updated_content = content.replace(
        'EMAIL_HOST_PASSWORD=your-gmail-app-password-here',
        f'EMAIL_HOST_PASSWORD={app_password}'
    )
    
    # Write back to file
    with open(env_file, 'w') as f:
        f.write(updated_content)
    
    print("✅ .env file updated with your Gmail App Password")
    return True

def test_email_setup():
    """Test the Gmail SMTP configuration."""
    print("\n🧪 Step 4: Testing Email Configuration")
    print("-" * 40)
    
    try:
        # Setup Django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'enhanced_timetable_system.settings')
        import django
        django.setup()
        
        from django.core.mail import send_mail
        from django.conf import settings
        
        print("📤 Sending test email...")
        
        result = send_mail(
            subject='Enhanced Timetable System - Email Test ✅',
            message='Congratulations! Your Gmail SMTP configuration is working correctly.',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.EMAIL_HOST_USER],  # Send to yourself
            fail_silently=False
        )
        
        if result:
            print("✅ Test email sent successfully!")
            print(f"📬 Check your inbox: {settings.EMAIL_HOST_USER}")
            print("📧 You should receive a test email within 1-2 minutes.")
            return True
        else:
            print("❌ Test email failed (no exception thrown)")
            return False
            
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Email test failed: {error_msg}")
        
        if "535" in error_msg or "Username and Password not accepted" in error_msg:
            print("\n🔧 Authentication Error Solutions:")
            print("1. ✅ Double-check your App Password is correct")
            print("2. ✅ Make sure 2-Factor Authentication is enabled")
            print("3. ✅ Try generating a new App Password")
            print("4. ✅ Remove any spaces from the App Password")
        else:
            print("\n🔧 General troubleshooting:")
            print("1. ✅ Check your internet connection")
            print("2. ✅ Verify Gmail credentials")
            print("3. ✅ Try running the test again in a few minutes")
        
        return False

def test_otp_system():
    """Test the complete OTP email system."""
    print("\n🔢 Step 5: Testing OTP System")
    print("-" * 40)
    
    try:
        import django
        from accounts.models import EmailOTP
        from utils.notifications import send_otp_notification
        
        test_email = "kingsong700@gmail.com"
        
        print("🎲 Generating test OTP...")
        otp_code = EmailOTP.generate_otp(test_email, 'registration')
        print(f"✅ OTP generated: {otp_code}")
        
        print("📤 Sending OTP email...")
        success = send_otp_notification(test_email, otp_code, 'registration', method='email')
        
        if success:
            print("✅ OTP email sent successfully!")
            print(f"📧 Check your inbox for OTP: {otp_code}")
            print("📱 You can now use this OTP to test user registration!")
            return True
        else:
            print("❌ OTP email sending failed")
            return False
            
    except Exception as e:
        print(f"❌ OTP test failed: {str(e)}")
        return False

def show_completion_message():
    print("\n" + "=" * 60)
    print("🎉 GMAIL SETUP COMPLETE!")
    print("=" * 60)
    
    print("\n📱 What's Working Now:")
    print("✅ Real emails sent to user inboxes")
    print("✅ Professional OTP verification emails")
    print("✅ Student, Teacher, Admin registration")
    print("✅ Password reset emails")
    
    print("\n🚀 Next Steps:")
    print("1. Restart your Django server:")
    print("   python manage.py runserver")
    
    print("\n2. Test user registration:")
    print("   • Go to http://127.0.0.1:8000")
    print("   • Try registering a new account")
    print("   • Check your email for OTP codes")
    
    print("\n📧 Email Features:")
    print("• Beautiful HTML email templates")
    print("• 6-digit OTP codes with 10-minute expiration")
    print("• Branded emails for your institution")
    print("• Reliable Gmail SMTP delivery")

def main():
    print_header()
    
    # Step 1 & 2: Gmail setup guide
    if not show_gmail_setup_steps():
        print("\n⏸️  Setup paused. Run this script again after enabling 2-Factor Authentication.")
        return
    
    # Step 3: Get App Password
    app_password = get_app_password()
    
    # Update .env file
    if not update_env_file(app_password):
        print("\n❌ Failed to update .env file")
        return
    
    # Step 4: Test email
    if test_email_setup():
        # Step 5: Test OTP system
        if test_otp_system():
            show_completion_message()
        else:
            print("\n⚠️  Email works but OTP system has issues. Registration should still work.")
    else:
        print("\n❌ Email setup incomplete. Please check the error messages above.")
        print("\n🔄 You can run this script again to retry the setup.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup cancelled by user")
    except Exception as e:
        print(f"\n❌ Setup error: {e}")
        print("\n🔧 Try running: python -m pip install django python-decouple")
