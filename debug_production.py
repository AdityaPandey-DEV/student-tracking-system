#!/usr/bin/env python3
"""
Production debugging script to identify registration issues
"""

import os
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'enhanced_timetable_system.settings')
django.setup()

def check_email_configuration():
    """Check email configuration in production."""
    from django.conf import settings
    
    print("🔍 Email Configuration Analysis")
    print("=" * 50)
    
    # Check email backend
    backend = getattr(settings, 'EMAIL_BACKEND', 'Not set')
    print(f"📧 Email Backend: {backend}")
    
    # Check SMTP settings
    if 'smtp' in backend.lower():
        host = getattr(settings, 'EMAIL_HOST', 'Not set')
        port = getattr(settings, 'EMAIL_PORT', 'Not set')
        user = getattr(settings, 'EMAIL_HOST_USER', 'Not set')
        password = getattr(settings, 'EMAIL_HOST_PASSWORD', 'Not set')
        use_tls = getattr(settings, 'EMAIL_USE_TLS', 'Not set')
        
        print(f"📧 SMTP Host: {host}")
        print(f"📧 SMTP Port: {port}")
        print(f"📧 SMTP User: {user}")
        print(f"📧 SMTP Password: {'*' * len(str(password)) if password and password != 'Not set' else 'Not set'}")
        print(f"📧 Use TLS: {use_tls}")
        
        # Check for spaces in password
        if password and ' ' in str(password):
            print("❌ CRITICAL: Password contains spaces!")
            print("🔧 Fix: Remove spaces from EMAIL_HOST_PASSWORD")
            return False
        elif password and len(str(password)) == 16:
            print("✅ Password format looks correct")
            return True
        else:
            print("❌ Password issue detected")
            return False
    else:
        print("ℹ️  Using console backend (development mode)")
        return True

def test_email_sending():
    """Test actual email sending."""
    from django.core.mail import send_mail
    from django.conf import settings
    
    print("\n🧪 Email Sending Test")
    print("=" * 50)
    
    try:
        if not hasattr(settings, 'EMAIL_HOST_USER') or not settings.EMAIL_HOST_USER:
            print("❌ EMAIL_HOST_USER not configured")
            return False
            
        result = send_mail(
            subject='Enhanced Timetable System - Production Test',
            message='This is a test from your production deployment on Render.',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[settings.EMAIL_HOST_USER],
            fail_silently=False
        )
        
        if result:
            print("✅ Email sent successfully!")
            print(f"📬 Check inbox: {settings.EMAIL_HOST_USER}")
            return True
        else:
            print("❌ Email failed to send (no exception)")
            return False
            
    except Exception as e:
        error_msg = str(e)
        print(f"❌ Email error: {error_msg}")
        
        if "535" in error_msg:
            print("🔧 Gmail authentication error - check App Password")
        elif "Connection" in error_msg:
            print("🔧 Network/connection error")
        else:
            print("🔧 Unknown email error")
        
        return False

def test_otp_system():
    """Test OTP generation and sending."""
    from accounts.models import EmailOTP
    from utils.notifications import send_otp_notification
    from django.conf import settings
    
    print("\n🔢 OTP System Test")
    print("=" * 50)
    
    try:
        test_email = getattr(settings, 'EMAIL_HOST_USER', 'test@example.com')
        
        # Generate OTP
        otp_code = EmailOTP.generate_otp(test_email, 'registration')
        print(f"✅ OTP generated: {otp_code}")
        
        # Test notification
        success = send_otp_notification(test_email, otp_code, 'registration', method='email')
        
        if success:
            print("✅ OTP notification sent successfully!")
            print(f"📧 Check email: {test_email}")
            return True
        else:
            print("❌ OTP notification failed")
            return False
            
    except Exception as e:
        print(f"❌ OTP system error: {str(e)}")
        return False

def check_database_connection():
    """Check database connectivity."""
    from django.db import connection
    
    print("\n🗄️  Database Connection Test")
    print("=" * 50)
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
        
        if result:
            print("✅ Database connection working")
            return True
        else:
            print("❌ Database connection failed")
            return False
            
    except Exception as e:
        print(f"❌ Database error: {str(e)}")
        return False

def check_environment():
    """Check environment variables and settings."""
    from django.conf import settings
    
    print("\n⚙️  Environment Check")
    print("=" * 50)
    
    debug_mode = getattr(settings, 'DEBUG', True)
    secret_key = getattr(settings, 'SECRET_KEY', 'default')
    allowed_hosts = getattr(settings, 'ALLOWED_HOSTS', [])
    
    print(f"🐛 DEBUG mode: {debug_mode}")
    print(f"🔑 Secret key set: {len(secret_key) > 20}")
    print(f"🌐 Allowed hosts: {allowed_hosts}")
    
    issues = []
    if debug_mode:
        issues.append("DEBUG=True in production")
    if len(secret_key) < 20:
        issues.append("Weak SECRET_KEY")
    if not allowed_hosts or 'smart-time-table-management-system-1.onrender.com' not in str(allowed_hosts):
        issues.append("ALLOWED_HOSTS not configured properly")
    
    if issues:
        print("⚠️  Issues found:")
        for issue in issues:
            print(f"   • {issue}")
        return False
    else:
        print("✅ Environment configuration looks good")
        return True

def main():
    """Run all diagnostic tests."""
    print("🚀 Enhanced Timetable System - Production Diagnostics")
    print("=" * 60)
    
    tests = [
        ("Email Configuration", check_email_configuration),
        ("Database Connection", check_database_connection),
        ("Environment Settings", check_environment),
        ("Email Sending", test_email_sending),
        ("OTP System", test_otp_system),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 DIAGNOSTIC SUMMARY")
    print("=" * 60)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nTests passed: {passed}/{len(results)}")
    
    if passed == len(results):
        print("🎉 All tests passed! System should be working.")
    else:
        print("⚠️  Issues found. Check the failed tests above.")
        print("\n🔧 Most common fixes:")
        print("1. Remove spaces from EMAIL_HOST_PASSWORD in Render")
        print("2. Set DEBUG=False in production")
        print("3. Check Gmail App Password is correct")

if __name__ == "__main__":
    main()
