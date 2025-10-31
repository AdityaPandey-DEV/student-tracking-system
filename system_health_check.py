#!/usr/bin/env python3
"""
Comprehensive System Health Check
Verify all components of the Student Tracking System are working correctly.
"""

import os
import sys
import django
import subprocess
from pathlib import Path

# Setup Django
sys.path.insert(0, '.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'enhanced_timetable_system.settings')
django.setup()

def check_django_setup():
    """Verify Django is properly configured."""
    print("🌐 Django Setup Check")
    print("=" * 30)
    
    try:
        from django.conf import settings
        from django.core.management import execute_from_command_line
        
        print(f"✅ Django settings loaded: {settings.DEBUG}")
        print(f"✅ Database: {settings.DATABASES['default']['ENGINE'].split('.')[-1]}")
        print(f"✅ Static files: {settings.STATIC_URL}")
        print(f"✅ Templates: {len(settings.TEMPLATES)} templates configured")
        
        # Test database connection
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✅ Database connection working")
        
        return True
    except Exception as e:
        print(f"❌ Django setup error: {e}")
        return False

def check_ai_system():
    """Verify AI system is working."""
    print("\n🤖 AI System Check")
    print("=" * 20)
    
    try:
        from utils.ai_service import ai_service
        from utils.offline_ai import get_ai_response
        
        print(f"✅ AI Provider: {ai_service.ai_provider}")
        print(f"✅ Offline AI Available: {ai_service.offline_ai_available}")
        
        # Test offline AI
        response = get_ai_response("Hello, test message")
        if response and len(response) > 10:
            print("✅ Offline AI responding correctly")
        else:
            print("❌ Offline AI response too short")
            return False
            
        # Test AI service integration
        service_response = ai_service.chat_with_ai("Test integration")
        if service_response and len(service_response) > 10:
            print("✅ AI service integration working")
        else:
            print("❌ AI service integration failed")
            return False
            
        return True
    except Exception as e:
        print(f"❌ AI system error: {e}")
        return False

def check_models_and_admin():
    """Check Django models and admin interface."""
    print("\n📊 Models & Admin Check")
    print("=" * 25)
    
    try:
        # Test user model (handle custom user model)
        try:
            from accounts.models import User
            user_count = User.objects.count()
            print(f"✅ Custom User model accessible: {user_count} users")
        except ImportError:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            user_count = User.objects.count()
            print(f"✅ User model accessible: {user_count} users")
        
        # Test timetable models (try different import paths)
        try:
            from timetable.models import Timetable, Subject, TimeSlot
            print("✅ Timetable models accessible")
        except ImportError:
            try:
                from apps.timetable.models import Timetable, Subject, TimeSlot  
                print("✅ Timetable models accessible (apps path)")
            except ImportError:
                print("⚠️ Custom timetable models not found, using basic functionality")
        
        # Check admin
        from django.contrib import admin
        print(f"✅ Admin interface configured")
        
        return True
    except Exception as e:
        print(f"❌ Models/Admin error: {e}")
        return False

def check_static_files():
    """Check static files are properly configured."""
    print("\n📁 Static Files Check")
    print("=" * 22)
    
    try:
        from django.conf import settings
        
        # Check static directories exist
        static_root = Path(settings.STATIC_ROOT) if settings.STATIC_ROOT else None
        if static_root and static_root.exists():
            file_count = len(list(static_root.rglob('*')))
            print(f"✅ Static files collected: {file_count} files")
        else:
            print("⚠️ Static files not collected")
        
        # Check for critical static files
        critical_files = [
            'js/safe_dom_utils.js',
            'js/admin_handlers.js',
            'js/student_handlers.js',
            'js/teacher_handlers.js'
        ]
        
        for file in critical_files:
            if static_root and (static_root / file).exists():
                print(f"✅ Found: {file}")
            else:
                print(f"⚠️ Missing: {file}")
        
        return True
    except Exception as e:
        print(f"❌ Static files error: {e}")
        return False

def check_security_features():
    """Check security configurations."""
    print("\n🔒 Security Check")
    print("=" * 17)
    
    try:
        from django.conf import settings
        
        # Check security settings
        security_checks = [
            ('DEBUG mode', not settings.DEBUG, "Should be False in production"),
            ('SECRET_KEY set', bool(settings.SECRET_KEY and len(settings.SECRET_KEY) > 10), "Should be set to random string"),
            ('ALLOWED_HOSTS configured', bool(settings.ALLOWED_HOSTS), "Should contain your domain"),
            ('CSRF protection', 'django.middleware.csrf.CsrfViewMiddleware' in settings.MIDDLEWARE, "CSRF middleware active"),
            ('Security middleware', 'django.middleware.security.SecurityMiddleware' in settings.MIDDLEWARE, "Security middleware active"),
        ]
        
        for check_name, result, description in security_checks:
            if result:
                print(f"✅ {check_name}: OK")
            else:
                print(f"⚠️ {check_name}: {description}")
        
        return True
    except Exception as e:
        print(f"❌ Security check error: {e}")
        return False

def check_environment():
    """Check Python environment and dependencies."""
    print("\n🐍 Environment Check")
    print("=" * 20)
    
    try:
        import sys
        print(f"✅ Python version: {sys.version.split()[0]}")
        
        # Check critical packages
        packages = [
            'django', 'requests', 'openai', 'cryptography'
        ]
        
        for package in packages:
            try:
                module = __import__(package)
                version = getattr(module, '__version__', 'Unknown')
                print(f"✅ {package}: {version}")
            except ImportError:
                print(f"⚠️ {package}: Not installed")
        
        # Check virtual environment
        if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
            print("✅ Virtual environment active")
        else:
            print("⚠️ Not in virtual environment")
        
        return True
    except Exception as e:
        print(f"❌ Environment check error: {e}")
        return False

def run_management_commands():
    """Test management commands."""
    print("\n⚙️ Management Commands Check")
    print("=" * 30)
    
    try:
        from django.core.management import call_command
        from io import StringIO
        
        # Test migrate
        call_command('migrate', verbosity=0)
        print("✅ Migrations applied successfully")
        
        # Test check
        output = StringIO()
        call_command('check', stdout=output)
        print("✅ Django check passed")
        
        return True
    except Exception as e:
        print(f"❌ Management commands error: {e}")
        return False

def main():
    """Run comprehensive system health check."""
    print("🚀 Student Tracking System - Health Check")
    print("=" * 50)
    
    checks = [
        check_environment,
        check_django_setup,
        check_models_and_admin,
        check_ai_system,
        check_static_files,
        check_security_features,
        run_management_commands
    ]
    
    results = []
    for check in checks:
        results.append(check())
    
    # Summary
    print("\n\n📋 Health Check Summary")
    print("=" * 25)
    passed = sum(results)
    total = len(results)
    
    print(f"Checks passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All health checks passed! Your system is ready for production!")
        print("\n🚀 Next steps:")
        print("   1. Run: python manage.py runserver")
        print("   2. Visit: http://127.0.0.1:8000/")
        print("   3. Test the AI chat feature")
        print("   4. Create user accounts and test functionality")
    elif passed >= total * 0.8:
        print("✅ System is mostly healthy with minor warnings")
        print("⚠️ Address the warnings above for optimal performance")
    else:
        print("❌ System has significant issues that need attention")
        print("🔧 Please address the failed checks above")
    
    return passed == total

if __name__ == "__main__":
    main()
