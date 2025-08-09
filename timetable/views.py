from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .models import Course, Subject, Teacher, Room, TimeSlot
from accounts.models import StudentProfile

@login_required
def initial_setup(request):
    """Initial setup for timetable data."""
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create_sample_data':
            try:
                with transaction.atomic():
                    # Create sample courses
                    btech, _ = Course.objects.get_or_create(
                        name='B.Tech',
                        defaults={
                            'full_name': 'Bachelor of Technology',
                            'duration_years': 4,
                            'description': 'Four-year undergraduate engineering program'
                        }
                    )
                    
                    bca, _ = Course.objects.get_or_create(
                        name='BCA',
                        defaults={
                            'full_name': 'Bachelor of Computer Applications',
                            'duration_years': 3,
                            'description': 'Three-year undergraduate computer science program'
                        }
                    )
                    
                    # Create sample subjects for B.Tech
                    Subject.objects.get_or_create(
                        code='CS101',
                        defaults={
                            'name': 'Data Structures',
                            'course': btech,
                            'year': 2,
                            'semester': 3,
                            'credits': 4
                        }
                    )
                    
                    Subject.objects.get_or_create(
                        code='CS102',
                        defaults={
                            'name': 'Algorithms',
                            'course': btech,
                            'year': 2,
                            'semester': 4,
                            'credits': 4
                        }
                    )
                    
                    Subject.objects.get_or_create(
                        code='MATH201',
                        defaults={
                            'name': 'Linear Algebra',
                            'course': btech,
                            'year': 2,
                            'semester': 3,
                            'credits': 3
                        }
                    )
                    
                    # Create sample teachers
                    Teacher.objects.get_or_create(
                        employee_id='T001',
                        defaults={
                            'name': 'Dr. John Smith',
                            'email': 'john.smith@college.edu',
                            'department': 'Computer Science',
                            'designation': 'Professor',
                            'specialization': 'Data Structures and Algorithms'
                        }
                    )
                    
                    Teacher.objects.get_or_create(
                        employee_id='T002',
                        defaults={
                            'name': 'Dr. Sarah Johnson',
                            'email': 'sarah.johnson@college.edu',
                            'department': 'Mathematics',
                            'designation': 'Associate Professor',
                            'specialization': 'Applied Mathematics'
                        }
                    )
                    
                    # Create sample rooms
                    Room.objects.get_or_create(
                        room_number='CS-101',
                        defaults={
                            'room_name': 'Computer Lab 1',
                            'room_type': 'lab',
                            'capacity': 40,
                            'floor': '1st Floor',
                            'building': 'CS Building'
                        }
                    )
                    
                    Room.objects.get_or_create(
                        room_number='LH-201',
                        defaults={
                            'room_name': 'Lecture Hall 201',
                            'room_type': 'classroom',
                            'capacity': 80,
                            'floor': '2nd Floor',
                            'building': 'Main Building'
                        }
                    )
                    
                    # Create time slots
                    time_slots = [
                        (1, '09:00:00', '09:50:00'),
                        (2, '10:00:00', '10:50:00'),
                        (3, '11:00:00', '11:50:00'),
                        (4, '12:00:00', '12:50:00'),
                        (5, '14:00:00', '14:50:00'),
                        (6, '15:00:00', '15:50:00'),
                        (7, '16:00:00', '16:50:00'),
                        (8, '17:00:00', '17:50:00'),
                    ]
                    
                    for period, start, end in time_slots:
                        TimeSlot.objects.get_or_create(
                            period_number=period,
                            defaults={
                                'start_time': start,
                                'end_time': end
                            }
                        )
                    
                    # Lunch break
                    TimeSlot.objects.get_or_create(
                        period_number=99,
                        defaults={
                            'start_time': '13:00:00',
                            'end_time': '14:00:00',
                            'is_break': True,
                            'break_duration': 60
                        }
                    )
                    
                messages.success(request, 'Sample data created successfully!')
            except Exception as e:
                messages.error(request, f'Failed to create sample data: {str(e)}')
        
        return redirect('timetable:initial_setup')
    
    # Get current counts
    stats = {
        'courses': Course.objects.count(),
        'subjects': Subject.objects.count(),
        'teachers': Teacher.objects.count(),
        'rooms': Room.objects.count(),
        'time_slots': TimeSlot.objects.count(),
        'students': StudentProfile.objects.count(),
    }
    
    return render(request, 'timetable/initial_setup.html', {'stats': stats})

def course_list(request):
    """List all courses."""
    courses = Course.objects.filter(is_active=True)
    return render(request, 'timetable/course_list.html', {'courses': courses})

def subject_list(request):
    """List all subjects."""
    subjects = Subject.objects.filter(is_active=True).select_related('course')
    return render(request, 'timetable/subject_list.html', {'subjects': subjects})

def teacher_list(request):
    """List all teachers."""
    teachers = Teacher.objects.filter(is_active=True)
    return render(request, 'timetable/teacher_list.html', {'teachers': teachers})

def room_list(request):
    """List all rooms."""
    rooms = Room.objects.filter(is_active=True)
    return render(request, 'timetable/room_list.html', {'rooms': rooms})
