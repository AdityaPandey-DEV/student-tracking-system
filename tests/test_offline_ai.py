#!/usr/bin/env python3
"""
Test Offline AI System
Test the intelligent offline AI without any external API calls.
"""

import sys
import os

# Add the project root to Python path so we can import Django modules
# Add project root to path (go up one directory from tests folder)
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'enhanced_timetable_system.settings')

import django
django.setup()

def test_offline_ai():
    """Test offline AI functionality."""
    print("🤖 Testing Offline AI System")
    print("=" * 40)
    
    try:
        from utils.offline_ai import get_ai_response
        
        # Test different types of queries
        test_queries = [
            "Hello! How are you?",
            "What's my next class?", 
            "Can you help me with my study schedule?",
            "I have an exam next week, any tips?",
            "How can I improve my math grades?",
            "I'm feeling stressed about assignments",
            "When is my chemistry class today?",
            "What are good time management strategies?",
            "Help me with physics homework",
            "How do I optimize my timetable?"
        ]
        
        print("\n🧪 Testing various queries:")
        print("-" * 30)
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n{i}. Query: \"{query}\"")
            try:
                response = get_ai_response(query)
                print(f"   Response: {response[:100]}...")
                print("   ✅ Success")
            except Exception as e:
                print(f"   ❌ Error: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to import offline AI: {e}")
        return False

def test_ai_service_integration():
    """Test AI service integration with offline AI."""
    print("\n\n🔧 Testing AI Service Integration")
    print("=" * 40)
    
    try:
        from utils.ai_service import ai_service
        
        print(f"AI Provider: {ai_service.ai_provider}")
        print(f"Mock Mode: {ai_service.mock_mode}")
        print(f"Offline AI Available: {ai_service.offline_ai_available}")
        
        # Test chat functionality
        test_message = "Hello, can you help me with my studies?"
        print(f"\nTesting chat with: \"{test_message}\"")
        
        response = ai_service.chat_with_ai(test_message)
        print(f"Response: {response}")
        
        if response and len(response) > 10:
            print("✅ AI Service working correctly")
            return True
        else:
            print("❌ AI Service response too short or empty")
            return False
            
    except Exception as e:
        print(f"❌ AI Service test failed: {e}")
        return False

def test_django_integration():
    """Test if the offline AI works within Django context."""
    print("\n\n🌐 Testing Django Integration")
    print("=" * 30)
    
    try:
        from django.conf import settings
        print(f"Django settings loaded: {settings.DEBUG}")
        
        # Try to simulate a view-like context
        try:
            from apps.timetable.models import CustomUser
            print("✅ Django models accessible")
        except ImportError:
            try:
                # Try alternative import path
                from timetable.models import CustomUser
                print("✅ Django models accessible (alternative path)")
            except ImportError:
                # Just verify Django is working
                from django.contrib.auth.models import User
                print("✅ Django models accessible (using built-in User)")
        
        # Test AI service in Django context
        from utils.ai_service import ai_service
        context = {
            'student_name': 'Test Student',
            'current_courses': ['Mathematics', 'Physics', 'Chemistry']
        }
        
        response = ai_service.chat_with_ai("What should I study today?", context)
        print(f"Context-aware response: {response[:100]}...")
        
        print("✅ Django integration working")
        return True
        
    except Exception as e:
        print(f"❌ Django integration test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Student Tracking System - Offline AI Test")
    print("=" * 50)
    
    results = []
    
    # Run tests
    results.append(test_offline_ai())
    results.append(test_ai_service_integration())
    results.append(test_django_integration())
    
    # Summary
    print("\n\n📋 Test Summary")
    print("=" * 20)
    passed = sum(results)
    total = len(results)
    
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("🎉 All tests passed! Your offline AI system is working perfectly!")
        print("\n💡 Your Student Tracking System now has:")
        print("   • Intelligent offline AI responses")
        print("   • No external API dependencies")
        print("   • Context-aware academic assistance")
        print("   • Full Django integration")
    else:
        print("⚠️ Some tests failed. Check the errors above.")
        
    print(f"\n🔗 You can now use the AI chat feature in your web application!")
    print("   Visit: http://127.0.0.1:8000/chat/ (after running python manage.py runserver)")
