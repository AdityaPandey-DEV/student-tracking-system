#!/usr/bin/env python3
"""
Quick email test script.
Run this on Render Shell to test email sending.
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'enhanced_timetable_system.settings')
django.setup()

from django.core.mail import send_mail, get_connection
from django.conf import settings

def test_email_send(to_email='kingsong7060@gmail.com'):
    """Test sending an email."""
    print("\n" + "="*70)
    print("🧪 TESTING EMAIL SENDING")
    print("="*70 + "\n")
    
    # Display configuration
    print("📋 Current Configuration:")
    print(f"   EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"   EMAIL_HOST: {getattr(settings, 'EMAIL_HOST', 'Not set')}")
    print(f"   EMAIL_PORT: {getattr(settings, 'EMAIL_PORT', 'Not set')}")
    print(f"   EMAIL_USE_TLS: {getattr(settings, 'EMAIL_USE_TLS', 'Not set')}")
    print(f"   EMAIL_HOST_USER: {getattr(settings, 'EMAIL_HOST_USER', 'Not set')}")
    print(f"   DEFAULT_FROM_EMAIL: {getattr(settings, 'DEFAULT_FROM_EMAIL', 'Not set')}")
    
    sendgrid_key = os.environ.get('SENDGRID_API_KEY', '')
    if sendgrid_key:
        masked_key = sendgrid_key[:10] + '...' + sendgrid_key[-10:] if len(sendgrid_key) > 20 else '***'
        print(f"   SENDGRID_API_KEY: SET ({masked_key})")
    else:
        print("   SENDGRID_API_KEY: ❌ NOT SET")
    
    print("\n" + "-"*70 + "\n")
    
    # Test connection
    try:
        print("📡 Testing SMTP connection...")
        connection = get_connection(
            backend=settings.EMAIL_BACKEND,
            host=settings.EMAIL_HOST,
            port=settings.EMAIL_PORT,
            username=settings.EMAIL_HOST_USER,
            password=getattr(settings, 'EMAIL_HOST_PASSWORD', None),
            use_tls=settings.EMAIL_USE_TLS,
            timeout=getattr(settings, 'EMAIL_TIMEOUT', 10),
        )
        
        connection.open()
        print("   ✅ Connection opened successfully!")
        connection.close()
        print("   ✅ Connection closed successfully!")
        
    except Exception as e:
        print(f"   ❌ Connection failed: {type(e).__name__}: {str(e)}")
        print("\n⚠️  Cannot proceed with email test due to connection error.")
        return False
    
    print("\n" + "-"*70 + "\n")
    
    # Send test email
    try:
        print(f"📤 Sending test email to: {to_email}")
        print(f"   From: {settings.DEFAULT_FROM_EMAIL}")
        
        subject = '🧪 Test Email - Student Tracking System'
        message = f"""Hello!

This is a test email from the Student Tracking System.

If you received this email, your SendGrid configuration is working correctly!

Configuration Details:
- Email Backend: {settings.EMAIL_BACKEND}
- Email Host: {settings.EMAIL_HOST}
- From Email: {settings.DEFAULT_FROM_EMAIL}

Best regards,
Student Tracking System
        """
        
        result = send_mail(
            subject=subject,
            message=message.strip(),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[to_email],
            fail_silently=False,
            connection=connection
        )
        
        if result == 1:
            print("\n" + "="*70)
            print("✅ SUCCESS! Email sent successfully!")
            print("="*70)
            print(f"\n📬 Please check the inbox (and spam folder) of: {to_email}")
            print("   Email should arrive within 1-2 minutes.")
            print("\n✅ Your email configuration is working correctly!")
            return True
        else:
            print(f"\n⚠️  Email send returned: {result} (expected 1)")
            return False
            
    except Exception as e:
        print("\n" + "="*70)
        print("❌ FAILED! Email sending error")
        print("="*70)
        print(f"\nError Type: {type(e).__name__}")
        print(f"Error Message: {str(e)}")
        
        # Provide troubleshooting hints
        print("\n🔧 Troubleshooting:")
        error_str = str(e).lower()
        if 'authentication' in error_str or '535' in error_str:
            print("   → Authentication failed")
            print("   1. Verify your SendGrid API key is correct")
            print("   2. Check that EMAIL_HOST_USER = 'apikey' (literal string)")
            print("   3. Verify API key has 'Mail Send' permissions")
        elif 'sender' in error_str or 'verified' in error_str:
            print("   → Sender email not verified")
            print("   1. Go to SendGrid → Settings → Sender Authentication")
            print("   2. Verify:", settings.DEFAULT_FROM_EMAIL)
            print("   3. Check your email for verification link")
        elif 'timeout' in error_str:
            print("   → Connection timeout")
            print("   1. Check network connectivity")
            print("   2. Increase EMAIL_TIMEOUT setting")
        else:
            print("   1. Check SendGrid dashboard for errors")
            print("   2. Verify all environment variables are set correctly")
            print("   3. Check Render logs for more details")
        
        return False

if __name__ == '__main__':
    success = test_email_send('kingsong7060@gmail.com')
    sys.exit(0 if success else 1)

