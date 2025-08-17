#!/usr/bin/env python3
"""
Script to reset and rebuild Django migrations for PostgreSQL compatibility
Run this script before deploying to ensure clean PostgreSQL-compatible migrations
"""

import os
import shutil
import django
from django.conf import settings
from django.core.management import execute_from_command_line

def setup_django():
    """Setup Django environment"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'enhanced_timetable_system.settings')
    django.setup()

def reset_migrations():
    """Reset all migration files"""
    print("🔄 Resetting Django migrations for PostgreSQL compatibility...")
    
    apps_with_migrations = ['accounts', 'timetable', 'ai_features']
    
    for app in apps_with_migrations:
        migrations_dir = os.path.join(app, 'migrations')
        
        if os.path.exists(migrations_dir):
            print(f"📁 Cleaning migrations for {app}...")
            
            # Keep __init__.py, remove everything else
            for filename in os.listdir(migrations_dir):
                if filename != '__init__.py' and filename.endswith('.py'):
                    file_path = os.path.join(migrations_dir, filename)
                    os.remove(file_path)
                    print(f"   ❌ Removed {filename}")
        
        print(f"   ✅ {app} migrations cleaned")

def create_fresh_migrations():
    """Create fresh migrations"""
    print("\n🏗️  Creating fresh PostgreSQL-compatible migrations...")
    
    try:
        # Create initial migrations for all apps
        execute_from_command_line(['manage.py', 'makemigrations', 'accounts'])
        execute_from_command_line(['manage.py', 'makemigrations', 'timetable'])
        execute_from_command_line(['manage.py', 'makemigrations', 'ai_features'])
        
        print("✅ Fresh migrations created successfully!")
        
    except Exception as e:
        print(f"❌ Error creating migrations: {str(e)}")
        raise

def main():
    """Main function"""
    print("🚀 Starting Django migrations reset for PostgreSQL...")
    print("=" * 60)
    
    try:
        setup_django()
        reset_migrations()
        create_fresh_migrations()
        
        print("\n" + "=" * 60)
        print("✅ Migration reset completed successfully!")
        print("📝 Next steps:")
        print("   1. Commit these new migration files")
        print("   2. Deploy to Render")
        print("   3. Migrations will be applied automatically during build")
        
    except Exception as e:
        print(f"\n❌ Migration reset failed: {str(e)}")
        import traceback
        print(traceback.format_exc())
        exit(1)

if __name__ == '__main__':
    main()
