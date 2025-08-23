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
from ai_features.models import AlgorithmicTimetableSuggestion, TimetableConfiguration, PerformanceInsight, AIAnalyticsReport
try:
    from utils.algorithmic_timetable import TimetableGenerator, create_subject_requirements, validate_timetable_constraints
except ImportError:
    TimetableGenerator = None

def admin_required(view_func):
    """Decorator to ensure user is an admin."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not hasattr(request.user, 'adminprofile'):
            messages.error(request, 'Access denied. Admin account required.')
            return redirect('accounts:landing')
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
    optimization_suggestions = AlgorithmicTimetableSuggestion.objects.filter(
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
        'algorithmic_suggestions': optimization_suggestions
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
        
        return redirect('accounts:manage_courses')
    
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
        
        return redirect('accounts:manage_teachers')
    
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
                # Parse and validate inputs
                subject_id = int(request.POST.get('subject_id'))
                teacher_id = int(request.POST.get('teacher_id'))
                course_name = request.POST.get('course')
                year_val = int(request.POST.get('year'))
                section_val = (request.POST.get('section') or '').upper()
                day_of_week_val = int(request.POST.get('day_of_week'))
                time_slot_id = int(request.POST.get('time_slot_id'))
                room_id = int(request.POST.get('room_id'))
                academic_year_val = request.POST.get('academic_year', '2023-24')
                semester_val = int(request.POST.get('semester'))

                # Optional: prevent assigning classes during a break slot
                slot = get_object_or_404(TimeSlot, id=time_slot_id)
                if getattr(slot, 'is_break', False):
                    messages.error(request, 'Cannot create timetable entry in a break slot. Please select a teaching period.')
                    return redirect('accounts:manage_timetable')

                # Conflict checks within same academic year and semester
                base_filters = {
                    'day_of_week': day_of_week_val,
                    'time_slot_id': time_slot_id,
                    'academic_year': academic_year_val,
                    'semester': semester_val,
                    'is_active': True,
                }

                # Teacher conflict
                if TimetableEntry.objects.filter(**base_filters, teacher_id=teacher_id).exists():
                    messages.error(request, 'Conflict: The selected teacher is already assigned at this day and period.')
                    return redirect('accounts:manage_timetable')

                # Room conflict
                if TimetableEntry.objects.filter(**base_filters, room_id=room_id).exists():
                    messages.error(request, 'Conflict: The selected room is already occupied at this day and period.')
                    return redirect('accounts:manage_timetable')

                # Class (course/year/section) conflict
                if TimetableEntry.objects.filter(
                    **base_filters,
                    course=course_name,
                    year=year_val,
                    section=section_val,
                ).exists():
                    messages.error(request, 'Conflict: This class already has a subject scheduled at this day and period.')
                    return redirect('accounts:manage_timetable')

                # Create entry
                with transaction.atomic():
                    TimetableEntry.objects.create(
                        subject_id=subject_id,
                        teacher_id=teacher_id,
                        course=course_name,
                        year=year_val,
                        section=section_val,
                        day_of_week=day_of_week_val,
                        time_slot_id=time_slot_id,
                        room_id=room_id,
                        academic_year=academic_year_val,
                        semester=semester_val,
                    )
                messages.success(request, 'Timetable entry added successfully!')
            except ValueError:
                messages.error(request, 'Invalid input: please ensure all fields are correctly filled.')
            except Exception as e:
                messages.error(request, f'Failed to add timetable entry: {str(e)}')
        
        elif action == 'generate_algorithmic_timetable':
            try:
                if not TimetableGenerator:
                    messages.error(request, 'Algorithmic timetable generator not available.')
                    return redirect('accounts:manage_timetable')
                
                # Get configuration
                config_name = request.POST.get('config_name', 'default')
                algorithm_type = request.POST.get('algorithm_type', 'constraint_satisfaction')
                
                # Get or create configuration
                config, created = TimetableConfiguration.objects.get_or_create(
                    name=config_name,
                    defaults={
                        'days_per_week': 5,
                        'periods_per_day': 8,
                        'period_duration': 50,
                        'break_periods': [3, 6],  # Break after 3rd and 6th period
                        'break_duration': 15,
                        'max_teacher_periods_per_day': 5,
                        'max_consecutive_periods': 2,
                        'max_subject_periods_per_day': 3,
                        'algorithm_type': algorithm_type,
                        'created_by': request.user
                    }
                )
                
                # Get all active course/year/section combinations
                all_combinations = TimetableEntry.objects.filter(
                    is_active=True
                ).values('course', 'year', 'section').distinct()
                
                if not all_combinations.exists():
                    messages.error(request, 'No existing timetable entries found. Please add some entries first.')
                    return redirect('accounts:manage_timetable')
                
                generated_count = 0
                total_combinations = len(all_combinations)
                
                for combo in all_combinations:
                    course = combo['course']
                    year = combo['year']
                    section = combo['section']
                    
                    print(f"DEBUG: Generating algorithmic timetable for {course} Year {year} Section {section}")
                    
                    # Get existing entries to resolve conflicts
                    existing_entries = TimetableEntry.objects.filter(
                        course=course, year=year, section=section, is_active=True
                    ).count()
                    
                    # Get subjects and teachers for this course/year
                    subjects = Subject.objects.filter(
                        course=course, year=year, is_active=True
                    ).select_related('course')
                    
                    teacher_subjects = TeacherSubject.objects.filter(
                        subject__course=course,
                        subject__year=year,
                        is_active=True
                    ).select_related('subject', 'teacher')
                    
                    if not subjects.exists():
                        print(f"DEBUG: No subjects found for {course} Year {year}, skipping...")
                        continue
                    
                    if not teacher_subjects.exists():
                        print(f"DEBUG: No teachers assigned to subjects for {course} Year {year}, skipping...")
                        continue
                    
                    # Build subject requirements for algorithmic solver
                    subject_requirements = []
                    for ts in teacher_subjects:
                        subject = ts.subject
                        requirement = {
                                'subject_id': subject.id,
                            'subject_code': subject.code,
                            'subject_name': subject.name,
                                'credits': subject.credits,
                                'periods_per_week': subject.credits * 2,  # 2 periods per credit
                                'teacher_id': ts.teacher.id,
                            'teacher_name': ts.teacher.name
                        }
                        subject_requirements.append(requirement)
                    
                    # Create algorithmic timetable generator
                    generator = TimetableGenerator(algorithm_type=algorithm_type)
                    
                    # Generate timetable using algorithm
                    result = generator.generate_timetable(
                        subjects=create_subject_requirements(subject_requirements),
                        days=config.days_per_week,
                        periods=config.periods_per_day,
                        break_periods=config.break_periods
                    )
                    
                    if not result['success']:
                        print(f"DEBUG: Algorithm failed for {course} Year {year} Section {section}: {result['error']}")
                        continue
                    
                    # Validate constraints
                    violations = validate_timetable_constraints(result['grid'], result['subjects'])
                    
                    # Create algorithmic timetable suggestion
                    try:
                        suggestion = AlgorithmicTimetableSuggestion.objects.create(
                            generated_by=request.user,
                            course=course,
                            year=year,
                            section=section,
                            academic_year='2023-24',
                            semester=1,
                            algorithm_type=algorithm_type,
                            max_periods_per_day=config.periods_per_day,
                            max_teacher_periods_per_day=config.max_teacher_periods_per_day,
                            max_consecutive_periods=config.max_consecutive_periods,
                            break_duration=config.break_duration,
                            suggestion_data={
                                'algorithm': algorithm_type,
                                'config': {
                                    'days_per_week': config.days_per_week,
                                    'periods_per_day': config.periods_per_day,
                                    'period_duration': config.period_duration,
                                    'break_periods': config.break_periods,
                                    'break_duration': config.break_duration
                                },
                                'generated_at': timezone.now().isoformat(),
                                'grid': result['grid'],
                                'subjects': result['subjects'],
                                'execution_time': result['execution_time'],
                                'constraint_violations': violations
                            },
                            optimization_score=result['optimization_score'],
                            conflicts_resolved=existing_entries,
                            constraint_violations=len(violations),
                            status='generated'
                        )
                        print(f"DEBUG: Created algorithmic suggestion with ID: {suggestion.id} for {course} Year {year} Section {section}")
                        generated_count += 1
                    except Exception as create_error:
                        print(f"DEBUG: Error creating AlgorithmicTimetableSuggestion for {course} Year {year} Section {section}: {create_error}")
                        continue
                
                if generated_count > 0:
                    messages.success(request, f'Generated {generated_count} algorithmic timetable suggestions for {total_combinations} course/year/section combinations using {algorithm_type} algorithm.')
                else:
                    messages.warning(request, 'No algorithmic timetable suggestions could be generated. Check if subjects and teachers are properly assigned.')
            except Exception as e:
                print(f"DEBUG: Error in generate_algorithmic_timetable: {e}")
                messages.error(request, f'Failed to generate algorithmic timetable suggestions: {str(e)}')
        
        return redirect('accounts:manage_timetable')
    
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
    
    # Get algorithmic suggestions
    algorithmic_suggestions = AlgorithmicTimetableSuggestion.objects.filter(
        status='generated'
    ).order_by('-created_at')[:5]
    
    # Get timetable configurations
    timetable_configs = TimetableConfiguration.objects.filter(is_active=True)
    
    context = {
        'courses': courses,
        'subjects': subjects,
        'teachers': teachers,
        'time_slots': time_slots,
        'rooms': rooms,
        'timetable_entries': timetable_entries,
        'algorithmic_suggestions': algorithmic_suggestions,
        'timetable_configs': timetable_configs,
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
                student = get_object_or_404(StudentProfile, pk=request.POST.get('student_id'))
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
                
                # Broadcast change to all connected users (for real-time sync)
                from django.core.cache import cache
                cache.set(f'user_updated_{user.id}', True, timeout=300)
                
                messages.success(request, f'Password reset for {user.username} successfully!')
            except Exception as e:
                messages.error(request, 'Failed to reset password.')
                
        elif action == 'toggle_student_status':
            try:
                student = get_object_or_404(StudentProfile, pk=request.POST.get('student_id'))
                student.user.is_active = not student.user.is_active
                student.user.save()
                
                # Broadcast change for real-time sync
                from django.core.cache import cache
                cache.set(f'student_status_updated_{student.pk}', True, timeout=300)
                
                status = 'activated' if student.user.is_active else 'deactivated'
                messages.success(request, f'Student {student.roll_number} {status} successfully!')
            except Exception as e:
                messages.error(request, 'Failed to update student status.')
        
        return redirect('accounts:manage_students')
    
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
        
        return redirect('accounts:manage_announcements')
    
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
def edit_announcement(request, announcement_id):
    """Edit an existing announcement."""
    announcement = get_object_or_404(Announcement, id=announcement_id)
    if request.method == 'POST':
        try:
            announcement.title = request.POST.get('title', announcement.title)
            announcement.content = request.POST.get('content', announcement.content)
            announcement.target_audience = request.POST.get('target_audience', announcement.target_audience)
            announcement.target_course = request.POST.get('target_course', announcement.target_course)
            target_year = request.POST.get('target_year')
            announcement.target_year = int(target_year) if target_year else None
            announcement.target_section = request.POST.get('target_section', announcement.target_section)
            announcement.is_urgent = bool(request.POST.get('is_urgent'))
            announcement.save()
            messages.success(request, 'Announcement updated successfully!')
            return redirect('accounts:manage_announcements')
        except Exception:
            messages.error(request, 'Failed to update announcement. Please check your inputs.')
    courses = Course.objects.filter(is_active=True)
    return render(request, 'admin/edit_announcement.html', {
        'announcement': announcement,
        'courses': courses,
    })

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
            if ai_service:
                analysis = ai_service.analyze_performance(performance_data)
            else:
                # Fallback analysis
                analysis = {
                    'overall_score': 75,
                    'strengths': ['Regular attendance', 'Good assignment completion'],
                    'areas_for_improvement': ['Exam performance', 'Participation']
                }
            
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
        
        return redirect('accounts:ai_analytics')
    
    # Get existing insights
    insights = PerformanceInsight.objects.filter(is_viewed=False).order_by('-created_at')[:10]
    
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

@login_required
@admin_required
def manage_timetable_configs(request):
    """Manage timetable configurations for algorithmic generation."""
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'create_config':
            try:
                name = request.POST.get('name')
                description = request.POST.get('description', '')
                days_per_week = int(request.POST.get('days_per_week', 5))
                periods_per_day = int(request.POST.get('periods_per_day', 8))
                period_duration = int(request.POST.get('period_duration', 50))
                break_periods = request.POST.get('break_periods', '').split(',') if request.POST.get('break_periods') else []
                break_duration = int(request.POST.get('break_duration', 15))
                max_teacher_periods_per_day = int(request.POST.get('max_teacher_periods_per_day', 5))
                max_consecutive_periods = int(request.POST.get('max_consecutive_periods', 2))
                max_subject_periods_per_day = int(request.POST.get('max_subject_periods_per_day', 3))
                algorithm_type = request.POST.get('algorithm_type', 'constraint_satisfaction')
                max_iterations = int(request.POST.get('max_iterations', 1000))
                timeout_seconds = int(request.POST.get('timeout_seconds', 30))
                
                # Convert break periods to integers
                break_periods = [int(p.strip()) for p in break_periods if p.strip().isdigit()]
                
                config = TimetableConfiguration.objects.create(
                    name=name,
                    description=description,
                    days_per_week=days_per_week,
                    periods_per_day=periods_per_day,
                    period_duration=period_duration,
                    break_periods=break_periods,
                    break_duration=break_duration,
                    max_teacher_periods_per_day=max_teacher_periods_per_day,
                    max_consecutive_periods=max_consecutive_periods,
                    max_subject_periods_per_day=max_subject_periods_per_day,
                    algorithm_type=algorithm_type,
                    max_iterations=max_iterations,
                    timeout_seconds=timeout_seconds,
                    created_by=request.user
                )
                
                messages.success(request, f'Timetable configuration "{name}" created successfully!')
                return redirect('accounts:manage_timetable_configs')
                
            except Exception as e:
                messages.error(request, f'Failed to create configuration: {str(e)}')
        
        elif action == 'update_config':
            try:
                config_id = int(request.POST.get('config_id'))
                config = get_object_or_404(TimetableConfiguration, id=config_id)
                
                config.name = request.POST.get('name', config.name)
                config.description = request.POST.get('description', config.description)
                config.days_per_week = int(request.POST.get('days_per_week', config.days_per_week))
                config.periods_per_day = int(request.POST.get('periods_per_day', config.periods_per_day))
                config.period_duration = int(request.POST.get('period_duration', config.period_duration))
                config.break_duration = int(request.POST.get('break_duration', config.break_duration))
                config.max_teacher_periods_per_day = int(request.POST.get('max_teacher_periods_per_day', config.max_teacher_periods_per_day))
                config.max_consecutive_periods = int(request.POST.get('max_consecutive_periods', config.max_consecutive_periods))
                config.max_subject_periods_per_day = int(request.POST.get('max_subject_periods_per_day', config.max_subject_periods_per_day))
                config.algorithm_type = request.POST.get('algorithm_type', config.algorithm_type)
                config.max_iterations = int(request.POST.get('max_iterations', config.max_iterations))
                config.timeout_seconds = int(request.POST.get('timeout_seconds', config.timeout_seconds))
                
                # Handle break periods
                break_periods_str = request.POST.get('break_periods', '')
                if break_periods_str:
                    break_periods = [int(p.strip()) for p in break_periods_str.split(',') if p.strip().isdigit()]
                    config.break_periods = break_periods
                
                config.save()
                messages.success(request, f'Configuration "{config.name}" updated successfully!')
                return redirect('accounts:manage_timetable_configs')
                
            except Exception as e:
                messages.error(request, f'Failed to update configuration: {str(e)}')
        
        elif action == 'delete_config':
            try:
                config_id = int(request.POST.get('config_id'))
                config = get_object_or_404(TimetableConfiguration, id=config_id)
                config_name = config.name
                config.delete()
                messages.success(request, f'Configuration "{config_name}" deleted successfully!')
                return redirect('accounts:manage_timetable_configs')
                
            except Exception as e:
                messages.error(request, f'Failed to delete configuration: {str(e)}')
        
        elif action == 'toggle_config':
            try:
                config_id = int(request.POST.get('config_id'))
                config = get_object_or_404(TimetableConfiguration, id=config_id)
                config.is_active = not config.is_active
                config.save()
                status = 'activated' if config.is_active else 'deactivated'
                messages.success(request, f'Configuration "{config.name}" {status} successfully!')
                return redirect('accounts:manage_timetable_configs')
                
            except Exception as e:
                messages.error(request, f'Failed to toggle configuration: {str(e)}')
    
    # Get all configurations
    configs = TimetableConfiguration.objects.all().order_by('-created_at')
    
    context = {
        'configs': configs,
        'algorithm_choices': AlgorithmicTimetableSuggestion.ALGORITHM_CHOICES
    }
    
    return render(request, 'admin/manage_timetable_configs.html', context)
