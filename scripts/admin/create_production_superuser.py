#!/usr/bin/env python
"""
Production Superuser Creation Script
===================================
Creates a superuser account for production deployment on Render.
Run this script in Render shell or as a management command.
"""

import os
import sys
import django
from django.core.management import execute_from_command_line

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'enhanced_timetable_system.settings')
# Add project root to path (go up 2 directories from scripts/admin/)
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)
django.setup()

from django.contrib.auth import get_user_model
from django.db import transaction

def create_production_superuser():
    """Create superuser for production environment."""
    User = get_user_model()
    
    # Production superuser credentials
    username = 'admin'
    email = 'adityapandey.dev.in@gmail.com'
    password = 'AdminPass123!'  # Change this to a secure password
    
    try:
        with transaction.atomic():
            # Check if superuser already exists
            if User.objects.filter(username=username).exists():
                print(f"✅ Superuser '{username}' already exists!")
                user = User.objects.get(username=username)
                print(f"📧 Email: {user.email}")
                print(f"🔑 Use existing credentials to login")
                return
            
            # Create superuser
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                user_type='admin'  # Set user type for your custom user model
            )
            
            print("🎉 Production superuser created successfully!")
            print(f"👤 Username: {username}")
            print(f"📧 Email: {email}")
            print(f"🔒 Password: {password}")
            print(f"🌐 Admin URL: https://your-app.onrender.com/admin/")
            print("\n⚠️  SECURITY: Change the password after first login!")
            
    except Exception as e:
        print(f"❌ Error creating superuser: {e}")

def create_interactive_superuser():
    """Create superuser with interactive prompts."""
    User = get_user_model()
    
    print("🔧 Creating Production Superuser")
    print("=" * 40)
    
    username = input("Username (default: admin): ").strip() or 'admin'
    email = input("Email address: ").strip()
    
    if not email:
        email = 'adityapandey.dev.in@gmail.com'
        print(f"Using default email: {email}")
    
    password = input("Password: ").strip()
    
    if not password:
        password = 'AdminPass123!'
        print("Using default password (change after login)")
    
    try:
        with transaction.atomic():
            if User.objects.filter(username=username).exists():
                print(f"❌ User '{username}' already exists!")
                return
            
            user = User.objects.create_superuser(
                username=username,
                email=email,
                password=password,
                user_type='admin'
            )
            
            print("✅ Superuser created successfully!")
            print(f"👤 Username: {username}")
            print(f"📧 Email: {email}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    # Check if running in production (Render)
    if os.environ.get('RENDER'):
        print("🌐 Running in Render production environment")
        create_production_superuser()
    else:
        print("💻 Running in development environment")
        create_interactive_superuser()
