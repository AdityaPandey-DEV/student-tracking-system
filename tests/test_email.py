#!/usr/bin/env python3
"""
Quick email test script for Student Tracking System
Run this after setting up Gmail App Password to test email functionality
"""
import os
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'enhanced_timetable_system.settings')
django.setup()

from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def check_env_file():
    """Check if .env file exists and has required email settings."""
    env_file = Path('.env')
    if not env_file.exists():
        print("❌ .env file not found!")
        print("\n📝 Create a .env file with your email settings:")
        print("""
# Add these lines to a new .env file:
DEBUG=True
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-16-character-app-password
        """)
        print("\n📋 See EMAIL_SETUP_GUIDE.md for detailed instructions!")
        return False
    return True

def test_email():
    try:
        print("🧪 Testing email configuration...")
        print(f"📧 Email Backend: {getattr(settings, 'EMAIL_BACKEND', 'Not configured')}")
        print(f"📧 Email Host: {getattr(settings, 'EMAIL_HOST', 'Not configured')}")
        print(f"📧 Email User: {getattr(settings, 'EMAIL_HOST_USER', 'Not configured')}")
        print(f"📧 DEBUG Mode: {settings.DEBUG}")
        
        # Check if console backend is being used
        if 'console' in settings.EMAIL_BACKEND.lower():
            print("\n🎯 Console email backend detected!")
            print("📧 In development mode, OTPs will be shown in console.")
            print("📧 To test real emails, configure SMTP settings in .env file.")
            return True
            
        # Validate required settings
        required_settings = ['EMAIL_HOST', 'EMAIL_HOST_USER', 'EMAIL_HOST_PASSWORD']
        missing = []
        
        for setting in required_settings:
            value = getattr(settings, setting, '')
            if not value or value in ['your-email@gmail.com', 'your-app-password']:
                missing.append(setting)
        
        if missing:
            print(f"\n❌ Missing email configuration: {', '.join(missing)}")
            print("\n📋 Please update your .env file with real values!")
            return False
        
        # Send test email
        print("\n📤 Sending test email...")
        subject = "Student Tracking System - Email Test"
        message = "This is a test email to verify SMTP configuration is working correctly!"
        from_email = settings.EMAIL_HOST_USER
        to_email = [settings.EMAIL_HOST_USER]  # Send to yourself
        
        result = send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=to_email,
            fail_silently=False
        )
        
        if result:
            print("✅ Email sent successfully!")
            print("✅ Gmail SMTP configuration is working!")
            print("✅ OTP emails should now be delivered to your inbox")
            print(f"\n📬 Check your inbox: {settings.EMAIL_HOST_USER}")
            return True
        else:
            print("❌ Email sending failed (no error thrown)")
            return False
            
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Email test failed: {error_msg}")
        
        # Provide specific guidance based on error
        if "535" in error_msg or "Username and Password not accepted" in error_msg:
            print("\n🔧 Gmail Authentication Error - Follow these steps:")
            print("1. ✅ Enable 2-Factor Authentication on your Gmail account")
            print("2. ✅ Generate App Password (NOT your regular Gmail password)")
            print("3. ✅ Use the 16-character app password in .env file")
            print("4. ✅ Remove any spaces from the app password")
        elif "Connection refused" in error_msg or "Name or service not known" in error_msg:
            print("\n🔧 Network/DNS Error:")
            print("1. ✅ Check your internet connection")
            print("2. ✅ Verify EMAIL_HOST is set to smtp.gmail.com")
            print("3. ✅ Check firewall settings")
        else:
            print("\n🔧 General troubleshooting:")
            print("1. ✅ Check .env file exists with correct email settings")
            print("2. ✅ Verify your Gmail credentials")
            print("3. ✅ See EMAIL_SETUP_GUIDE.md for detailed help")
        
        return False

def test_otp_generation():
    """Test OTP generation and email template."""
    try:
        print("\n🔢 Testing OTP generation...")
        from accounts.models import EmailOTP
        from utils.notifications import send_otp_notification
        
        test_email = settings.EMAIL_HOST_USER if hasattr(settings, 'EMAIL_HOST_USER') else "test@example.com"
        
        # Generate OTP
        otp_code = EmailOTP.generate_otp(test_email, 'registration')
        print(f"✅ OTP generated: {otp_code}")
        
        # Test notification sending
        success = send_otp_notification(test_email, otp_code, 'registration', method='email')
        
        if success:
            print("✅ OTP notification system working!")
        else:
            print("❌ OTP notification failed")
            
        return success
        
    except Exception as e:
        print(f"❌ OTP test failed: {str(e)}")
        return False

if __name__ == "__main__":
    print("🚀 Student Tracking System - Email Configuration Test")
    print("=" * 60)
    
    # Check environment setup
    if not check_env_file():
        print("\n⚠️  Please create .env file first, then run this test again.")
        exit(1)
    
    # Test email configuration
    email_success = test_email()
    
    # Test OTP system
    if email_success:
        otp_success = test_otp_generation()
        
        if otp_success:
            print("\n🎉 All tests passed! Your email system is ready.")
            print("\n📱 Users can now register with email OTP verification!")
        else:
            print("\n⚠️  Email works but OTP system has issues.")
    else:
        print("\n❌ Email configuration needs attention.")
        print("\n📋 Check EMAIL_SETUP_GUIDE.md for troubleshooting help.")
