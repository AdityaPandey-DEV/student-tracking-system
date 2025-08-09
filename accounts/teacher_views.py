"""
Teacher dashboard and management views.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, Count
from django.db import transaction
from django.utils import timezone
from datetime import datetime, timedelta
import json

from accounts.models import User, StudentProfile, TeacherProfile
from timetable.models import (
    Course, Subject, Teacher, TeacherSubject, TimeSlot, Room,
    TimetableEntry, Enrollment, Attendance, Announcement
)
from ai_features.models import StudyMaterial, Assignment

def teacher_required(view_func):
    """Decorator to ensure user is a teacher."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        
        # Check if user has teacher profile or is linked to a teacher
        teacher = None
        if hasattr(request.user, 'teacherprofile'):
            teacher = request.user.teacherprofile.teacher
        else:
            # Check if user is linked to a Teacher model via email
            try:
                teacher = Teacher.objects.get(email=request.user.email, is_active=True)
            except Teacher.DoesNotExist:
                pass
        
        if not teacher:
            messages.error(request, 'Access denied. Teacher account required.')
            return redirect('landing')
        
        # Add teacher to request for easy access
        request.teacher = teacher
        return view_func(request, *args, **kwargs)
    return wrapper

@login_required
@teacher_required
def teacher_dashboard(request):
    """Teacher dashboard with overview of classes and responsibilities."""
    teacher = request.teacher
    
    # Get teacher's assigned subjects
    teacher_subjects = TeacherSubject.objects.filter(
        teacher=teacher,
        is_active=True
    ).select_related('subject', 'subject__course')
    
    # Get today's classes
    today = timezone.now().date()
    today_weekday = today.weekday()  # Monday is 0
    
    today_classes = TimetableEntry.objects.filter(
        teacher=teacher,
        is_active=True,
        day_of_week=today_weekday
    ).select_related('subject', 'time_slot', 'room').order_by('time_slot__start_time')
    
    # Get upcoming classes (next 7 days)
    upcoming_classes = TimetableEntry.objects.filter(
        teacher=teacher,
        is_active=True
    ).select_related('subject', 'time_slot', 'room').order_by('day_of_week', 'time_slot__start_time')[:10]
    
    # Get students count across all classes
    total_students = Enrollment.objects.filter(
        subject__teachersubject__teacher=teacher,
        subject__teachersubject__is_active=True,
        is_active=True
    ).values('student').distinct().count()
    
    # Get pending assignments/materials to upload
    pending_materials = StudyMaterial.objects.filter(
        uploaded_by=request.user,
        is_published=False
    ).count()
    
    # Recent announcements by teacher
    recent_announcements = Announcement.objects.filter(
        posted_by=request.user,
        is_active=True
    ).order_by('-created_at')[:5]
    
    # Attendance statistics for current month
    current_month = timezone.now().replace(day=1)
    monthly_attendance = Attendance.objects.filter(
        timetable_entry__teacher=teacher,
        date__gte=current_month
    ).count()
    
    context = {
        'teacher': teacher,
        'teacher_subjects': teacher_subjects,
        'today_classes': today_classes,
        'upcoming_classes': upcoming_classes,
        'total_students': total_students,
        'pending_materials': pending_materials,
        'recent_announcements': recent_announcements,
        'monthly_attendance': monthly_attendance,
        'today': today
    }
    
    return render(request, 'teacher/dashboard.html', context)

@login_required
@teacher_required
def teacher_timetable(request):
    """View teacher's complete timetable."""
    teacher = request.teacher
    
    # Get all timetable entries for the teacher
    timetable_entries = TimetableEntry.objects.filter(
        teacher=teacher,
        is_active=True
    ).select_related('subject', 'time_slot', 'room').order_by('day_of_week', 'time_slot__start_time')
    
    # Get all time slots for structure
    time_slots = TimeSlot.objects.filter(is_active=True).order_by('period_number')
    
    # Organize timetable by day and time
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    timetable_grid = {}
    
    for day_num, day_name in enumerate(days):
        timetable_grid[day_name] = {}
        for time_slot in time_slots:
            timetable_grid[day_name][time_slot.id] = None
    
    # Fill the grid with actual entries
    for entry in timetable_entries:
        day_name = days[entry.day_of_week]
        timetable_grid[day_name][entry.time_slot.id] = entry
    
    context = {
        'teacher': teacher,
        'timetable_grid': timetable_grid,
        'time_slots': time_slots,
        'days': days
    }
    
    return render(request, 'teacher/timetable.html', context)

@login_required
@teacher_required
def teacher_classes(request):
    """View all classes assigned to the teacher."""
    teacher = request.teacher
    
    # Get all timetable entries grouped by class
    timetable_entries = TimetableEntry.objects.filter(
        teacher=teacher,
        is_active=True
    ).select_related('subject', 'time_slot', 'room')
    
    # Group by course, year, section
    classes = {}
    for entry in timetable_entries:
        key = f"{entry.course}-{entry.year}-{entry.section}"
        if key not in classes:
            classes[key] = {
                'course': entry.course,
                'year': entry.year,
                'section': entry.section,
                'subjects': set(),
                'entries': []
            }
        classes[key]['subjects'].add(entry.subject)
        classes[key]['entries'].append(entry)
    
    # Get student counts for each class
    for class_key, class_data in classes.items():
        student_count = Enrollment.objects.filter(
            subject__in=class_data['subjects'],
            is_active=True
        ).values('student').distinct().count()
        class_data['student_count'] = student_count
    
    context = {
        'teacher': teacher,
        'classes': classes
    }
    
    return render(request, 'teacher/classes.html', context)

@login_required
@teacher_required
def teacher_students(request):
    """View all students in teacher's classes."""
    teacher = request.teacher
    course = request.GET.get('course', '')
    year = request.GET.get('year', '')
    section = request.GET.get('section', '')
    
    # Get students enrolled in teacher's subjects
    students_query = StudentProfile.objects.filter(
        enrollment__subject__teachersubject__teacher=teacher,
        enrollment__subject__teachersubject__is_active=True,
        enrollment__is_active=True
    ).select_related('user').distinct()
    
    # Apply filters if provided
    if course:
        students_query = students_query.filter(course=course)
    if year:
        students_query = students_query.filter(year=int(year))
    if section:
        students_query = students_query.filter(section=section)
    
    students = students_query.order_by('course', 'year', 'section', 'roll_number')
    
    # Get unique courses, years, sections for filters
    all_students = StudentProfile.objects.filter(
        enrollment__subject__teachersubject__teacher=teacher,
        enrollment__subject__teachersubject__is_active=True,
        enrollment__is_active=True
    ).distinct()
    
    courses = all_students.values_list('course', flat=True).distinct()
    years = all_students.values_list('year', flat=True).distinct()
    sections = all_students.values_list('section', flat=True).distinct()
    
    context = {
        'teacher': teacher,
        'students': students,
        'courses': courses,
        'years': sorted(years) if years else [],
        'sections': sections,
        'selected_course': course,
        'selected_year': year,
        'selected_section': section
    }
    
    return render(request, 'teacher/students.html', context)

@login_required
@teacher_required
def mark_attendance(request):
    """Mark attendance for students."""
    teacher = request.teacher
    
    if request.method == 'POST':
        timetable_entry_id = request.POST.get('timetable_entry_id')
        attendance_date = request.POST.get('date')
        
        try:
            timetable_entry = get_object_or_404(TimetableEntry, id=timetable_entry_id, teacher=teacher)
            
            # Get enrolled students for this subject
            enrolled_students = Enrollment.objects.filter(
                subject=timetable_entry.subject,
                is_active=True
            ).select_related('student', 'student__user')
            
            with transaction.atomic():
                for enrollment in enrolled_students:
                    student_id = str(enrollment.student.id)
                    status = request.POST.get(f'attendance_{student_id}', 'absent')
                    
                    # Create or update attendance record
                    attendance, created = Attendance.objects.get_or_create(
                        student=enrollment.student,
                        timetable_entry=timetable_entry,
                        date=attendance_date,
                        defaults={
                            'status': status,
                            'marked_by': request.user
                        }
                    )
                    
                    if not created:
                        attendance.status = status
                        attendance.marked_by = request.user
                        attendance.save()
            
            messages.success(request, 'Attendance marked successfully!')
            return redirect('mark_attendance')
            
        except Exception as e:
            messages.error(request, 'Failed to mark attendance.')
            return redirect('mark_attendance')
    
    # Get teacher's classes for today or selected date
    selected_date = request.GET.get('date', timezone.now().date().strftime('%Y-%m-%d'))
    selected_date_obj = datetime.strptime(selected_date, '%Y-%m-%d').date()
    weekday = selected_date_obj.weekday()
    
    # Get timetable entries for the selected day
    timetable_entries = TimetableEntry.objects.filter(
        teacher=teacher,
        is_active=True,
        day_of_week=weekday
    ).select_related('subject', 'time_slot', 'room').order_by('time_slot__start_time')
    
    # Get selected class details
    selected_entry_id = request.GET.get('class_id')
    selected_entry = None
    enrolled_students = []
    existing_attendance = {}
    
    if selected_entry_id:
        selected_entry = get_object_or_404(TimetableEntry, id=selected_entry_id, teacher=teacher)
        enrolled_students = Enrollment.objects.filter(
            subject=selected_entry.subject,
            is_active=True
        ).select_related('student', 'student__user').order_by('student__roll_number')
        
        # Get existing attendance for this date
        for enrollment in enrolled_students:
            try:
                attendance = Attendance.objects.get(
                    student=enrollment.student,
                    timetable_entry=selected_entry,
                    date=selected_date_obj
                )
                existing_attendance[enrollment.student.id] = attendance.status
            except Attendance.DoesNotExist:
                existing_attendance[enrollment.student.id] = 'present'  # Default
    
    context = {
        'teacher': teacher,
        'timetable_entries': timetable_entries,
        'selected_date': selected_date,
        'selected_entry': selected_entry,
        'enrolled_students': enrolled_students,
        'existing_attendance': existing_attendance
    }
    
    return render(request, 'teacher/mark_attendance.html', context)

@login_required
@teacher_required
def manage_materials(request):
    """Manage study materials and assignments."""
    teacher = request.teacher
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add_material':
            try:
                StudyMaterial.objects.create(
                    title=request.POST.get('title'),
                    description=request.POST.get('description'),
                    subject_id=request.POST.get('subject_id'),
                    course=request.POST.get('course'),
                    year=int(request.POST.get('year')),
                    section=request.POST.get('section'),
                    material_type=request.POST.get('material_type', 'document'),
                    content=request.POST.get('content', ''),
                    file_url=request.POST.get('file_url', ''),
                    uploaded_by=request.user,
                    is_published=bool(request.POST.get('is_published'))
                )
                messages.success(request, 'Study material added successfully!')
            except Exception as e:
                messages.error(request, 'Failed to add study material.')
        
        elif action == 'add_assignment':
            try:
                Assignment.objects.create(
                    title=request.POST.get('title'),
                    description=request.POST.get('description'),
                    subject_id=request.POST.get('subject_id'),
                    course=request.POST.get('course'),
                    year=int(request.POST.get('year')),
                    section=request.POST.get('section'),
                    due_date=request.POST.get('due_date'),
                    max_marks=int(request.POST.get('max_marks', 100)),
                    instructions=request.POST.get('instructions', ''),
                    created_by=request.user,
                    is_published=bool(request.POST.get('is_published'))
                )
                messages.success(request, 'Assignment created successfully!')
            except Exception as e:
                messages.error(request, 'Failed to create assignment.')
        
        return redirect('manage_materials')
    
    # Get teacher's subjects
    teacher_subjects = TeacherSubject.objects.filter(
        teacher=teacher,
        is_active=True
    ).select_related('subject')
    
    # Get study materials uploaded by teacher
    materials = StudyMaterial.objects.filter(
        uploaded_by=request.user
    ).select_related('subject').order_by('-created_at')
    
    # Get assignments created by teacher
    assignments = Assignment.objects.filter(
        created_by=request.user
    ).select_related('subject').order_by('-created_at')
    
    context = {
        'teacher': teacher,
        'teacher_subjects': teacher_subjects,
        'materials': materials,
        'assignments': assignments
    }
    
    return render(request, 'teacher/manage_materials.html', context)

@login_required
@teacher_required
def teacher_announcements(request):
    """Manage teacher announcements."""
    teacher = request.teacher
    
    if request.method == 'POST':
        try:
            Announcement.objects.create(
                title=request.POST.get('title'),
                content=request.POST.get('content'),
                posted_by=request.user,
                target_audience=request.POST.get('target_audience', 'students'),
                target_course=request.POST.get('target_course', ''),
                target_year=int(request.POST.get('target_year', 0)) if request.POST.get('target_year') else None,
                target_section=request.POST.get('target_section', ''),
                is_urgent=bool(request.POST.get('is_urgent'))
            )
            messages.success(request, 'Announcement posted successfully!')
        except Exception as e:
            messages.error(request, 'Failed to post announcement.')
        
        return redirect('teacher_announcements')
    
    # Get teacher's announcements
    announcements = Announcement.objects.filter(
        posted_by=request.user,
        is_active=True
    ).order_by('-created_at')
    
    # Get unique courses, years, sections from teacher's classes
    timetable_entries = TimetableEntry.objects.filter(
        teacher=teacher,
        is_active=True
    ).values('course', 'year', 'section').distinct()
    
    courses = set()
    years = set()
    sections = set()
    
    for entry in timetable_entries:
        courses.add(entry['course'])
        years.add(entry['year'])
        sections.add(entry['section'])
    
    context = {
        'teacher': teacher,
        'announcements': announcements,
        'courses': sorted(courses),
        'years': sorted(years),
        'sections': sorted(sections)
    }
    
    return render(request, 'teacher/announcements.html', context)

@login_required
@teacher_required
def attendance_reports(request):
    """View attendance reports for teacher's classes."""
    teacher = request.teacher
    
    # Get filters
    course = request.GET.get('course', '')
    year = request.GET.get('year', '')
    section = request.GET.get('section', '')
    subject_id = request.GET.get('subject', '')
    
    # Base query for attendance
    attendance_query = Attendance.objects.filter(
        timetable_entry__teacher=teacher
    ).select_related('student', 'student__user', 'timetable_entry__subject')
    
    # Apply filters
    if course:
        attendance_query = attendance_query.filter(timetable_entry__course=course)
    if year:
        attendance_query = attendance_query.filter(timetable_entry__year=int(year))
    if section:
        attendance_query = attendance_query.filter(timetable_entry__section=section)
    if subject_id:
        attendance_query = attendance_query.filter(timetable_entry__subject_id=subject_id)
    
    # Get attendance statistics
    total_classes = attendance_query.count()
    present_count = attendance_query.filter(status='present').count()
    attendance_percentage = (present_count / total_classes * 100) if total_classes > 0 else 0
    
    # Get recent attendance records
    recent_attendance = attendance_query.order_by('-date', '-created_at')[:50]
    
    # Get student-wise attendance summary
    from django.db.models import Count, Case, When, IntegerField
    student_attendance = attendance_query.values(
        'student_id', 'student__roll_number', 'student__user__first_name', 'student__user__last_name'
    ).annotate(
        total_classes=Count('id'),
        present_classes=Count(Case(When(status='present', then=1), output_field=IntegerField())),
        absent_classes=Count(Case(When(status='absent', then=1), output_field=IntegerField())),
        late_classes=Count(Case(When(status='late', then=1), output_field=IntegerField()))
    ).order_by('-present_classes')
    
    # Calculate percentage for each student
    for student in student_attendance:
        student['attendance_percentage'] = (
            student['present_classes'] / student['total_classes'] * 100
        ) if student['total_classes'] > 0 else 0
    
    # Get filter options
    teacher_subjects = TeacherSubject.objects.filter(
        teacher=teacher,
        is_active=True
    ).select_related('subject')
    
    timetable_entries = TimetableEntry.objects.filter(
        teacher=teacher,
        is_active=True
    ).values('course', 'year', 'section').distinct()
    
    courses = set()
    years = set()
    sections = set()
    
    for entry in timetable_entries:
        courses.add(entry['course'])
        years.add(entry['year'])
        sections.add(entry['section'])
    
    context = {
        'teacher': teacher,
        'total_classes': total_classes,
        'present_count': present_count,
        'attendance_percentage': round(attendance_percentage, 1),
        'recent_attendance': recent_attendance,
        'student_attendance': student_attendance,
        'teacher_subjects': teacher_subjects,
        'courses': sorted(courses),
        'years': sorted(years),
        'sections': sorted(sections),
        'selected_course': course,
        'selected_year': year,
        'selected_section': section,
        'selected_subject': subject_id
    }
    
    return render(request, 'teacher/attendance_reports.html', context)
