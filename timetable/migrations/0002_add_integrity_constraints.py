# Generated database migration for enhanced data integrity (SQLite compatible)

from django.db import migrations, models
from django.db.models import UniqueConstraint, CheckConstraint, Q

class Migration(migrations.Migration):

    dependencies = [
        ('timetable', '0001_initial'),
    ]

    operations = [
        # Add Django model-level constraints that work with SQLite
        # These constraints will be enforced at the application level
        
        # Add unique constraints to prevent scheduling conflicts
        migrations.AddConstraint(
            model_name='timetableentry',
            constraint=UniqueConstraint(
                fields=['room', 'day_of_week', 'time_slot', 'academic_year', 'semester'],
                condition=Q(is_active=True),
                name='unique_room_time_slot'
            ),
        ),
        
        migrations.AddConstraint(
            model_name='timetableentry',
            constraint=UniqueConstraint(
                fields=['teacher', 'day_of_week', 'time_slot', 'academic_year', 'semester'],
                condition=Q(is_active=True),
                name='unique_teacher_time_slot'
            ),
        ),
        
        migrations.AddConstraint(
            model_name='timetableentry',
            constraint=UniqueConstraint(
                fields=['course', 'year', 'section', 'day_of_week', 'time_slot', 'academic_year', 'semester'],
                condition=Q(is_active=True),
                name='unique_class_time_slot'
            ),
        ),
        
        # Add check constraints for data validation
        migrations.AddConstraint(
            model_name='timetableentry',
            constraint=CheckConstraint(
                check=Q(year__gte=1) & Q(year__lte=4),
                name='valid_year_range'
            ),
        ),
        
        migrations.AddConstraint(
            model_name='timetableentry',
            constraint=CheckConstraint(
                check=Q(day_of_week__gte=0) & Q(day_of_week__lte=6),
                name='valid_day_of_week'
            ),
        ),
    ]
