from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import AdminProfile

User = get_user_model()

class Command(BaseCommand):
    help = 'Create a default superuser for deployment'
    
    def handle(self, *args, **options):
        if not User.objects.filter(username='admin').exists():
            user = User.objects.create_superuser(
                username='admin',
                email='admin@example.com',
                password='admin123',
                user_type='admin'
            )
            
            # Create admin profile
            AdminProfile.objects.create(
                user=user,
                admin_id='ADMIN001',
                department='Administration',
                designation='System Administrator'
            )
            
            self.stdout.write(
                self.style.SUCCESS(
                    'Default superuser created successfully!\n'
                    'Username: admin\n'
                    'Password: admin123\n'
                    'Please change the password after first login.'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING('Superuser already exists.')
            )
