#!/usr/bin/env python3
"""
SendGrid Setup Wizard for Student Tracking System
This script helps you set up SendGrid email service (recommended for Render free tier).
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

def print_header():
    print("📧 SendGrid Setup Wizard for Student Tracking System")
    print("=" * 60)
    print("SendGrid is recommended for Render free tier deployment")
    print("Gmail SMTP is often blocked on Render free tier")
    print("SendGrid provides 100 emails/day for free!\n")

def show_sendgrid_setup_steps():
    print("🔧 Step 1: Create SendGrid Account")
    print("-" * 40)
    print("1. Go to: https://signup.sendgrid.com/")
    print("2. Sign up for a free account (100 emails/day)")
    print("3. Verify your email address")
    
    choice = input("\n✅ Have you created a SendGrid account? (y/n): ").lower()
    if choice != 'y':
        print("\n⚠️  Please create a SendGrid account first!")
        print("Opening SendGrid signup page...")
        import webbrowser
        webbrowser.open("https://signup.sendgrid.com/")
        return False
    
    print("\n🔑 Step 2: Generate API Key")
    print("-" * 40)
    print("1. Go to: https://app.sendgrid.com/settings/api_keys")
    print("2. Click 'Create API Key'")
    print("3. Name it: 'Student Tracking System'")
    print("4. Select 'Full Access' permissions")
    print("5. Click 'Create & View'")
    print("6. Copy the API key (starts with 'SG.')")
    print("   ⚠️  You'll only see it once!")
    
    choice = input("\n📋 Ready to generate API Key? (y/n): ").lower()
    if choice == 'y':
        import webbrowser
        webbrowser.open("https://app.sendgrid.com/settings/api_keys")
    
    return True

def get_api_key():
    """Get SendGrid API key from user."""
    print("\n" + "=" * 60)
    print("📝 Enter SendGrid API Key")
    print("=" * 60)
    print("Format: SG.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx.xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    
    while True:
        api_key = input("\n🔑 SendGrid API Key: ").strip()
        
        if not api_key:
            print("❌ API key cannot be empty. Please try again.")
            continue
        
        if not api_key.startswith('SG.'):
            print("⚠️  Warning: SendGrid API keys usually start with 'SG.'")
            retry = input("Continue anyway? (y/n): ").lower()
            if retry != 'y':
                continue
        
        if len(api_key) < 20:
            print("❌ API key seems too short. Please check and try again.")
            continue
        
        # Confirm
        print(f"\n📋 You entered: {api_key[:10]}...{api_key[-10:]}")
        confirm = input("✅ Is this correct? (y/n): ").lower()
        if confirm == 'y':
            return api_key

def get_sender_email():
    """Get verified sender email from user."""
    print("\n" + "=" * 60)
    print("📧 Sender Email Configuration")
    print("=" * 60)
    print("This email must be verified in SendGrid")
    print("Go to: https://app.sendgrid.com/settings/sender_auth/senders/new")
    
    while True:
        email = input("\n📧 Sender Email (must be verified in SendGrid): ").strip().lower()
        
        if not email or '@' not in email:
            print("❌ Invalid email format. Please try again.")
            continue
        
        print(f"\n📋 Sender Email: {email}")
        confirm = input("✅ Is this correct? (y/n): ").lower()
        if confirm == 'y':
            return email

def update_env_file(api_key, sender_email):
    """Update .env file with SendGrid configuration."""
    env_file = Path(project_root) / '.env'
    
    # Read existing .env if it exists
    env_vars = {}
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip()
    
    # Update email configuration
    env_vars['EMAIL_BACKEND'] = 'django.core.mail.backends.smtp.EmailBackend'
    env_vars['EMAIL_PROVIDER'] = 'sendgrid'
    env_vars['EMAIL_HOST'] = 'smtp.sendgrid.net'
    env_vars['EMAIL_PORT'] = '587'
    env_vars['EMAIL_USE_TLS'] = 'True'
    env_vars['EMAIL_HOST_USER'] = 'apikey'
    env_vars['SENDGRID_API_KEY'] = api_key
    env_vars['DEFAULT_FROM_EMAIL'] = sender_email
    env_vars['SENDGRID_FROM_EMAIL'] = sender_email
    env_vars['EMAIL_TIMEOUT'] = '10'
    
    # Remove old Gmail-specific settings
    keys_to_remove = ['EMAIL_HOST_PASSWORD']  # Only remove if it's not needed
    for key in keys_to_remove:
        if key in env_vars and not key.startswith('SENDGRID'):
            del env_vars[key]
    
    # Write updated .env file
    with open(env_file, 'w') as f:
        f.write("# SendGrid Email Configuration\n")
        f.write("# Generated by setup_sendgrid.py\n\n")
        
        # Write email settings
        f.write("# Email Backend\n")
        for key, value in sorted(env_vars.items()):
            if key.startswith('EMAIL') or key.startswith('SENDGRID'):
                f.write(f"{key}={value}\n")
        
        # Write other settings (preserve non-email vars)
        f.write("\n# Other Settings\n")
        for key, value in sorted(env_vars.items()):
            if not (key.startswith('EMAIL') or key.startswith('SENDGRID')):
                f.write(f"{key}={value}\n")
    
    print(f"\n✅ Updated {env_file}")
    return True

def print_render_instructions():
    """Print instructions for setting up SendGrid on Render."""
    print("\n" + "=" * 60)
    print("🚀 Render Deployment Configuration")
    print("=" * 60)
    print("\nIn your Render Dashboard, add these environment variables:\n")
    print("EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend")
    print("EMAIL_PROVIDER=sendgrid")
    print("EMAIL_HOST=smtp.sendgrid.net")
    print("EMAIL_PORT=587")
    print("EMAIL_USE_TLS=True")
    print("EMAIL_HOST_USER=apikey")
    print("SENDGRID_API_KEY=<your-api-key-here>")
    print("DEFAULT_FROM_EMAIL=<your-verified-email>")
    print("EMAIL_TIMEOUT=10")
    print("\n⚠️  Make sure to verify your sender email in SendGrid first!")
    print("   Go to: https://app.sendgrid.com/settings/sender_auth/senders/new")

def main():
    print_header()
    
    if not show_sendgrid_setup_steps():
        return
    
    api_key = get_api_key()
    sender_email = get_sender_email()
    
    print("\n" + "=" * 60)
    print("💾 Saving Configuration")
    print("=" * 60)
    
    if update_env_file(api_key, sender_email):
        print("\n✅ SendGrid configuration saved successfully!")
        print("\n📋 Next Steps:")
        print("1. Verify your sender email in SendGrid")
        print("2. Test email sending: python scripts/tests/test_email.py")
        print("3. For Render deployment, see instructions below")
        
        print_render_instructions()
        
        print("\n✅ Setup complete! SendGrid is now configured.")
    else:
        print("\n❌ Failed to save configuration. Please check file permissions.")

if __name__ == '__main__':
    main()

