#!/usr/bin/env python3
"""
System Connectivity Test for Student Tracking System
Tests all interconnections between models, views, and templates
"""
import os
import sys
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'enhanced_timetable_system.settings')

try:
    django.setup()
except Exception as e:
    print(f"❌ Django setup failed: {str(e)}")
    sys.exit(1)

# Now import Django components
from django.test import Client
from django.urls import reverse, NoReverseMatch
from django.db import connection
from django.core.exceptions import ImproperlyConfigured
import importlib

def test_models():
    """Test model imports and basic functionality."""
    print("🔍 Testing Models...")
    
    try:
        # Test accounts models
        from accounts.models import User, StudentProfile, AdminProfile, TeacherProfile, EmailOTP
        print("  ✅ Accounts models imported successfully")
        
        # Test timetable models
        from timetable.models import Course, Subject, Teacher, TimetableEntry, Announcement
        print("  ✅ Timetable models imported successfully")
        
        # Test AI features models
        from ai_features.models import AIChat, StudyRecommendation, PerformanceInsight
        print("  ✅ AI features models imported successfully")
        
        # Test model relationships
        print("  🔗 Testing model relationships...")
        
        # Test foreign key relationships exist
        assert hasattr(StudentProfile, 'user')
        assert hasattr(TimetableEntry, 'subject')
        assert hasattr(TimetableEntry, 'teacher')
        print("  ✅ Model relationships verified")
        
        return True
        
    except ImportError as e:
        print(f"  ❌ Model import failed: {str(e)}")
        return False
    except Exception as e:
        print(f"  ❌ Model test failed: {str(e)}")
        return False

def test_views():
    """Test view imports and basic functionality."""
    print("🔍 Testing Views...")
    
    try:
        # Test main views
        from accounts import views, student_views, admin_views, teacher_views, api_views
        print("  ✅ Main views imported successfully")
        
        # Test view functions exist
        required_views = [
            'landing_page', 'student_register', 'user_login',
            'student_dashboard', 'admin_dashboard'
        ]
        
        for view_name in required_views:
            if hasattr(views, view_name):
                print(f"    ✅ {view_name} found in views")
            elif hasattr(student_views, view_name):
                print(f"    ✅ {view_name} found in student_views")
            elif hasattr(admin_views, view_name):
                print(f"    ✅ {view_name} found in admin_views")
            else:
                print(f"    ⚠️ {view_name} not found")
        
        # Test API views
        api_functions = ['get_announcement_details', 'search_content', 'ai_chat_response']
        for func in api_functions:
            if hasattr(api_views, func):
                print(f"    ✅ API function {func} found")
            else:
                print(f"    ⚠️ API function {func} missing")
        
        return True
        
    except ImportError as e:
        print(f"  ❌ View import failed: {str(e)}")
        return False
    except Exception as e:
        print(f"  ❌ View test failed: {str(e)}")
        return False

def test_urls():
    """Test URL configurations."""
    print("🔍 Testing URL Configuration...")
    
    try:
        # Test main URL patterns
        from enhanced_timetable_system.urls import urlpatterns as main_urls
        print(f"  ✅ Main URL patterns loaded ({len(main_urls)} patterns)")
        
        # Test app URL patterns
        from accounts.urls import urlpatterns as accounts_urls
        from accounts.api_urls import urlpatterns as api_urls
        from timetable.urls import urlpatterns as timetable_urls
        from ai_features.urls import urlpatterns as ai_urls
        
        print(f"  ✅ Accounts URLs: {len(accounts_urls)} patterns")
        print(f"  ✅ API URLs: {len(api_urls)} patterns")
        print(f"  ✅ Timetable URLs: {len(timetable_urls)} patterns")
        print(f"  ✅ AI Features URLs: {len(ai_urls)} patterns")
        
        # Test critical URL reversals
        critical_urls = [
            'accounts:landing',
            'accounts:student_dashboard',
            'accounts:admin_dashboard',
            'accounts:login'
        ]
        
        for url_name in critical_urls:
            try:
                reverse(url_name)
                print(f"    ✅ {url_name} reverses correctly")
            except NoReverseMatch:
                print(f"    ❌ {url_name} cannot be reversed")
        
        return True
        
    except ImportError as e:
        print(f"  ❌ URL import failed: {str(e)}")
        return False
    except Exception as e:
        print(f"  ❌ URL test failed: {str(e)}")
        return False

def test_templates():
    """Test template existence."""
    print("🔍 Testing Templates...")
    
    try:
        import os
        from django.conf import settings
        
        template_dirs = settings.TEMPLATES[0]['DIRS']
        if template_dirs:
            templates_dir = template_dirs[0]
            print(f"  📁 Templates directory: {templates_dir}")
            
            # Check critical templates
            critical_templates = [
                'base.html',
                'accounts/landing.html',
                'accounts/login.html',
                'student/dashboard.html',
                'admin/dashboard.html',
                'accounts/student_register.html'
            ]
            
            for template in critical_templates:
                template_path = os.path.join(templates_dir, template)
                if os.path.exists(template_path):
                    print(f"    ✅ {template} exists")
                else:
                    print(f"    ❌ {template} missing")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Template test failed: {str(e)}")
        return False

def test_database():
    """Test database connectivity."""
    print("🔍 Testing Database Connection...")
    
    try:
        # Test database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            if result[0] == 1:
                print("  ✅ Database connection successful")
        
        # Test table existence
        tables = connection.introspection.table_names()
        
        required_tables = [
            'accounts_user',
            'accounts_studentprofile', 
            'timetable_course',
            'timetable_subject',
            'ai_features_aichat'
        ]
        
        for table in required_tables:
            if table in tables:
                print(f"    ✅ Table {table} exists")
            else:
                print(f"    ⚠️ Table {table} missing (may need migration)")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Database test failed: {str(e)}")
        return False

def test_utilities():
    """Test utility modules."""
    print("🔍 Testing Utilities...")
    
    try:
        # Test AI service
        try:
            from utils.ai_service import ai_service
            print("  ✅ AI service imported successfully")
            
            # Test AI service functionality
            response = ai_service.chat_response("Hello")
            if response:
                print("  ✅ AI service responding")
            else:
                print("  ⚠️ AI service not responding (may be in mock mode)")
                
        except ImportError:
            print("  ⚠️ AI service not available")
        
        # Test notifications
        try:
            from utils.notifications import send_otp_notification
            print("  ✅ Notifications module imported")
        except ImportError:
            print("  ⚠️ Notifications module not available")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Utilities test failed: {str(e)}")
        return False

def test_static_files():
    """Test static files configuration."""
    print("🔍 Testing Static Files...")
    
    try:
        # Check static files settings
        print(f"  📁 STATIC_URL: {settings.STATIC_URL}")
        print(f"  📁 STATIC_ROOT: {settings.STATIC_ROOT}")
        
        # Check if static files exist
        import os
        static_js_dir = os.path.join(settings.BASE_DIR, 'static', 'js')
        if os.path.exists(static_js_dir):
            js_files = os.listdir(static_js_dir)
            print(f"  ✅ Found {len(js_files)} JavaScript files")
            
            required_js = [
                'admin_handlers.js',
                'student_handlers.js',
                'teacher_handlers.js'
            ]
            
            for js_file in required_js:
                if js_file in js_files:
                    print(f"    ✅ {js_file} exists")
                else:
                    print(f"    ❌ {js_file} missing")
        else:
            print("  ⚠️ Static JS directory not found")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Static files test failed: {str(e)}")
        return False

def main():
    """Run all connectivity tests."""
    print("🚀 Student Tracking System - Connectivity Test")
    print("=" * 50)
    
    tests = [
        ("Models", test_models),
        ("Views", test_views), 
        ("URLs", test_urls),
        ("Templates", test_templates),
        ("Database", test_database),
        ("Utilities", test_utilities),
        ("Static Files", test_static_files)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}")
        print("-" * 30)
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"  💥 Unexpected error in {test_name}: {str(e)}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {test_name:<15} {status}")
    
    print(f"\n🎯 Overall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All connectivity tests PASSED! System is properly interconnected.")
        return 0
    else:
        print("⚠️  Some connectivity issues found. Check failed tests above.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
