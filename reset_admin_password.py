#!/usr/bin/env python
"""
Reset Admin Password Script
==========================
Quick utility to reset the superuser password.
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'enhanced_timetable_system.settings')
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from django.contrib.auth import get_user_model

def reset_admin_password():
    User = get_user_model()
    
    try:
        # Find the admin user
        admin_user = User.objects.get(username='aditya')
        
        # Set new password
        new_password = input("Enter new password for admin user 'aditya': ")
        confirm_password = input("Confirm password: ")
        
        if new_password != confirm_password:
            print("❌ Passwords don't match!")
            return
        
        admin_user.set_password(new_password)
        admin_user.save()
        
        print("✅ Password updated successfully for admin user 'aditya'")
        print("🔑 You can now login to /admin/ with the new password")
        
    except User.DoesNotExist:
        print("❌ Admin user 'aditya' not found!")
        print("🔧 Create a new superuser with: python manage.py createsuperuser")

if __name__ == "__main__":
    reset_admin_password()
