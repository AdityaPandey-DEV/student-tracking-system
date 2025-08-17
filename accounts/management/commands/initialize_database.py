from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.db import connection
from django.conf import settings
import sys

class Command(BaseCommand):
    help = 'Initialize database with migrations and sample data - force execution'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force initialization even if tables exist',
        )

    def handle(self, *args, **options):
        self.stdout.write('🚀 Initializing database...\n')
        
        try:
            # Check database connection
            self.stdout.write('📡 Testing database connection...')
            with connection.cursor() as cursor:
                cursor.execute("SELECT version();")
                version = cursor.fetchone()[0]
                self.stdout.write(f'   ✓ Connected to: {version}')
            
            # Check if accounts_user table exists
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_schema = 'public' 
                        AND table_name = 'accounts_user'
                    );
                """)
                table_exists = cursor.fetchone()[0]
                
            if table_exists and not options['force']:
                self.stdout.write('   ⚠️ Tables already exist. Use --force to reinitialize.')
                return
            
            # Run migrations
            self.stdout.write('🔄 Running makemigrations...')
            call_command('makemigrations', verbosity=2)
            
            self.stdout.write('🔄 Applying migrations...')
            call_command('migrate', verbosity=2)
            
            # Verify table creation
            self.stdout.write('🔍 Verifying table creation...')
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT table_name FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name LIKE '%_user'
                    ORDER BY table_name;
                """)
                tables = cursor.fetchall()
                if tables:
                    self.stdout.write('   ✓ User tables found:')
                    for table in tables:
                        self.stdout.write(f'     - {table[0]}')
                else:
                    self.stdout.write('   ❌ No user tables found!')
                    return
            
            # Create superuser
            self.stdout.write('👤 Creating default superuser...')
            call_command('create_default_superuser')
            
            # Populate sample data
            self.stdout.write('📊 Populating sample data...')
            call_command('populate_realistic_data')
            
            self.stdout.write(self.style.SUCCESS('\n✅ Database initialization completed successfully!'))
            self.stdout.write('🔑 Login credentials:')
            self.stdout.write('   Admin: admin / admin123')
            self.stdout.write('   Teacher: teacher1 / teacher123')  
            self.stdout.write('   Student: student1 / student123')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Database initialization failed: {str(e)}')
            )
            import traceback
            self.stdout.write(traceback.format_exc())
            sys.exit(1)
