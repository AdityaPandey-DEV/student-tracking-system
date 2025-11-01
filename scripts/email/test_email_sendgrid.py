#!/usr/bin/env python
"""
Test email sending with current configuration.
Tests sending an email to kingsong7060@gmail.com
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'enhanced_timetable_system.settings')
django.setup()

from django.conf import settings
from django.core.mail import send_mail, get_connection
from django.core.mail.message import EmailMessage

def print_email_config():
    """Print current email configuration."""
    print("\n" + "="*60)
    print("📧 EMAIL CONFIGURATION STATUS")
    print("="*60)
    print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"EMAIL_PROVIDER: {getattr(settings, 'EMAIL_PROVIDER', 'Not set')}")
    print(f"EMAIL_HOST: {getattr(settings, 'EMAIL_HOST', 'Not set')}")
    print(f"EMAIL_PORT: {getattr(settings, 'EMAIL_PORT', 'Not set')}")
    print(f"EMAIL_USE_TLS: {getattr(settings, 'EMAIL_USE_TLS', 'Not set')}")
    print(f"EMAIL_HOST_USER: {getattr(settings, 'EMAIL_HOST_USER', 'Not set')}")
    print(f"DEFAULT_FROM_EMAIL: {getattr(settings, 'DEFAULT_FROM_EMAIL', 'Not set')}")
    print(f"EMAIL_TIMEOUT: {getattr(settings, 'EMAIL_TIMEOUT', 'Not set')}")
    
    # Check for SendGrid
    sendgrid_key = os.environ.get('SENDGRID_API_KEY', '')
    if sendgrid_key:
        print(f"SENDGRID_API_KEY: {'SET' if sendgrid_key else 'NOT SET'} (length: {len(sendgrid_key)})")
    else:
        print("SENDGRID_API_KEY: NOT SET")
    
    # Check EMAIL_HOST_PASSWORD
    email_pass = getattr(settings, 'EMAIL_HOST_PASSWORD', None)
    if email_pass:
        print(f"EMAIL_HOST_PASSWORD: SET (length: {len(email_pass)})")
    else:
        print("EMAIL_HOST_PASSWORD: NOT SET")
    print("="*60 + "\n")

def test_email_send(to_email='kingsong7060@gmail.com'):
    """Test sending an email."""
    print(f"\n🧪 Testing email sending to: {to_email}")
    print("-" * 60)
    
    try:
        # Get email connection
        connection = get_connection(
            backend=settings.EMAIL_BACKEND,
            host=settings.EMAIL_HOST,
            port=settings.EMAIL_PORT,
            username=settings.EMAIL_HOST_USER,
            password=getattr(settings, 'EMAIL_HOST_PASSWORD', None),
            use_tls=getattr(settings, 'EMAIL_USE_TLS', False),
            timeout=getattr(settings, 'EMAIL_TIMEOUT', 10),
        )
        
        # Test connection
        print("📡 Testing connection...")
        connection.open()
        print("✅ Connection opened successfully!")
        connection.close()
        print("✅ Connection closed successfully!")
        
        # Send test email
        print("\n📤 Sending test email...")
        subject = '🧪 Test Email - Student Tracking System'
        message = """
Hello!

This is a test email from the Student Tracking System.

If you received this email, your email configuration is working correctly!

Email Configuration:
- Backend: {backend}
- Provider: {provider}
- Host: {host}

Best regards,
Student Tracking System
        """.format(
            backend=settings.EMAIL_BACKEND,
            provider=getattr(settings, 'EMAIL_PROVIDER', 'N/A'),
            host=getattr(settings, 'EMAIL_HOST', 'N/A')
        )
        
        from_email = settings.DEFAULT_FROM_EMAIL
        
        result = send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=[to_email],
            fail_silently=False,
            connection=connection
        )
        
        if result == 1:
            print(f"✅ Email sent successfully to {to_email}!")
            print(f"✅ Return value: {result} (1 = success)")
            return True
        else:
            print(f"⚠️  Email send returned: {result} (expected 1)")
            return False
            
    except Exception as e:
        print(f"❌ Error sending email: {type(e).__name__}: {str(e)}")
        import traceback
        print("\n📋 Full traceback:")
        traceback.print_exc()
        return False

def main():
    """Main function."""
    print_email_config()
    
    # Check if configuration looks valid
    if settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
        print("⚠️  WARNING: Using console backend. Email will not actually be sent.")
        print("   To send real emails, set EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend\n")
    
    # Check for SendGrid
    if getattr(settings, 'EMAIL_PROVIDER', '').lower() == 'sendgrid':
        sendgrid_key = os.environ.get('SENDGRID_API_KEY', '')
        if not sendgrid_key:
            print("❌ ERROR: SendGrid provider selected but SENDGRID_API_KEY is not set!")
            print("   Please set SENDGRID_API_KEY environment variable.\n")
            return False
        elif not sendgrid_key.startswith('SG.'):
            print("⚠️  WARNING: SENDGRID_API_KEY doesn't start with 'SG.' - may be invalid")
    
    # Test email
    success = test_email_send('kingsong7060@gmail.com')
    
    if success:
        print("\n" + "="*60)
        print("✅ SUCCESS! Email configuration is working!")
        print("="*60)
        print(f"\n📬 Please check the inbox (and spam folder) of: kingsong7060@gmail.com")
    else:
        print("\n" + "="*60)
        print("❌ FAILED! Email configuration has issues.")
        print("="*60)
        print("\n🔧 Troubleshooting:")
        print("1. Check environment variables are set correctly")
        print("2. For SendGrid: Verify API key is correct and sender email is verified")
        print("3. For Gmail: Check app password is correct")
        print("4. Check Render logs for network errors")
    
    return success

if __name__ == '__main__':
    main()

