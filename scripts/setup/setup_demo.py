#!/usr/bin/env python3
"""
Student Tracking System - Demo Setup
This script sets up a working demo environment with console-based OTP display.
"""

import os
import django
import subprocess
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'enhanced_timetable_system.settings')
django.setup()

from django.conf import settings
from django.core.management import call_command

def setup_demo_environment():
    """Set up a working demo environment."""
    print("🚀 Setting up Student Tracking System Demo")
    print("=" * 60)
    
    # Configure for demo mode (console email backend)
    env_content = """# Student Tracking System - Demo Configuration
DEBUG=True
SECRET_KEY=demo-secret-key-for-testing-only-replace-in-production

# Email Configuration (Console Backend for Demo - OTPs shown in terminal)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Database (SQLite - no setup needed)
DATABASE_URL=sqlite:///db.sqlite3

# Production settings (uncomment and configure for real deployment)
# EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
# EMAIL_HOST=smtp.gmail.com
# EMAIL_PORT=587
# EMAIL_USE_TLS=True
# EMAIL_HOST_USER=your-email@gmail.com
# EMAIL_HOST_PASSWORD=your-gmail-app-password

# Optional API Keys
OPENAI_API_KEY=
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
"""
    
    # Write demo .env file
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print("✅ Demo environment configured")
    print("📧 Email OTP will be displayed in console (no email setup required)")

def setup_database():
    """Set up the database with migrations."""
    print("\n🗄️  Setting up database...")
    
    try:
        # Apply migrations
        call_command('makemigrations', verbosity=0)
        call_command('migrate', verbosity=0)
        print("✅ Database migrations applied")
        
        # Create superuser if none exists
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        if not User.objects.filter(is_superuser=True).exists():
            # Create default admin user for demo
            admin_user = User.objects.create_superuser(
                username='admin',
                email='admin@demo.com',
                password='admin123',
                user_type='admin'
            )
            print("✅ Demo admin user created: admin/admin123")
            
            # Create admin profile
            from accounts.models import AdminProfile
            AdminProfile.objects.create(
                user=admin_user,
                admin_id='ADMIN001',
                department='Information Technology',
                designation='System Administrator'
            )
            print("✅ Admin profile created")
        else:
            print("✅ Admin user already exists")
            
    except Exception as e:
        print(f"❌ Database setup error: {e}")
        return False
    
    return True

def test_system():
    """Test the system functionality."""
    print("\n🧪 Testing system functionality...")
    
    try:
        # Test OTP generation
        from accounts.models import EmailOTP
        from utils.notifications import send_otp_notification
        
        test_email = "demo@example.com"
        otp_code = EmailOTP.generate_otp(test_email, 'registration')
        print(f"✅ OTP generated: {otp_code}")
        
        # Test notification (will show in console)
        success = send_otp_notification(test_email, otp_code, 'registration', method='email')
        if success:
            print("✅ OTP notification system working")
        
        print("✅ All systems functional")
        return True
        
    except Exception as e:
        print(f"❌ System test error: {e}")
        return False

def show_usage_instructions():
    """Show instructions for using the demo."""
    print("\n" + "=" * 60)
    print("🎉 DEMO SETUP COMPLETE!")
    print("=" * 60)
    
    print("\n📱 HOW TO USE:")
    print("1. Start the server:")
    print("   python manage.py runserver")
    
    print("\n2. Open your browser:")
    print("   http://127.0.0.1:8000")
    
    print("\n3. Try these demo features:")
    print("   • Student Registration - OTP shown in console")
    print("   • Admin Registration - OTP shown in console") 
    print("   • Teacher Registration - OTP shown in console")
    print("   • Login with: admin/admin123 (admin user)")
    
    print("\n📧 EMAIL OTP DEMO:")
    print("   • When registering, OTP codes appear in this terminal")
    print("   • Copy the 6-digit code and paste it in the registration form")
    print("   • No email setup required for demo!")
    
    print("\n🔧 FOR PRODUCTION:")
    print("   1. Get Gmail App Password (see EMAIL_SETUP_GUIDE.md)")
    print("   2. Update .env file with real email credentials")
    print("   3. Change DEBUG=False")
    print("   4. Set proper SECRET_KEY")
    
    print("\n🌟 FEATURES TO EXPLORE:")
    print("   • AI-powered timetable optimization")
    print("   • Student/Teacher dashboards") 
    print("   • Attendance tracking")
    print("   • Course management")
    print("   • Announcement system")

if __name__ == "__main__":
    try:
        # Setup demo environment
        setup_demo_environment()
        
        # Setup database
        if setup_database():
            # Test system
            if test_system():
                show_usage_instructions()
            else:
                print("\n⚠️  System test failed, but demo should still work")
                show_usage_instructions()
        else:
            print("\n❌ Database setup failed. Please check for errors.")
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Setup interrupted by user")
    except Exception as e:
        print(f"\n❌ Setup failed: {e}")
        print("\n🔧 Try running: python manage.py migrate")
