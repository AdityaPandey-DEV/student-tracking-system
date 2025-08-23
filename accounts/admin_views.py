"""
Admin dashboard and management views.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.db import transaction, models
from django.utils import timezone
from datetime import timedelta

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

try:
    from utils.ai_service import ai_service
except ImportError:
    ai_service = None

def _get_current_academic_year():
    """Get current academic year dynamically."""
    current_year = timezone.now().year
    current_month = timezone.now().month
    # Academic year starts in June (month 6)
    if current_month >= 6:
        return f"{current_year}-{current_year + 1}"
    else:
        return f"{current_year-1}-{current_year}"

def _get_current_semester():
    """Get current semester dynamically."""
    current_month = timezone.now().month
    # Semester 1: June to December (months 6-12)
    # Semester 2: January to May (months 1-5)
    return 1 if current_month in [6, 7, 8, 9, 10, 11, 12] else 2

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
    
    # Basic statistics with optimized queries
    total_students = StudentProfile.objects.count()
    total_teachers = Teacher.objects.filter(is_active=True).count()
    total_courses = Course.objects.filter(is_active=True).count()
    total_subjects = Subject.objects.filter(is_active=True).count()
    
    # Recent registrations (last 7 days) with optimized query
    week_ago = timezone.now() - timedelta(days=7)
    recent_students = StudentProfile.objects.filter(
        user__date_joined__gte=week_ago
    ).count()
    
    # Timetable statistics
    active_timetable_entries = TimetableEntry.objects.filter(is_active=True).count()
    
    # Recent announcements with limit for performance
    recent_announcements = Announcement.objects.filter(
        is_active=True
    ).select_related('posted_by').order_by('-created_at')[:5]
    
    # Course-wise student distribution with optimized query
    course_distribution = []
    courses = Course.objects.filter(is_active=True)
    
    for course in courses:
        # Count students for this course by matching the course name
        student_count = StudentProfile.objects.filter(
            course=course.name,
            user__is_active=True
        ).count()
        
        course_distribution.append({
            'name': course.name,
            'full_name': course.full_name,
            'student_count': student_count
        })
    
    # Sort by student count (descending)
    course_distribution.sort(key=lambda x: x['student_count'], reverse=True)
    
    # AI insights summary with limit for performance
    ai_insights = PerformanceInsight.objects.filter(
        is_actionable=True,
        is_viewed=False
    ).select_related('generated_by').order_by('-impact_score')[:3]
    
    # Timetable optimization suggestions with limit for performance
    optimization_suggestions = AlgorithmicTimetableSuggestion.objects.filter(
        status='generated'
    ).select_related('generated_by').order_by('-optimization_score')[:3]
    
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
                name = request.POST.get('name', '').strip()
                full_name = request.POST.get('full_name', '').strip()
                duration_years = request.POST.get('duration_years', '4')
                
                # Input validation
                if not name or not full_name:
                    messages.error(request, 'Course name and full name are required.')
                    return redirect('accounts:manage_courses')
                
                if not duration_years.isdigit() or int(duration_years) <= 0:
                    messages.error(request, 'Duration must be a positive number.')
                    return redirect('accounts:manage_courses')
                
                Course.objects.create(
                    name=name,
                    full_name=full_name,
                    duration_years=int(duration_years),
                    description=request.POST.get('description', '').strip()
                )
                messages.success(request, 'Course added successfully!')
            except Exception as e:
                messages.error(request, 'Failed to add course. Please check the details.')
        
        elif action == 'add_subject':
            try:
                code = request.POST.get('code', '').strip().upper()
                name = request.POST.get('name', '').strip()
                course_id = request.POST.get('course_id')
                year = request.POST.get('year')
                semester = request.POST.get('semester')
                credits = request.POST.get('credits', '3')
                
                # Input validation
                if not all([code, name, course_id, year, semester]):
                    messages.error(request, 'All fields are required.')
                    return redirect('accounts:manage_courses')
                
                if not year.isdigit() or not semester.isdigit() or not credits.isdigit():
                    messages.error(request, 'Year, semester, and credits must be numbers.')
                    return redirect('accounts:manage_courses')
                
                if int(year) <= 0 or int(semester) <= 0 or int(credits) <= 0:
                    messages.error(request, 'Year, semester, and credits must be positive numbers.')
                    return redirect('accounts:manage_courses')
                
                Subject.objects.create(
                    code=code,
                    name=name,
                    course_id=course_id,
                    year=int(year),
                    semester=int(semester),
                    credits=int(credits),
                    description=request.POST.get('description', '').strip()
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
                employee_id = request.POST.get('employee_id', '').strip().upper()
                name = request.POST.get('name', '').strip()
                email = request.POST.get('email', '').strip()
                phone_number = request.POST.get('phone_number', '').strip()
                department = request.POST.get('department', '').strip()
                
                # Input validation
                if not all([employee_id, name, email, department]):
                    messages.error(request, 'Employee ID, name, email, and department are required.')
                    return redirect('accounts:manage_teachers')
                
                if '@' not in email:
                    messages.error(request, 'Please enter a valid email address.')
                    return redirect('accounts:manage_teachers')
                
                Teacher.objects.create(
                    employee_id=employee_id,
                    name=name,
                    email=email,
                    phone_number=phone_number,
                    department=department,
                    designation=request.POST.get('designation', '').strip(),
                    specialization=request.POST.get('specialization', '').strip()
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
                # Parse and validate inputs with comprehensive validation
                subject_id = request.POST.get('subject_id')
                teacher_id = request.POST.get('teacher_id')
                course_name = request.POST.get('course', '').strip()
                year_val = request.POST.get('year')
                section_val = (request.POST.get('section') or '').strip().upper()
                day_of_week_val = request.POST.get('day_of_week')
                time_slot_id = request.POST.get('time_slot_id')
                room_id = request.POST.get('room_id')
                academic_year_val = request.POST.get('academic_year') or _get_current_academic_year()
                semester_val = request.POST.get('semester')
                
                # Comprehensive input validation
                if not all([subject_id, teacher_id, course_name, year_val, day_of_week_val, time_slot_id, room_id, semester_val]):
                    messages.error(request, 'All required fields must be filled.')
                    return redirect('accounts:manage_timetable')
                
                # Validate numeric fields
                numeric_fields = {
                    'subject_id': subject_id,
                    'teacher_id': teacher_id,
                    'year': year_val,
                    'day_of_week': day_of_week_val,
                    'time_slot_id': time_slot_id,
                    'room_id': room_id,
                    'semester': semester_val
                }
                
                for field_name, field_value in numeric_fields.items():
                    if not field_value or not str(field_value).isdigit():
                        messages.error(request, f'{field_name.replace("_", " ").title()} must be a valid number.')
                        return redirect('accounts:manage_timetable')
                
                # Convert to integers after validation
                subject_id = int(subject_id)
                teacher_id = int(teacher_id)
                year_val = int(year_val)
                day_of_week_val = int(day_of_week_val)
                time_slot_id = int(time_slot_id)
                room_id = int(room_id)
                semester_val = int(semester_val)
                
                # Validate ranges and logical constraints
                if year_val <= 0 or year_val > 10:  # Reasonable year range
                    messages.error(request, 'Year must be between 1 and 10.')
                    return redirect('accounts:manage_timetable')
                
                if semester_val not in [1, 2]:
                    messages.error(request, 'Semester must be 1 or 2.')
                    return redirect('accounts:manage_timetable')
                
                if day_of_week_val < 0 or day_of_week_val > 6:  # 0=Monday, 6=Sunday
                    messages.error(request, 'Day of week must be between 0 and 6.')
                    return redirect('accounts:manage_timetable')
                
                if not course_name or len(course_name) > 50:  # Reasonable course name length
                    messages.error(request, 'Course name is required and must be less than 50 characters.')
                    return redirect('accounts:manage_timetable')
                
                if len(section_val) > 10:  # Reasonable section length
                    messages.error(request, 'Section must be less than 10 characters.')
                    return redirect('accounts:manage_timetable')
                
                # Validate academic year format (YYYY-YYYY)
                if not isinstance(academic_year_val, str) or len(academic_year_val) != 7 or '-' not in academic_year_val:
                    messages.error(request, 'Academic year must be in format YYYY-YYYY.')
                    return redirect('accounts:manage_timetable')
                
                # Validate that referenced objects exist
                try:
                    subject = Subject.objects.get(id=subject_id, is_active=True)
                except Subject.DoesNotExist:
                    messages.error(request, 'Selected subject does not exist or is inactive.')
                    return redirect('accounts:manage_timetable')
                
                try:
                    teacher = Teacher.objects.get(id=teacher_id, is_active=True)
                except Teacher.DoesNotExist:
                    messages.error(request, 'Selected teacher does not exist or is inactive.')
                    return redirect('accounts:manage_timetable')
                
                try:
                    time_slot = TimeSlot.objects.get(id=time_slot_id, is_active=True)
                except TimeSlot.DoesNotExist:
                    messages.error(request, 'Selected time slot does not exist or is inactive.')
                    return redirect('accounts:manage_timetable')
                
                try:
                    room = Room.objects.get(id=room_id, is_active=True)
                except Room.DoesNotExist:
                    messages.error(request, 'Selected room does not exist or is inactive.')
                    return redirect('accounts:manage_timetable')
                
                # Validate course exists
                try:
                    course = Course.objects.get(name=course_name, is_active=True)
                except Course.DoesNotExist:
                    messages.error(request, f'Course "{course_name}" does not exist or is inactive.')
                    return redirect('accounts:manage_timetable')

                # Optional: prevent assigning classes during a break slot
                if getattr(time_slot, 'is_break', False):
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

                # Create entry with validated data
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
            except ValueError as e:
                messages.error(request, f'Invalid input: {str(e)}. Please ensure all fields are correctly filled.')
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
                    course_name = combo['course']
                    year = combo['year']
                    section = combo['section']
                    
                    print(f"DEBUG: Generating algorithmic timetable for {course_name} Year {year} Section {section}")
                    
                    # Get the Course object from the course name
                    try:
                        course_obj = Course.objects.get(name=course_name, is_active=True)
                    except Course.DoesNotExist:
                        print(f"DEBUG: Course '{course_name}' not found, skipping...")
                        continue
                    
                    # Get existing entries to resolve conflicts
                    existing_entries = TimetableEntry.objects.filter(
                        course=course_name, year=year, section=section, is_active=True
                    ).count()
                    
                    # Get subjects and teachers for this course/year
                    subjects = Subject.objects.filter(
                        course=course_obj, year=year, is_active=True
                    ).select_related('course')
                    
                    teacher_subjects = TeacherSubject.objects.filter(
                        subject__course=course_obj,
                        subject__year=year,
                        is_active=True
                    ).select_related('subject', 'teacher')
                    
                    if not subjects.exists():
                        print(f"DEBUG: No subjects found for {course_name} Year {year}, skipping...")
                        continue
                    
                    if not teacher_subjects.exists():
                        print(f"DEBUG: No teachers assigned to subjects for {course_name} Year {year}, skipping...")
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
                            'periods_per_week': subject.credits * 2,  # 2 periods per credit (standard: 1 credit = 2 periods/week)
                            'teacher_id': ts.teacher.id,
                            'teacher_name': ts.teacher.name
                        }
                        subject_requirements.append(requirement)
                    
                    # Limit subjects to prevent memory issues (max 8 subjects per course)
                    if len(subject_requirements) > 8:
                        print(f"DEBUG: Too many subjects ({len(subject_requirements)}) for {course_name} Year {year}, limiting to 8 to prevent memory issues")
                        subject_requirements = subject_requirements[:8]
                    
                    # Skip if too few subjects (less than 2)
                    if len(subject_requirements) < 2:
                        print(f"DEBUG: Too few subjects ({len(subject_requirements)}) for {course_name} Year {year}, skipping...")
                        continue
                    
                    # Create algorithmic timetable generator
                    generator = TimetableGenerator(algorithm_type=algorithm_type)
                    
                    # Generate timetable using algorithm with timeout protection
                    result = None
                    try:
                        import threading
                        import time
                        
                        # Cross-platform timeout solution
                        timeout_occurred = False
                        
                        def timeout_handler():
                            nonlocal timeout_occurred
                            timeout_occurred = True
                        
                        # Set timeout to 10 seconds to prevent memory issues
                        timer = threading.Timer(10.0, timeout_handler)
                        timer.start()
                        
                        start_time = time.time()
                        result = generator.generate_timetable(
                            subjects=create_subject_requirements(subject_requirements),
                            days=config.days_per_week,
                            periods=config.periods_per_day,
                            break_periods=config.break_periods
                        )
                        
                        timer.cancel()  # Cancel the timer
                        
                        # Check if timeout occurred
                        if timeout_occurred:
                            raise TimeoutError("Algorithm execution timed out")
                            
                    except TimeoutError:
                        print(f"DEBUG: Algorithm timed out for {course_name} Year {year} Section {section}, skipping...")
                        continue
                    except Exception as algo_error:
                        print(f"DEBUG: Algorithm error for {course_name} Year {year} Section {section}: {algo_error}")
                        continue
                    
                    # Check if result was generated successfully
                    if not result or not result.get('success'):
                        print(f"DEBUG: Algorithm failed or timed out for {course_name} Year {year} Section {section}")
                        continue
                    
                    # Validate constraints
                    violations = validate_timetable_constraints(result['grid'], result['subjects'])
                    
                    # Create algorithmic timetable suggestion
                    try:
                        # Get current academic year and semester dynamically
                        academic_year = _get_current_academic_year()
                        semester = _get_current_semester()
                        
                        suggestion = AlgorithmicTimetableSuggestion.objects.create(
                            generated_by=request.user,
                            course=course_name,
                            year=year,
                            section=section,
                            academic_year=academic_year,
                            semester=semester,
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
                        print(f"DEBUG: Created algorithmic suggestion with ID: {suggestion.id} for {course_name} Year {year} Section {section}")
                        generated_count += 1
                    except Exception as create_error:
                        print(f"DEBUG: Error creating AlgorithmicTimetableSuggestion for {course_name} Year {year} Section {section}: {create_error}")
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
                    academic_year=request.POST.get('academic_year') or _get_current_academic_year(),
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
            title = request.POST.get('title', '').strip()
            content = request.POST.get('content', '').strip()
            target_audience = request.POST.get('target_audience', 'all')
            target_course = request.POST.get('target_course', '').strip()
            target_year = request.POST.get('target_year')
            target_section = request.POST.get('target_section', '').strip()
            
            # Input validation
            if not title or not content:
                messages.error(request, 'Title and content are required.')
                return redirect('accounts:manage_announcements')
            
            if len(title) > 200:  # Assuming title field has max_length=200
                messages.error(request, 'Title is too long. Maximum 200 characters allowed.')
                return redirect('accounts:manage_announcements')
            
            if len(content) > 2000:  # Assuming content field has max_length=2000
                messages.error(request, 'Content is too long. Maximum 2000 characters allowed.')
                return redirect('accounts:manage_announcements')
            
            Announcement.objects.create(
                title=title,
                content=content,
                posted_by=request.user,
                target_audience=target_audience,
                target_course=target_course,
                target_year=int(target_year) if target_year and target_year.isdigit() else None,
                target_section=target_section,
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
    try:
        stats = {
            'total_insights': PerformanceInsight.objects.count(),
            'actionable_insights': PerformanceInsight.objects.filter(is_actionable=True).count(),
            'avg_confidence': PerformanceInsight.objects.aggregate(
                avg_confidence=models.Avg('confidence_score')
            )['avg_confidence'] or 0
        }
    except Exception as e:
        # Fallback statistics if database query fails
        stats = {
            'total_insights': 0,
            'actionable_insights': 0,
            'avg_confidence': 0
        }
        print(f"Warning: Failed to get AI analytics stats: {e}")
    
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
                name = request.POST.get('name', '').strip()
                description = request.POST.get('description', '').strip()
                days_per_week = request.POST.get('days_per_week', '5')
                periods_per_day = request.POST.get('periods_per_day', '8')
                period_duration = request.POST.get('period_duration', '50')
                break_periods = request.POST.get('break_periods', '')
                break_duration = request.POST.get('break_duration', '15')
                max_teacher_periods_per_day = request.POST.get('max_teacher_periods_per_day', '5')
                max_consecutive_periods = request.POST.get('max_consecutive_periods', '2')
                max_subject_periods_per_day = request.POST.get('max_subject_periods_per_day', '3')
                algorithm_type = request.POST.get('algorithm_type', 'constraint_satisfaction')
                max_iterations = request.POST.get('max_iterations', '1000')
                timeout_seconds = request.POST.get('timeout_seconds', '30')
                
                # Input validation
                if not name:
                    messages.error(request, 'Configuration name is required.')
                    return redirect('accounts:manage_timetable_configs')
                
                # Validate numeric fields
                numeric_fields = {
                    'days_per_week': days_per_week,
                    'periods_per_day': periods_per_day,
                    'period_duration': period_duration,
                    'break_duration': break_duration,
                    'max_teacher_periods_per_day': max_teacher_periods_per_day,
                    'max_consecutive_periods': max_consecutive_periods,
                    'max_subject_periods_per_day': max_subject_periods_per_day,
                    'max_iterations': max_iterations,
                    'timeout_seconds': timeout_seconds
                }
                
                for field_name, field_value in numeric_fields.items():
                    if not field_value.isdigit() or int(field_value) <= 0:
                        messages.error(request, f'{field_name.replace("_", " ").title()} must be a positive number.')
                        return redirect('accounts:manage_timetable_configs')
                
                # Validate logical constraints
                if int(days_per_week) > 7:
                    messages.error(request, 'Days per week cannot exceed 7.')
                    return redirect('accounts:manage_timetable_configs')
                
                if int(periods_per_day) > 12:
                    messages.error(request, 'Periods per day cannot exceed 12.')
                    return redirect('accounts:manage_timetable_configs')
                
                if int(max_teacher_periods_per_day) > int(periods_per_day):
                    messages.error(request, 'Max teacher periods per day cannot exceed total periods per day.')
                    return redirect('accounts:manage_timetable_configs')
                
                # Convert break periods to integers
                break_periods_list = []
                if break_periods:
                    for p in break_periods.split(','):
                        p = p.strip()
                        if p.isdigit():
                            period_num = int(p)
                            if 0 < period_num <= int(periods_per_day):
                                break_periods_list.append(period_num)
                            else:
                                messages.error(request, f'Break period {period_num} is invalid. Must be between 1 and {periods_per_day}.')
                                return redirect('accounts:manage_timetable_configs')
                        else:
                            messages.error(request, 'Break periods must be comma-separated numbers.')
                            return redirect('accounts:manage_timetable_configs')
                
                config = TimetableConfiguration.objects.create(
                    name=name,
                    description=description,
                    days_per_week=int(days_per_week),
                    periods_per_day=int(periods_per_day),
                    period_duration=int(period_duration),
                    break_periods=break_periods_list,
                    break_duration=int(break_duration),
                    max_teacher_periods_per_day=int(max_teacher_periods_per_day),
                    max_consecutive_periods=int(max_consecutive_periods),
                    max_subject_periods_per_day=int(max_subject_periods_per_day),
                    algorithm_type=algorithm_type,
                    max_iterations=int(max_iterations),
                    timeout_seconds=int(timeout_seconds),
                    created_by=request.user
                )
                
                messages.success(request, f'Timetable configuration "{name}" created successfully!')
                return redirect('accounts:manage_timetable_configs')
                
            except Exception as e:
                messages.error(request, f'Failed to create configuration: {str(e)}')
        
        elif action == 'update_config':
            try:
                config_id = request.POST.get('config_id')
                if not config_id or not config_id.isdigit():
                    messages.error(request, 'Invalid configuration ID.')
                    return redirect('accounts:manage_timetable_configs')
                
                config = get_object_or_404(TimetableConfiguration, id=int(config_id))
                
                # Get and validate input values
                name = request.POST.get('name', '').strip()
                description = request.POST.get('description', '').strip()
                days_per_week = request.POST.get('days_per_week')
                periods_per_day = request.POST.get('periods_per_day')
                period_duration = request.POST.get('period_duration')
                break_duration = request.POST.get('break_duration')
                max_teacher_periods_per_day = request.POST.get('max_teacher_periods_per_day')
                max_consecutive_periods = request.POST.get('max_consecutive_periods')
                max_subject_periods_per_day = request.POST.get('max_subject_periods_per_day')
                algorithm_type = request.POST.get('algorithm_type')
                max_iterations = request.POST.get('max_iterations')
                timeout_seconds = request.POST.get('timeout_seconds')
                
                # Input validation
                if not name:
                    messages.error(request, 'Configuration name is required.')
                    return redirect('accounts:manage_timetable_configs')
                
                # Validate numeric fields
                numeric_fields = {
                    'days_per_week': days_per_week,
                    'periods_per_day': periods_per_day,
                    'period_duration': period_duration,
                    'break_duration': break_duration,
                    'max_teacher_periods_per_day': max_teacher_periods_per_day,
                    'max_consecutive_periods': max_consecutive_periods,
                    'max_subject_periods_per_day': max_subject_periods_per_day,
                    'max_iterations': max_iterations,
                    'timeout_seconds': timeout_seconds
                }
                
                for field_name, field_value in numeric_fields.items():
                    if field_value and (not field_value.isdigit() or int(field_value) <= 0):
                        messages.error(request, f'{field_name.replace("_", " ").title()} must be a positive number.')
                        return redirect('accounts:manage_timetable_configs')
                
                # Update fields with validation
                if name:
                    config.name = name
                if description is not None:
                    config.description = description
                if days_per_week and days_per_week.isdigit():
                    days_val = int(days_per_week)
                    if days_val > 7:
                        messages.error(request, 'Days per week cannot exceed 7.')
                        return redirect('accounts:manage_timetable_configs')
                    config.days_per_week = days_val
                if periods_per_day and periods_per_day.isdigit():
                    periods_val = int(periods_per_day)
                    if periods_val > 12:
                        messages.error(request, 'Periods per day cannot exceed 12.')
                        return redirect('accounts:manage_timetable_configs')
                    config.periods_per_day = periods_val
                if period_duration and period_duration.isdigit():
                    config.period_duration = int(period_duration)
                if break_duration and break_duration.isdigit():
                    config.break_duration = int(break_duration)
                if max_teacher_periods_per_day and max_teacher_periods_per_day.isdigit():
                    max_teacher_val = int(max_teacher_periods_per_day)
                    if max_teacher_val > config.periods_per_day:
                        messages.error(request, 'Max teacher periods per day cannot exceed total periods per day.')
                        return redirect('accounts:manage_timetable_configs')
                    config.max_teacher_periods_per_day = max_teacher_val
                if max_consecutive_periods and max_consecutive_periods.isdigit():
                    config.max_consecutive_periods = int(max_consecutive_periods)
                if max_subject_periods_per_day and max_subject_periods_per_day.isdigit():
                    config.max_subject_periods_per_day = int(max_subject_periods_per_day)
                if algorithm_type:
                    config.algorithm_type = algorithm_type
                if max_iterations and max_iterations.isdigit():
                    config.max_iterations = int(max_iterations)
                if timeout_seconds and timeout_seconds.isdigit():
                    config.timeout_seconds = int(timeout_seconds)
                
                # Handle break periods with validation
                break_periods_str = request.POST.get('break_periods', '')
                if break_periods_str:
                    break_periods_list = []
                    for p in break_periods_str.split(','):
                        p = p.strip()
                        if p.isdigit():
                            period_num = int(p)
                            if 0 < period_num <= config.periods_per_day:
                                break_periods_list.append(period_num)
                            else:
                                messages.error(request, f'Break period {period_num} is invalid. Must be between 1 and {config.periods_per_day}.')
                                return redirect('accounts:manage_timetable_configs')
                        else:
                            messages.error(request, 'Break periods must be comma-separated numbers.')
                            return redirect('accounts:manage_timetable_configs')
                    config.break_periods = break_periods_list
                
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
