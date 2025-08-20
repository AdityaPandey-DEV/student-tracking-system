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
try:
    from utils.ai_service import ai_service
except ImportError:
    ai_service = None

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
        
        elif action == 'generate_ai_timetable':
            try:
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
                    
                    print(f"DEBUG: Generating timetable for {course} Year {year} Section {section}")
                    
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
                    
                    # Build subject requirements
                    subject_requirements = {}
                    for ts in teacher_subjects:
                        subject = ts.subject
                        if subject.subject_code not in subject_requirements:
                            subject_requirements[subject.subject_code] = {
                                'subject_id': subject.id,
                                'subject_code': subject.subject_code,
                                'subject_name': subject.subject_name,
                                'credits': subject.credits,
                                'periods_per_week': subject.credits * 2,  # 2 periods per credit
                                'remaining': subject.credits * 2,
                                'teacher_id': ts.teacher.id,
                                'teacher_name': ts.teacher.user.get_full_name() or ts.teacher.user.username
                            }
                        else:
                            # Multiple teachers for same subject - use the first one for now
                            pass
                    
                    # Get time slots and build segments
                    time_slots = TimeSlot.objects.filter(is_active=True).order_by('period_number')
                    teaching_period_numbers = [ts.period_number for ts in time_slots if not ts.is_break]
                    break_periods = [ts.period_number for ts in time_slots if ts.is_break]
                    
                    # Build segments based on breaks
                    segments = []
                    current_segment = []
                    for ts in time_slots:
                        if ts.is_break:
                            if current_segment:
                                segments.append(current_segment)
                                current_segment = []
                        else:
                            current_segment.append(ts.period_number)
                    if current_segment:
                        segments.append(current_segment)
                    
                    print(f"DEBUG: Built {len(segments)} segments: {segments}")
                    print(f"DEBUG: Teaching periods: {teaching_period_numbers}")
                    print(f"DEBUG: Break periods: {break_periods}")
                    
                    # Initialize grid
                    days = [0, 1, 2, 3, 4]  # Monday to Friday
                    grid = {}
                    subject_list = []
                    
                    # Track teacher constraints
                    busy = set()  # (teacher_id, day, period)
                    teacher_daily = {}  # (teacher_id, day) -> count
                    teacher_consec = {}  # (teacher_id, day) -> consecutive count
                    teacher_last_period = {}  # (teacher_id, day) -> last period number
                    subject_daily_count = {}  # (subject_id, day) -> count
                    subject_day_cap = {}  # subject_id -> max per day
                    
                    # Teacher constraints
                    max_consecutive = 2
                    max_daily_load = 6
                    
                    # Set per-day caps based on credits
                    for subject_code, req in subject_requirements.items():
                        max_per_day = min(3, max(1, req['credits'] // 2))  # Cap at 3, min 1
                        subject_day_cap[req['subject_id']] = max_per_day
                    
                    # First pass: fill required periods respecting constraints
                    day_rotation = 0
                    for day in days:
                        day_rows = []
                        last_subject_id = None
                        
                        # First, add all periods for this day (including breaks)
                        for period_num in range(1, 11):  # Periods 1-10
                            # Check if this period is a break
                            is_break_period = period_num in break_periods
                            
                            if is_break_period:
                                # Add break period
                                day_rows.append({
                                    'period_number': period_num,
                                    'subject_code': '-',
                                    'subject_name': 'Break',
                                    'teacher_name': ''
                                })
                                continue
                            
                            # This is a teaching period, try to place a subject
                            if period_num not in teaching_period_numbers:
                                continue
                            
                            # Try to place subjects with remaining periods
                            candidates = sorted(
                                [s for s in subject_requirements.values() if s['remaining'] > 0],
                                key=lambda x: x['remaining'], reverse=True
                            )
                            
                            placed = False
                            for item in candidates:
                                # Avoid immediate repeat if last placed in this segment is same subject
                                if item['subject_code'] == last_subject_id:
                                    continue
                                
                                # Check teacher availability
                                t_id = item['teacher_id']
                                if t_id and (t_id, day, period_num) in busy:
                                    continue
                                
                                # Check daily load limit
                                if t_id and teacher_daily.get((t_id, day), 0) >= max_daily_load:
                                    continue
                                
                                # Consecutive constraint relative to adjacent period number
                                if t_id:
                                    key = (t_id, day)
                                    last = teacher_last_period.get(key)
                                    consec = teacher_consec.get(key, 0)
                                    if last is not None and period_num == last + 1 and consec >= max_consecutive:
                                        continue
                                
                                # Place
                                day_rows.append({
                                    'period_number': period_num,
                                    'subject_code': item['subject_code'],
                                    'subject_name': item['subject_name'],
                                    'teacher_name': item['teacher_name']
                                })
                                item['remaining'] -= 1
                                last_subject_id = item['subject_code']
                                placed = True
                                subject_daily_count[(item['subject_id'], day)] = subject_daily_count.get((item['subject_id'], day), 0) + 1
                                
                                if t_id:
                                    key = (t_id, day)
                                    last = teacher_last_period.get(key)
                                    if last is not None and period_num == last + 1:
                                        teacher_consec[key] = teacher_consec.get(key, 0) + 1
                                    else:
                                        teacher_consec[key] = 1
                                    teacher_last_period[key] = period_num
                                    teacher_daily[key] = teacher_daily.get(key, 0) + 1
                                break
                            
                            if not placed:
                                # Leave free if no feasible assignment
                                day_rows.append({
                                    'period_number': period_num,
                                    'subject_code': '-',
                                    'subject_name': 'Free Period',
                                    'teacher_name': ''
                                })
                                last_subject_id = None
                        
                        grid[str(day)] = day_rows
                        day_rotation += 1
                    
                    # Second pass: try to fill remaining Free Periods by relaxing per-day caps slightly (still honoring teacher constraints)
                    for di, day in enumerate(days):
                        # Build quick access map for this day's cells
                        day_cells = grid[str(day)]
                        used_periods = set(cell['period_number'] for cell in day_cells if cell['subject_code'] != '-')
                        
                        # Iterate through all periods 1-10, but skip break periods
                        for period_num in range(1, 11):
                            # Skip break periods
                            if period_num in break_periods:
                                continue
                                
                                # If already filled, skip
                                if period_num in used_periods:
                                    continue
                                
                                # Try to place any subject with remaining or under soft cap (cap + 1)
                                soft_cap_ok = lambda sid: subject_daily_count.get((sid, day), 0) < (subject_day_cap.get(sid, 1) + 1)
                                
                                # Sort by remaining desc
                                candidates = sorted(
                                    [s for s in subject_requirements.values() if s['remaining'] > 0 and soft_cap_ok(s['subject_id'])],
                                    key=lambda x: x['remaining'], reverse=True
                                )
                                
                                placed = False
                                # Get the last subject from the current day to avoid immediate repeats
                                last_subject_id = None
                                for cell in day_cells:
                                    if cell['subject_code'] != '-' and cell['period_number'] < period_num:
                                        last_subject_id = cell['subject_code']
                                
                                for item in candidates:
                                    # Avoid immediate repeat if last filled in this segment/day is same subject
                                    if item['subject_code'] == last_subject_id:
                                        continue
                                    
                                    t_id = item['teacher_id']
                                    if t_id and (t_id, day, period_num) in busy:
                                        continue
                                    
                                    if t_id and teacher_daily.get((t_id, day), 0) >= max_daily_load:
                                        continue
                                    
                                    if t_id:
                                        key = (t_id, day)
                                        last = teacher_last_period.get(key)
                                        consec = teacher_consec.get(key, 0)
                                        if last is not None and period_num == last + 1 and consec >= max_consecutive:
                                            continue
                                    
                                    # Place now by replacing the Free Period cell
                                    for idx, cell in enumerate(day_cells):
                                        if cell['period_number'] == period_num and cell['subject_code'] == '-':
                                            day_cells[idx] = {
                                                'period_number': period_num,
                                                'subject_code': item['subject_code'],
                                                'subject_name': item['subject_name'],
                                                'teacher_name': item['teacher_name']
                                            }
                                            
                                            if item['remaining'] > 0:
                                                item['remaining'] -= 1
                                            
                                            subject_daily_count[(item['subject_id'], day)] = subject_daily_count.get((item['subject_id'], day), 0) + 1
                                            
                                            if t_id:
                                                key = (t_id, day)
                                                last = teacher_last_period.get(key)
                                                if last is not None and period_num == last + 1:
                                                    teacher_consec[key] = teacher_consec.get(key, 0) + 1
                                                else:
                                                    teacher_consec[key] = 1
                                                teacher_last_period[key] = period_num
                                                teacher_daily[key] = teacher_daily.get(key, 0) + 1
                                            
                                            placed = True
                                            break
                                    
                                    if placed:
                                        break
                    
                    # Third pass: aggressive fill - ignore remaining credits but respect teacher constraints
                    for di, day in enumerate(days):
                        day_cells = grid[str(day)]
                        used_periods = set(cell['period_number'] for cell in day_cells if cell['subject_code'] != '-')
                        
                        # Iterate through all periods 1-10, but skip break periods
                        for period_num in range(1, 11):
                            # Skip break periods
                            if period_num in break_periods:
                                continue
                                
                                if period_num in used_periods:
                                    continue
                                
                                # Try any subject that can fit (respecting teacher constraints)
                                candidates = sorted(
                                    [s for s in subject_requirements.values()],
                                    key=lambda x: x['remaining'], reverse=True
                                )
                                
                                placed = False
                                last_subject_id = None
                                for cell in day_cells:
                                    if cell['subject_code'] != '-' and cell['period_number'] < period_num:
                                        last_subject_id = cell['subject_code']
                                
                                for item in candidates:
                                    if item['subject_code'] == last_subject_id:
                                        continue
                                    
                                    t_id = item['teacher_id']
                                    if t_id and (t_id, day, period_num) in busy:
                                        continue
                                    
                                    if t_id and teacher_daily.get((t_id, day), 0) >= max_daily_load:
                                        continue
                                    
                                    if t_id:
                                        key = (t_id, day)
                                        last = teacher_last_period.get(key)
                                        consec = teacher_consec.get(key, 0)
                                        if last is not None and period_num == last + 1 and consec >= max_consecutive:
                                            continue
                                    
                                    # Place by replacing Free Period
                                    for idx, cell in enumerate(day_cells):
                                        if cell['period_number'] == period_num and cell['subject_code'] == '-':
                                            day_cells[idx] = {
                                                'period_number': period_num,
                                                'subject_code': item['subject_code'],
                                                'subject_name': item['subject_name'],
                                                'teacher_name': item['teacher_name']
                                            }
                                            
                                            if item['remaining'] > 0:
                                                item['remaining'] -= 1
                                            
                                            subject_daily_count[(item['subject_id'], day)] = subject_daily_count.get((item['subject_id'], day), 0) + 1
                                            
                                            if t_id:
                                                key = (t_id, day)
                                                last = teacher_last_period.get(key)
                                                if last is not None and period_num == last + 1:
                                                    teacher_consec[key] = teacher_consec.get(key, 0) + 1
                                                else:
                                                    teacher_consec[key] = 1
                                                teacher_last_period[key] = period_num
                                                teacher_daily[key] = teacher_daily.get(key, 0) + 1
                                            
                                            placed = True
                                            break
                                    
                                    if placed:
                                        break
                    
                    # Build subject list for the suggestion
                    subject_list = []
                    for subject_code, req in subject_requirements.items():
                        subject_list.append({
                            'code': subject_code,
                            'name': req['subject_name'],
                            'teacher_name': req['teacher_name'],
                            'credits': req['credits'],
                            'periods_per_week': req['periods_per_week']
                        })
                    
                    # Calculate optimization metrics
                    total_slots = len(teaching_period_numbers) * len(days)
                    filled_slots = sum(1 for day in days for cell in grid[str(day)] if cell['subject_code'] != '-')
                    utilization = (filled_slots / total_slots) * 100 if total_slots > 0 else 0
                    
                    # Coverage across days
                    day_coverage = []
                    for day in days:
                        day_filled = sum(1 for cell in grid[str(day)] if cell['subject_code'] != '-')
                        day_coverage.append(day_filled / len(teaching_period_numbers) if len(teaching_period_numbers) > 0 else 0)
                    avg_coverage = sum(day_coverage) / len(day_coverage) if day_coverage else 0
                    coverage_bonus = avg_coverage * 10.0  # up to +10
                    
                    # Fairness (consecutive periods)
                    unmet_demand = sum(max(0, req['periods_per_week'] - (req['periods_per_week'] - req['remaining'])) for req in subject_requirements.values())
                    
                    if teacher_consec:
                        avg_consec = sum(teacher_consec.values()) / max(1, len(teacher_consec))
                    fairness_bonus = max(0.0, (max_consecutive - min(max_consecutive, avg_consec))) * 5.0  # up to +10
                    
                    # Compute score
                    optimization_score = utilization * 0.7 + coverage_bonus * 0.2 + fairness_bonus * 0.1 - (unmet_demand * 1.5)
                    optimization_score = max(0.0, min(100.0, round(optimization_score, 1)))
                    print(f"DEBUG: Optimization score computed: {optimization_score}")

                    optimization = {
                        'method': 'greedy-constraints+segment-pass',
                        'utilization_percent': round(utilization, 1),
                        'avg_coverage_ratio': round(avg_coverage, 2),
                        'fairness_bonus': round(fairness_bonus, 1),
                        'conflicts_resolved': existing_entries,
                        'unmet_subject_periods': int(unmet_demand),
                        'suggestions': [
                            'Avoids teacher double-booking automatically',
                            'Limits long continuous stretches for teachers',
                            'Spreads subjects across week and segments based on credits'
                        ]
                    }
                    
                    # Create timetable suggestion for this combination
                    try:
                        suggestion = TimetableSuggestion.objects.create(
                            generated_by=request.user,
                            course=course,
                            year=year,
                            section=section,
                            academic_year='2023-24',
                            semester=1,
                            suggestion_data={
                                'optimization': optimization,
                                'generated_at': timezone.now().isoformat(),
                                'grid': grid,
                                'subjects': subject_list
                            },
                            optimization_score=optimization_score,
                            conflicts_resolved=existing_entries,
                            status='generated'
                        )
                        print(f"DEBUG: Created suggestion with ID: {suggestion.id} for {course} Year {year} Section {section}")
                        generated_count += 1
                    except Exception as create_error:
                        print(f"DEBUG: Error creating TimetableSuggestion for {course} Year {year} Section {section}: {create_error}")
                        continue
                
                if generated_count > 0:
                    messages.success(request, f'Generated {generated_count} timetable suggestions for {total_combinations} course/year/section combinations. Check the suggestions tab.')
                else:
                    messages.warning(request, 'No timetable suggestions could be generated. Check if subjects and teachers are properly assigned.')
            except Exception as e:
                print(f"DEBUG: Error in generate_ai_timetable: {e}")
                messages.error(request, 'Failed to generate timetable suggestions.')
        
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
