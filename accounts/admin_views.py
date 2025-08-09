"""
Admin dashboard and management views.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, Count, Avg
from django.db import transaction, models
from django.utils import timezone
from datetime import datetime, timedelta
import json

from accounts.models import User, StudentProfile, AdminProfile
from timetable.models import (
    Course, Subject, Teacher, TeacherSubject, TimeSlot, Room,
    TimetableEntry, Enrollment, Attendance, Announcement
)
from ai_features.models import TimetableSuggestion, PerformanceInsight, AIAnalyticsReport
from utils.ai_service import ai_service

def admin_required(view_func):
    """Decorator to ensure user is an admin."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not hasattr(request.user, 'adminprofile'):
            messages.error(request, 'Access denied. Admin account required.')
            return redirect('landing')
        return view_func(request, *args, **kwargs)
    return wrapper

@login_required
@admin_required
def admin_dashboard(request):
    """Admin dashboard with analytics and overview."""
    admin = request.user.adminprofile
    
    # Basic statistics
    total_students = StudentProfile.objects.count()
    total_teachers = Teacher.objects.filter(is_active=True).count()
    total_courses = Course.objects.filter(is_active=True).count()
    total_subjects = Subject.objects.filter(is_active=True).count()
    
    # Recent registrations (last 7 days)
    week_ago = timezone.now() - timedelta(days=7)
    recent_students = StudentProfile.objects.filter(
        user__date_joined__gte=week_ago
    ).count()
    
    # Timetable statistics
    active_timetable_entries = TimetableEntry.objects.filter(is_active=True).count()
    
    # Recent announcements
    recent_announcements = Announcement.objects.filter(
        is_active=True
    ).order_by('-created_at')[:5]
    
    # Course-wise student distribution
    # Since StudentProfile.course is a CharField, we need to group manually
    from django.db.models import Case, When, IntegerField
    
    course_distribution = []
    for course in Course.objects.filter(is_active=True):
        student_count = StudentProfile.objects.filter(
            course=course.name,
            user__is_active=True
        ).count()
        course_distribution.append({
            'name': course.name,
            'full_name': course.full_name,
            'student_count': student_count
        })
    
    # Sort by student count descending
    course_distribution = sorted(course_distribution, key=lambda x: x['student_count'], reverse=True)
    
    # AI insights summary
    ai_insights = PerformanceInsight.objects.filter(
        is_actionable=True,
        is_viewed=False
    ).order_by('-impact_score')[:3]
    
    # Timetable optimization suggestions
    optimization_suggestions = TimetableSuggestion.objects.filter(
        status='generated'
    ).order_by('-optimization_score')[:3]
    
    context = {
        'admin': admin,
        'total_students': total_students,
        'total_teachers': total_teachers,
        'total_courses': total_courses,
        'total_subjects': total_subjects,
        'recent_students': recent_students,
        'active_timetable_entries': active_timetable_entries,
        'recent_announcements': recent_announcements,
        'course_distribution': course_distribution,
        'ai_insights': ai_insights,
        'optimization_suggestions': optimization_suggestions
    }
    
    return render(request, 'admin/dashboard.html', context)

@login_required
@admin_required
def manage_courses(request):
    """Manage courses and subjects."""
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add_course':
            try:
                Course.objects.create(
                    name=request.POST.get('name'),
                    full_name=request.POST.get('full_name'),
                    duration_years=int(request.POST.get('duration_years', 4)),
                    description=request.POST.get('description', '')
                )
                messages.success(request, 'Course added successfully!')
            except Exception as e:
                messages.error(request, 'Failed to add course. Please check the details.')
        
        elif action == 'add_subject':
            try:
                Subject.objects.create(
                    code=request.POST.get('code').upper(),
                    name=request.POST.get('name'),
                    course_id=request.POST.get('course_id'),
                    year=int(request.POST.get('year')),
                    semester=int(request.POST.get('semester')),
                    credits=int(request.POST.get('credits', 3)),
                    description=request.POST.get('description', '')
                )
                messages.success(request, 'Subject added successfully!')
            except Exception as e:
                messages.error(request, 'Failed to add subject. Please check the details.')
        
        return redirect('manage_courses')
    
    courses = Course.objects.filter(is_active=True).order_by('name')
    subjects = Subject.objects.filter(is_active=True).select_related('course').order_by('course__name', 'year', 'semester')
    
    context = {
        'courses': courses,
        'subjects': subjects
    }
    
    return render(request, 'admin/manage_courses.html', context)

@login_required
@admin_required
def manage_teachers(request):
    """Manage teachers and their subject assignments."""
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add_teacher':
            try:
                Teacher.objects.create(
                    employee_id=request.POST.get('employee_id').upper(),
                    name=request.POST.get('name'),
                    email=request.POST.get('email'),
                    phone_number=request.POST.get('phone_number'),
                    department=request.POST.get('department'),
                    designation=request.POST.get('designation', ''),
                    specialization=request.POST.get('specialization', '')
                )
                messages.success(request, 'Teacher added successfully!')
            except Exception as e:
                messages.error(request, 'Failed to add teacher. Please check the details.')
        
        elif action == 'assign_subject':
            try:
                teacher = get_object_or_404(Teacher, id=request.POST.get('teacher_id'))
                subject = get_object_or_404(Subject, id=request.POST.get('subject_id'))
                
                TeacherSubject.objects.get_or_create(
                    teacher=teacher,
                    subject=subject,
                    defaults={'is_active': True}
                )
                messages.success(request, 'Subject assigned successfully!')
            except Exception as e:
                messages.error(request, 'Failed to assign subject.')
        
        return redirect('manage_teachers')
    
    teachers = Teacher.objects.filter(is_active=True).order_by('name')
    subjects = Subject.objects.filter(is_active=True).select_related('course').order_by('course__name', 'name')
    
    # Get teacher-subject assignments
    teacher_assignments = TeacherSubject.objects.filter(
        is_active=True
    ).select_related('teacher', 'subject', 'subject__course')
    
    context = {
        'teachers': teachers,
        'subjects': subjects,
        'teacher_assignments': teacher_assignments
    }
    
    return render(request, 'admin/manage_teachers.html', context)

@login_required
@admin_required
def manage_timetable(request):
    """Manage timetable entries."""
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'add_entry':
            try:
                with transaction.atomic():
                    TimetableEntry.objects.create(
                        subject_id=request.POST.get('subject_id'),
                        teacher_id=request.POST.get('teacher_id'),
                        course=request.POST.get('course'),
                        year=int(request.POST.get('year')),
                        section=request.POST.get('section').upper(),
                        day_of_week=int(request.POST.get('day_of_week')),
                        time_slot_id=request.POST.get('time_slot_id'),
                        room_id=request.POST.get('room_id'),
                        academic_year=request.POST.get('academic_year', '2023-24'),
                        semester=int(request.POST.get('semester'))
                    )
                messages.success(request, 'Timetable entry added successfully!')
            except Exception as e:
                messages.error(request, f'Failed to add timetable entry: {str(e)}')
        
        elif action == 'generate_ai_timetable':
            try:
                course = request.POST.get('course')
                year = int(request.POST.get('year'))
                section = request.POST.get('section')
                
                # Get existing timetable data
                existing_entries = TimetableEntry.objects.filter(
                    course=course,
                    year=year,
                    section=section,
                    is_active=True
                ).count()
                
                timetable_data = {
                    'course': course,
                    'year': year,
                    'section': section,
                    'conflicts': existing_entries,
                    'available_slots': list(range(1, 9))
                }
                
                # Generate AI optimization
                optimization = ai_service.optimize_timetable(timetable_data)
                
                # Create timetable suggestion
                TimetableSuggestion.objects.create(
                    generated_by=request.user,
                    course=course,
                    year=year,
                    section=section,
                    academic_year='2023-24',
                    semester=1,
                    suggestion_data={
                        'optimization': optimization,
                        'generated_at': timezone.now().isoformat()
                    },
                    optimization_score=optimization['optimization_score'],
                    status='generated'
                )
                
                messages.success(request, 'AI timetable optimization generated! Check the suggestions tab.')
            except Exception as e:
                messages.error(request, 'Failed to generate AI timetable.')
        
        return redirect('manage_timetable')
    
    # Get data for the form
    courses = Course.objects.filter(is_active=True)
    subjects = Subject.objects.filter(is_active=True).select_related('course')
    teachers = Teacher.objects.filter(is_active=True)
    time_slots = TimeSlot.objects.filter(is_active=True).order_by('period_number')
    rooms = Room.objects.filter(is_active=True)
    
    # Get existing timetable entries
    timetable_entries = TimetableEntry.objects.filter(
        is_active=True
    ).select_related('subject', 'teacher', 'time_slot', 'room').order_by(
        'course', 'year', 'section', 'day_of_week', 'time_slot__period_number'
    )
    
    # Get AI suggestions
    ai_suggestions = TimetableSuggestion.objects.filter(
        status='generated'
    ).order_by('-created_at')[:5]
    
    context = {
        'courses': courses,
        'subjects': subjects,
        'teachers': teachers,
        'time_slots': time_slots,
        'rooms': rooms,
        'timetable_entries': timetable_entries,
        'ai_suggestions': ai_suggestions,
        'days': [(i, day) for i, day in enumerate(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'])]
    }
    
    return render(request, 'admin/manage_timetable.html', context)

@login_required
@admin_required
def manage_students(request):
    """Manage students and enrollments."""
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'enroll_student':
            try:
                student = get_object_or_404(StudentProfile, id=request.POST.get('student_id'))
                subject = get_object_or_404(Subject, id=request.POST.get('subject_id'))
                
                Enrollment.objects.get_or_create(
                    student=student,
                    subject=subject,
                    academic_year=request.POST.get('academic_year', '2023-24'),
                    semester=int(request.POST.get('semester')),
                    defaults={'is_active': True}
                )
                messages.success(request, 'Student enrolled successfully!')
            except Exception as e:
                messages.error(request, 'Failed to enroll student.')
        
        elif action == 'reset_password':
            try:
                user = get_object_or_404(User, id=request.POST.get('user_id'))
                new_password = request.POST.get('new_password')
                
                user.set_password(new_password)
                user.save()
                
                messages.success(request, f'Password reset for {user.username} successfully!')
            except Exception as e:
                messages.error(request, 'Failed to reset password.')
        
        return redirect('manage_students')
    
    # Get students with search/filter
    students = StudentProfile.objects.select_related('user').order_by('course', 'year', 'section', 'roll_number')
    
    search_query = request.GET.get('search')
    if search_query:
        students = students.filter(
            Q(roll_number__icontains=search_query) |
            Q(user__first_name__icontains=search_query) |
            Q(user__last_name__icontains=search_query) |
            Q(course__icontains=search_query)
        )
    
    course_filter = request.GET.get('course')
    if course_filter:
        students = students.filter(course=course_filter)
    
    year_filter = request.GET.get('year')
    if year_filter:
        students = students.filter(year=year_filter)
    
    # Get subjects for enrollment
    subjects = Subject.objects.filter(is_active=True).select_related('course')
    
    # Get recent enrollments
    recent_enrollments = Enrollment.objects.filter(
        is_active=True
    ).select_related('student', 'subject').order_by('-enrolled_at')[:10]
    
    context = {
        'students': students[:50],  # Limit for performance
        'subjects': subjects,
        'recent_enrollments': recent_enrollments,
        'courses': Course.objects.filter(is_active=True),
        'search_query': search_query,
        'course_filter': course_filter,
        'year_filter': year_filter
    }
    
    return render(request, 'admin/manage_students.html', context)

@login_required
@admin_required
def manage_announcements(request):
    """Manage announcements."""
    
    if request.method == 'POST':
        try:
            Announcement.objects.create(
                title=request.POST.get('title'),
                content=request.POST.get('content'),
                posted_by=request.user,
                target_audience=request.POST.get('target_audience', 'all'),
                target_course=request.POST.get('target_course', ''),
                target_year=int(request.POST.get('target_year', 0)) if request.POST.get('target_year') else None,
                target_section=request.POST.get('target_section', ''),
                is_urgent=bool(request.POST.get('is_urgent'))
            )
            messages.success(request, 'Announcement posted successfully!')
        except Exception as e:
            messages.error(request, 'Failed to post announcement.')
        
        return redirect('manage_announcements')
    
    announcements = Announcement.objects.filter(
        is_active=True
    ).order_by('-created_at')
    
    courses = Course.objects.filter(is_active=True)
    
    context = {
        'announcements': announcements,
        'courses': courses
    }
    
    return render(request, 'admin/manage_announcements.html', context)

@login_required
@admin_required
def ai_analytics(request):
    """AI-powered analytics dashboard."""
    
    # Generate performance insights if requested
    if request.method == 'POST' and request.POST.get('action') == 'generate_insights':
        try:
            # Get performance data
            total_students = StudentProfile.objects.count()
            total_attendance = Attendance.objects.count()
            present_attendance = Attendance.objects.filter(status='present').count()
            
            performance_data = {
                'total_students': total_students,
                'attendance_trend': 'Stable',
                'assignment_completion': 85,
                'period': 'Current Semester',
                'subject_scores': {'Math': 78, 'Physics': 82, 'Chemistry': 75}
            }
            
            # Generate AI analysis
            analysis = ai_service.analyze_performance(performance_data)
            
            # Create performance insight
            PerformanceInsight.objects.create(
                title=f"Performance Analysis - {timezone.now().strftime('%B %Y')}",
                insight_type='performance_trend',
                scope='institution',
                description=f"Generated AI insights for institutional performance",
                insight_data=performance_data,
                confidence_score=analysis['overall_score'],
                impact_score=75,
                is_actionable=True,
                generated_by=request.user
            )
            
            messages.success(request, 'AI insights generated successfully!')
        except Exception as e:
            messages.error(request, 'Failed to generate insights.')
        
        return redirect('ai_analytics')
    
    # Get existing insights
    insights = PerformanceInsight.objects.all().order_by('-created_at')[:10]
    
    # Get analytics reports
    reports = AIAnalyticsReport.objects.filter(
        is_published=True
    ).order_by('-created_at')[:5]
    
    # Basic statistics for dashboard
    stats = {
        'total_insights': PerformanceInsight.objects.count(),
        'actionable_insights': PerformanceInsight.objects.filter(is_actionable=True).count(),
        'avg_confidence': PerformanceInsight.objects.aggregate(
            avg_confidence=models.Avg('confidence_score')
        )['avg_confidence'] or 0
    }
    
    context = {
        'insights': insights,
        'reports': reports,
        'stats': stats
    }
    
    return render(request, 'admin/ai_analytics.html', context)
