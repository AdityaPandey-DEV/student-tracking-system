"""
Django Management Command: Create Production Superuser
=====================================================
Creates a superuser for production deployment.

Usage:
    python manage.py create_production_admin
    python manage.py create_production_admin --username admin --email admin@example.com
"""

from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.db import transaction
import os

class Command(BaseCommand):
    help = 'Create a superuser for production deployment'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            default='admin',
            help='Username for the superuser (default: admin)'
        )
        parser.add_argument(
            '--email',
            default='adityapandey.dev.in@gmail.com',
            help='Email address for the superuser'
        )
        parser.add_argument(
            '--password',
            help='Password for the superuser (if not provided, will use default)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force creation even if user exists'
        )

    def handle(self, *args, **options):
        User = get_user_model()
        
        username = options['username']
        email = options['email']
        password = options.get('password') or 'AdminPass123!'
        
        self.stdout.write(
            self.style.SUCCESS('🔧 Creating Production Superuser')
        )
        self.stdout.write('=' * 50)
        
        try:
            with transaction.atomic():
                # Check if user already exists
                if User.objects.filter(username=username).exists():
                    if not options['force']:
                        existing_user = User.objects.get(username=username)
                        self.stdout.write(
                            self.style.WARNING(f'⚠️  Superuser "{username}" already exists!')
                        )
                        self.stdout.write(f'📧 Email: {existing_user.email}')
                        self.stdout.write(f'🔑 Use existing credentials to login')
                        self.stdout.write(f'🌐 Admin URL: /admin/')
                        return
                    else:
                        # Delete existing user if force is used
                        User.objects.filter(username=username).delete()
                        self.stdout.write(
                            self.style.WARNING(f'🗑️  Deleted existing user "{username}"')
                        )
                
                # Create superuser
                user = User.objects.create_superuser(
                    username=username,
                    email=email,
                    password=password,
                    user_type='admin'
                )
                
                self.stdout.write(
                    self.style.SUCCESS('🎉 Production superuser created successfully!')
                )
                self.stdout.write(f'👤 Username: {username}')
                self.stdout.write(f'📧 Email: {email}')
                
                if not options.get('password'):
                    self.stdout.write(f'🔒 Password: {password}')
                    self.stdout.write(
                        self.style.WARNING('⚠️  SECURITY: Change the password after first login!')
                    )
                
                # Determine the base URL
                if os.environ.get('RENDER'):
                    domain = os.environ.get('RENDER_EXTERNAL_URL', 'your-app.onrender.com')
                    admin_url = f'{domain}/admin/'
                else:
                    admin_url = 'http://127.0.0.1:8000/admin/'
                
                self.stdout.write(f'🌐 Admin URL: {admin_url}')
                
                # Additional setup for production
                if os.environ.get('RENDER'):
                    self.stdout.write('\n' + '=' * 50)
                    self.stdout.write(
                        self.style.SUCCESS('🚀 Production Setup Complete!')
                    )
                    self.stdout.write('📋 Next Steps:')
                    self.stdout.write('1. Visit the admin URL above')
                    self.stdout.write('2. Login with the credentials shown')
                    self.stdout.write('3. Change the default password immediately')
                    self.stdout.write('4. Configure additional admin users if needed')
                
        except Exception as e:
            raise CommandError(f'❌ Error creating superuser: {e}')
        
        self.stdout.write('\n' + '✅ Command completed successfully!')
