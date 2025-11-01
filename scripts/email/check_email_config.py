#!/usr/bin/env python3
"""
Simple script to check email configuration from environment variables.
This script doesn't require Django to be installed - it just reads env vars.
"""

import os
from pathlib import Path

def check_env_file():
    """Check .env file if it exists."""
    env_file = Path('.env')
    env_vars = {}
    
    if env_file.exists():
        print("✅ Found .env file\n")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    else:
        print("⚠️  No .env file found (this is okay if using Render environment variables)\n")
    
    return env_vars

def check_email_config():
    """Check email configuration."""
    print("="*70)
    print("📧 EMAIL CONFIGURATION CHECKER")
    print("="*70)
    print()
    
    # Check .env file
    env_vars = check_env_file()
    
    # Check environment variables (from Render or shell)
    print("Checking environment variables...")
    print("-" * 70)
    
    # Email backend
    email_backend = os.environ.get('EMAIL_BACKEND') or env_vars.get('EMAIL_BACKEND', 'Not set')
    print(f"EMAIL_BACKEND: {email_backend}")
    
    # Email provider
    email_provider = os.environ.get('EMAIL_PROVIDER') or env_vars.get('EMAIL_PROVIDER', 'Not set')
    print(f"EMAIL_PROVIDER: {email_provider}")
    
    # Email host
    email_host = os.environ.get('EMAIL_HOST') or env_vars.get('EMAIL_HOST', 'Not set')
    print(f"EMAIL_HOST: {email_host}")
    
    # Email port
    email_port = os.environ.get('EMAIL_PORT') or env_vars.get('EMAIL_PORT', 'Not set')
    print(f"EMAIL_PORT: {email_port}")
    
    # Email use TLS
    email_tls = os.environ.get('EMAIL_USE_TLS') or env_vars.get('EMAIL_USE_TLS', 'Not set')
    print(f"EMAIL_USE_TLS: {email_tls}")
    
    # Email host user
    email_user = os.environ.get('EMAIL_HOST_USER') or env_vars.get('EMAIL_HOST_USER', 'Not set')
    print(f"EMAIL_HOST_USER: {email_user}")
    
    # SendGrid API Key
    sendgrid_key = os.environ.get('SENDGRID_API_KEY') or env_vars.get('SENDGRID_API_KEY', '')
    if sendgrid_key:
        print(f"SENDGRID_API_KEY: ✅ SET (length: {len(sendgrid_key)}, starts with 'SG.'? {sendgrid_key.startswith('SG.')})")
    else:
        print("SENDGRID_API_KEY: ❌ NOT SET")
    
    # Email host password (check if set, don't print value)
    email_pass = os.environ.get('EMAIL_HOST_PASSWORD') or env_vars.get('EMAIL_HOST_PASSWORD', '')
    if email_pass:
        print(f"EMAIL_HOST_PASSWORD: ✅ SET (length: {len(email_pass)})")
    else:
        print("EMAIL_HOST_PASSWORD: ❌ NOT SET")
    
    # Default from email
    from_email = os.environ.get('DEFAULT_FROM_EMAIL') or env_vars.get('DEFAULT_FROM_EMAIL', 'Not set')
    print(f"DEFAULT_FROM_EMAIL: {from_email}")
    
    # Email timeout
    email_timeout = os.environ.get('EMAIL_TIMEOUT') or env_vars.get('EMAIL_TIMEOUT', 'Not set')
    print(f"EMAIL_TIMEOUT: {email_timeout}")
    
    print()
    print("="*70)
    print("📋 CONFIGURATION ANALYSIS")
    print("="*70)
    print()
    
    # Analyze configuration
    issues = []
    recommendations = []
    
    if 'console' in str(email_backend).lower():
        print("⚠️  Using console backend - emails won't be sent, only printed to console")
        recommendations.append("Set EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend for real emails")
    elif 'smtp' not in str(email_backend).lower():
        issues.append(f"Invalid EMAIL_BACKEND: {email_backend}")
    
    if email_provider.lower() == 'sendgrid':
        if not sendgrid_key:
            issues.append("SendGrid provider selected but SENDGRID_API_KEY is not set!")
        elif not sendgrid_key.startswith('SG.'):
            issues.append("SENDGRID_API_KEY format looks incorrect (should start with 'SG.')")
        
        if email_user != 'apikey':
            recommendations.append("For SendGrid, EMAIL_HOST_USER should be 'apikey' (literal string)")
        
        if email_host != 'smtp.sendgrid.net':
            recommendations.append("For SendGrid, EMAIL_HOST should be 'smtp.sendgrid.net'")
    else:
        if not email_pass and not sendgrid_key:
            issues.append("Neither EMAIL_HOST_PASSWORD nor SENDGRID_API_KEY is set!")
        
        if email_host == 'smtp.gmail.com' and not email_pass:
            issues.append("Gmail SMTP requires EMAIL_HOST_PASSWORD (app password)")
    
    if not from_email or from_email == 'Not set' or 'example.com' in from_email:
        issues.append("DEFAULT_FROM_EMAIL is not set or using placeholder")
    
    # Print results
    if not issues:
        print("✅ Configuration looks good!")
    else:
        print("❌ Issues found:")
        for issue in issues:
            print(f"   - {issue}")
    
    if recommendations:
        print("\n💡 Recommendations:")
        for rec in recommendations:
            print(f"   - {rec}")
    
    print()
    print("="*70)
    print("🧪 HOW TO TEST EMAIL ON RENDER")
    print("="*70)
    print()
    print("Since you're using Render, test email sending by:")
    print()
    print("1. Deploy your changes to Render")
    print("2. Try registering a new user at: /register/student/")
    print("3. Check Render logs for email sending status")
    print("4. If email fails, the OTP code will be displayed on screen")
    print()
    print("Or use Django shell on Render:")
    print("  python manage.py shell")
    print("  >>> from django.core.mail import send_mail")
    print("  >>> from django.conf import settings")
    print("  >>> send_mail('Test', 'Test message', settings.DEFAULT_FROM_EMAIL, ['kingsong7060@gmail.com'])")
    print()
    print("="*70)
    
    return len(issues) == 0

if __name__ == '__main__':
    success = check_email_config()
    exit(0 if success else 1)

