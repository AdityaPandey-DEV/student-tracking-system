"""
Student API views for real-time synchronization and AJAX functionality
"""

from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.core.cache import cache
from django.utils import timezone
from django.db.models import Q, Count, Avg
import json
from datetime import datetime, timedelta

from .models import User, StudentProfile
from timetable.models import (
    Course, Subject, Teacher, TeacherSubject, TimeSlot, Room,
    TimetableEntry, Enrollment, Attendance, Announcement
)
from ai_features.models import StudyMaterial, Assignment

def student_required_api(view_func):
    """Decorator to ensure user is a student for API calls."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'message': 'Authentication required'}, status=401)
        
        # Check if user has student profile
        student = None
        if hasattr(request.user, 'studentprofile'):
            student = request.user.studentprofile
        
        if not student:
            return JsonResponse({'success': False, 'message': 'Student access required'}, status=403)
        
        # Add student to request for easy access
        request.student = student
        return view_func(request, *args, **kwargs)
    return wrapper

@login_required
@student_required_api
@require_http_methods(["GET"])
def get_my_timetable(request):
    """Get student's personal timetable."""
    try:
        # Get student's enrolled subjects
        enrollments = Enrollment.objects.filter(
            student=request.student,
            is_active=True
        ).select_related('subject')
        
        enrolled_subjects = [enrollment.subject for enrollment in enrollments]
        
        # Get timetable entries for enrolled subjects
        timetable_entries = TimetableEntry.objects.filter(
            subject__in=enrolled_subjects,
            course=request.student.course,
            year=request.student.year,
            section=request.student.section,
            is_active=True
        ).select_related('subject', 'teacher', 'room', 'time_slot').order_by('day_of_week', 'time_slot__start_time')
        
        timetable_data = []
        for entry in timetable_entries:
            timetable_data.append({
                'id': entry.id,
                'subject': entry.subject.name,
                'subject_code': entry.subject.code,
                'teacher': entry.teacher.full_name,
                'room': entry.room.room_number,
                'day': entry.get_day_of_week_display(),
                'time': f"{entry.time_slot.start_time} - {entry.time_slot.end_time}",
                'period': entry.time_slot.period_number
            })
        
        return JsonResponse({
            'success': True, 
            'timetable': timetable_data,
            'student_info': {
                'name': request.user.get_full_name(),
                'roll_number': request.student.roll_number,
                'course': request.student.course,
                'year': request.student.year,
                'section': request.student.section
            }
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@login_required
@student_required_api
@require_http_methods(["GET"])
def get_my_attendance(request):
    """Get student's attendance records."""
    try:
        # Get filters
        subject_id = request.GET.get('subject', '')
        start_date = request.GET.get('start_date', '')
        end_date = request.GET.get('end_date', '')
        
        # Base attendance query
        attendance_query = Attendance.objects.filter(
            student=request.student
        ).select_related('timetable_entry__subject', 'timetable_entry__teacher')
        
        # Apply filters
        if subject_id:
            attendance_query = attendance_query.filter(timetable_entry__subject_id=subject_id)
        if start_date:
            attendance_query = attendance_query.filter(date__gte=start_date)
        if end_date:
            attendance_query = attendance_query.filter(date__lte=end_date)
        
        # Get attendance records
        attendance_records = attendance_query.order_by('-date')[:50]  # Limit to recent 50 records
        
        attendance_data = []
        total_classes = 0
        present_count = 0
        
        for record in attendance_records:
            attendance_data.append({
                'date': record.date.strftime('%Y-%m-%d'),
                'subject': record.timetable_entry.subject.name,
                'teacher': record.timetable_entry.teacher.full_name,
                'status': record.status,
                'marked_at': record.marked_at.strftime('%Y-%m-%d %H:%M') if record.marked_at else 'Not marked'
            })
            
            total_classes += 1
            if record.status == 'present':
                present_count += 1
        
        # Calculate overall statistics
        attendance_percentage = (present_count / total_classes * 100) if total_classes > 0 else 0
        
        # Get subject-wise statistics
        subject_stats = {}
        for record in attendance_records:
            subject_name = record.timetable_entry.subject.name
            if subject_name not in subject_stats:
                subject_stats[subject_name] = {'total': 0, 'present': 0}
            
            subject_stats[subject_name]['total'] += 1
            if record.status == 'present':
                subject_stats[subject_name]['present'] += 1
        
        for subject_name in subject_stats:
            stats = subject_stats[subject_name]
            stats['percentage'] = (stats['present'] / stats['total'] * 100) if stats['total'] > 0 else 0
        
        return JsonResponse({
            'success': True,
            'attendance_records': attendance_data,
            'statistics': {
                'total_classes': total_classes,
                'present_count': present_count,
                'absent_count': total_classes - present_count,
                'attendance_percentage': round(attendance_percentage, 1),
                'subject_wise': subject_stats
            }
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@login_required
@student_required_api
@require_http_methods(["GET"])
def get_my_study_materials(request):
    """Get study materials for student's courses."""
    try:
        # Get filters
        subject_id = request.GET.get('subject', '')
        material_type = request.GET.get('type', '')
        
        # Get study materials for student's course/year/section
        materials_query = StudyMaterial.objects.filter(
            course=request.student.course,
            year=request.student.year,
            section=request.student.section,
            is_published=True
        ).select_related('subject', 'uploaded_by').order_by('-uploaded_at')
        
        # Apply filters
        if subject_id:
            materials_query = materials_query.filter(subject_id=subject_id)
        if material_type:
            materials_query = materials_query.filter(material_type=material_type)
        
        materials = materials_query[:50]  # Limit to recent 50 materials
        
        materials_data = []
        for material in materials:
            materials_data.append({
                'id': material.id,
                'title': material.title,
                'description': material.description,
                'subject': material.subject.name,
                'type': material.get_material_type_display(),
                'uploaded_by': material.uploaded_by.get_full_name(),
                'uploaded_at': material.uploaded_at.strftime('%Y-%m-%d %H:%M'),
                'file_url': material.file_url,
                'content_preview': material.content[:200] + '...' if len(material.content) > 200 else material.content
            })
        
        return JsonResponse({
            'success': True,
            'materials': materials_data,
            'total_count': materials_query.count()
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@login_required
@student_required_api
@require_http_methods(["GET"])
def get_my_announcements(request):
    """Get announcements for the student."""
    try:
        # Get announcements targeted to this student's class or general announcements
        announcements_query = Announcement.objects.filter(
            Q(target_audience='all') |
            Q(target_audience='section',
              target_course=request.student.course,
              target_year=request.student.year,
              target_section=request.student.section)
        ).select_related('posted_by').order_by('-is_urgent', '-posted_at')
        
        recent_announcements = announcements_query[:20]  # Recent 20 announcements
        
        announcements_data = []
        for announcement in recent_announcements:
            announcements_data.append({
                'id': announcement.id,
                'title': announcement.title,
                'content': announcement.content,
                'posted_by': announcement.posted_by.get_full_name(),
                'posted_at': announcement.posted_at.strftime('%Y-%m-%d %H:%M'),
                'is_urgent': announcement.is_urgent,
                'target_audience': announcement.get_target_audience_display()
            })
        
        # Count urgent announcements
        urgent_count = announcements_query.filter(is_urgent=True).count()
        
        return JsonResponse({
            'success': True,
            'announcements': announcements_data,
            'urgent_count': urgent_count,
            'total_count': announcements_query.count()
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@login_required
@student_required_api
@require_http_methods(["GET"])
def get_dashboard_stats(request):
    """Get dashboard statistics for student."""
    try:
        # Get enrolled subjects count
        enrolled_subjects = Enrollment.objects.filter(
            student=request.student,
            is_active=True
        ).count()
        
        # Get attendance statistics
        attendance_records = Attendance.objects.filter(student=request.student)
        total_classes = attendance_records.count()
        present_classes = attendance_records.filter(status='present').count()
        attendance_percentage = (present_classes / total_classes * 100) if total_classes > 0 else 0
        
        # Get recent announcements count
        recent_announcements = Announcement.objects.filter(
            Q(target_audience='all') |
            Q(target_audience='section',
              target_course=request.student.course,
              target_year=request.student.year,
              target_section=request.student.section),
            posted_at__gte=timezone.now() - timedelta(days=7)
        ).count()
        
        # Get available study materials count
        study_materials = StudyMaterial.objects.filter(
            course=request.student.course,
            year=request.student.year,
            section=request.student.section,
            is_published=True
        ).count()
        
        # Get today's classes
        today = timezone.now().date()
        today_weekday = today.weekday()  # 0=Monday, 6=Sunday
        
        today_classes = TimetableEntry.objects.filter(
            subject__in=Enrollment.objects.filter(
                student=request.student,
                is_active=True
            ).values('subject'),
            course=request.student.course,
            year=request.student.year,
            section=request.student.section,
            day_of_week=today_weekday,
            is_active=True
        ).select_related('subject', 'teacher', 'time_slot').order_by('time_slot__start_time')
        
        today_schedule = []
        for class_entry in today_classes:
            today_schedule.append({
                'subject': class_entry.subject.name,
                'teacher': class_entry.teacher.full_name,
                'time': f"{class_entry.time_slot.start_time} - {class_entry.time_slot.end_time}",
                'room': class_entry.room.room_number
            })
        
        stats = {
            'enrolled_subjects': enrolled_subjects,
            'total_classes': total_classes,
            'attendance_percentage': round(attendance_percentage, 1),
            'recent_announcements': recent_announcements,
            'study_materials': study_materials,
            'today_classes': today_schedule
        }
        
        return JsonResponse({'success': True, 'stats': stats})
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@login_required
@student_required_api
@require_http_methods(["GET"])
def check_student_updates(request):
    """Check for real-time updates for student interface."""
    try:
        student_id = request.student.id
        course_section = f"{request.student.course}_{request.student.year}_{request.student.section}"
        
        updates = {
            'has_updates': False,
            'timestamp': timezone.now().isoformat()
        }
        
        # Check for various update types
        update_keys = [
            f'attendance_updated_{student_id}',
            f'materials_updated_{course_section}',
            f'announcements_updated_{course_section}',
            f'timetable_updated_{course_section}'
        ]
        
        for key in update_keys:
            if cache.get(key):
                updates['has_updates'] = True
                # Clear the cache key after reading
                cache.delete(key)
                break
        
        return JsonResponse(updates)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@login_required
@student_required_api
@require_http_methods(["GET"])
def get_material_details(request, material_id):
    """Get detailed information about a study material."""
    try:
        material = get_object_or_404(
            StudyMaterial, 
            id=material_id,
            course=request.student.course,
            year=request.student.year,
            section=request.student.section,
            is_published=True
        )
        
        material_data = {
            'id': material.id,
            'title': material.title,
            'description': material.description,
            'subject': material.subject.name,
            'type': material.get_material_type_display(),
            'content': material.content,
            'file_url': material.file_url,
            'uploaded_by': material.uploaded_by.get_full_name(),
            'uploaded_at': material.uploaded_at.strftime('%Y-%m-%d %H:%M')
        }
        
        return JsonResponse({'success': True, 'material': material_data})
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)
