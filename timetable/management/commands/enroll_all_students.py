from django.core.management.base import BaseCommand
from accounts.models import StudentProfile
from timetable.models import Subject, Enrollment
from django.db import transaction

class Command(BaseCommand):
    help = 'Enroll all students in their appropriate subjects'

    def handle(self, *args, **options):
        self.stdout.write('📝 Enrolling all students in subjects...\n')
        
        academic_year = "2024-25"
        all_students = StudentProfile.objects.all()
        total_enrollments = 0
        
        with transaction.atomic():
            for student in all_students:
                # Get subjects for student's course and year
                subjects = Subject.objects.filter(
                    course__name=student.course,
                    year=student.year
                )
                
                enrolled_count = 0
                for subject in subjects:
                    enrollment, created = Enrollment.objects.get_or_create(
                        student=student,
                        subject=subject,
                        academic_year=academic_year,
                        semester=subject.semester,
                        defaults={'is_active': True}
                    )
                    if created:
                        enrolled_count += 1
                        total_enrollments += 1
                
                if enrolled_count > 0:
                    self.stdout.write(f'  ✓ {student.roll_number}: Enrolled in {enrolled_count} subjects')
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Total new enrollments: {total_enrollments}'))
        self.stdout.write(f'✅ Total enrollments now: {Enrollment.objects.count()}')

