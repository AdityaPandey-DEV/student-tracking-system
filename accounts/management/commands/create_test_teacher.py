from django.core.management.base import BaseCommand
from django.db import transaction
from accounts.models import User, TeacherProfile
from timetable.models import Teacher


class Command(BaseCommand):
    help = 'Create a test teacher account for debugging login/registration issues'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, help='Teacher email address', default='teacher@test.com')
        parser.add_argument('--employee-id', type=str, help='Employee ID (optional)', default='T001')
        parser.add_argument('--password', type=str, help='Password', default='teacher123')

    def handle(self, *args, **options):
        email = options['email']
        employee_id = options['employee_id']
        password = options['password']
        
        try:
            with transaction.atomic():
                # Check if user already exists
                if User.objects.filter(email=email).exists():
                    self.stdout.write(
                        self.style.WARNING(f'User with email {email} already exists!')
                    )
                    return
                
                # Create User
                username = employee_id if employee_id else email
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    first_name='Test',
                    last_name='Teacher',
                    phone_number='+1234567890',
                    user_type='teacher'
                )
                user.set_password(password)
                user.save()
                
                # Create TeacherProfile
                teacher_profile = TeacherProfile.objects.create(
                    user=user,
                    employee_id=employee_id if employee_id else None,
                    department='Computer Science',
                    designation='Assistant Professor',
                    specialization='Web Development, Database Systems'
                )
                
                # Create corresponding Teacher model record
                teacher_employee_id = employee_id if employee_id else f"T{user.id:04d}"
                
                # Check if Teacher record already exists
                try:
                    teacher = Teacher.objects.get(employee_id=teacher_employee_id)
                    self.stdout.write(
                        self.style.WARNING(f'Teacher record with employee_id {teacher_employee_id} already exists, linking to existing record')
                    )
                except Teacher.DoesNotExist:
                    teacher = Teacher.objects.create(
                        employee_id=teacher_employee_id,
                        name=user.get_full_name(),
                        email=email,
                        phone_number=user.phone_number,
                        department=teacher_profile.department,
                        designation=teacher_profile.designation,
                        specialization=teacher_profile.specialization,
                        is_active=True
                    )
                
                # Link TeacherProfile to Teacher
                teacher_profile.teacher = teacher
                teacher_profile.save()
                
                self.stdout.write(
                    self.style.SUCCESS(f'✅ Test teacher created successfully!')
                )
                self.stdout.write(f'📧 Email: {email}')
                self.stdout.write(f'🆔 Username: {username}')
                self.stdout.write(f'👤 Employee ID: {employee_id or "None"}')
                self.stdout.write(f'🔒 Password: {password}')
                self.stdout.write(f'🔗 Teacher ID in timetable: {teacher.id}')
                self.stdout.write(
                    self.style.WARNING('\n⚠️  You can now test teacher login with either:')
                )
                self.stdout.write(f'   - Employee ID: {employee_id}')
                self.stdout.write(f'   - Email: {email}')
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error creating test teacher: {str(e)}')
            )
