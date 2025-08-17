from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import AdminProfile
import os
import secrets
import string

User = get_user_model()

class Command(BaseCommand):
    help = 'Create a default superuser for deployment'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='admin',
            help='Username for the superuser (default: admin)'
        )
        parser.add_argument(
            '--email',
            type=str,
            default='admin@example.com',
            help='Email for the superuser (default: admin@example.com)'
        )
        parser.add_argument(
            '--password',
            type=str,
            help='Password for the superuser (will generate secure password if not provided)'
        )
    
    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'User "{username}" already exists.')
            )
            return
        
        # Get password from options, environment, or generate secure one
        password = options.get('password') or os.environ.get('DJANGO_SUPERUSER_PASSWORD')
        
        if not password:
            # Generate secure password
            alphabet = string.ascii_letters + string.digits + '!@#$%^&*'
            password = ''.join(secrets.choice(alphabet) for _ in range(16))
            generated_password = True
        else:
            generated_password = False
        
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            user_type='admin'
        )
        
        # Create admin profile
        AdminProfile.objects.create(
            user=user,
            admin_id='ADMIN001',
            department='Administration',
            designation='System Administrator'
        )
        
        if generated_password:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Superuser created successfully!\n'
                    f'Username: {username}\n'
                    f'Email: {email}\n'
                    f'Generated Password: {password}\n'
                    f'⚠️  IMPORTANT: Save this password securely and change it after first login!'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Superuser created successfully!\n'
                    f'Username: {username}\n'
                    f'Email: {email}\n'
                    f'Password: [provided/from environment]\n'
                    f'Please change the password after first login if needed.'
                )
            )
