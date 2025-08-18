"""
Teacher API views for real-time synchronization and AJAX functionality
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
import csv
from datetime import datetime, timedelta

from .models import User, StudentProfile, TeacherProfile
from timetable.models import (
    Course, Subject, Teacher, TeacherSubject, TimeSlot, Room,
    TimetableEntry, Enrollment, Attendance, Announcement
)
from ai_features.models import StudyMaterial, Assignment

def teacher_required_api(view_func):
    """Decorator to ensure user is a teacher for API calls."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'message': 'Authentication required'}, status=401)
        
        # Check if user has teacher profile or is linked to a teacher
        teacher = None
        if hasattr(request.user, 'teacherprofile') and request.user.teacherprofile.teacher:
            teacher = request.user.teacherprofile.teacher
        else:
            # Check if user is linked to a Teacher model via email
            try:
                teacher = Teacher.objects.get(email=request.user.email, is_active=True)
            except Teacher.DoesNotExist:
                pass
        
        if not teacher:
            return JsonResponse({'success': False, 'message': 'Teacher access required'}, status=403)
        
        # Add teacher to request for easy access
        request.teacher = teacher
        return view_func(request, *args, **kwargs)
    return wrapper

@login_required
@teacher_required_api
@require_http_methods(["GET"])
def get_class_students(request, class_id):
    """Get students for a specific class for attendance marking."""
    try:
        timetable_entry = get_object_or_404(TimetableEntry, id=class_id, teacher=request.teacher)
        
        # Get enrolled students for this subject
        enrollments = Enrollment.objects.filter(
            subject=timetable_entry.subject,
            is_active=True
        ).select_related('student', 'student__user').order_by('student__roll_number')
        
        students = []
        for enrollment in enrollments:
            students.append({
                'id': enrollment.student.pk,
                'name': enrollment.student.user.get_full_name(),
                'roll_number': enrollment.student.roll_number,
                'email': enrollment.student.user.email
            })
        
        class_info = {
            'subject_name': timetable_entry.subject.name,
            'subject_code': timetable_entry.subject.code,
            'course': timetable_entry.course,
            'year': timetable_entry.year,
            'section': timetable_entry.section,
            'room': timetable_entry.room.room_number,
            'time': f"{timetable_entry.time_slot.start_time} - {timetable_entry.time_slot.end_time}"
        }
        
        return JsonResponse({
            'success': True, 
            'students': students,
            'class_info': class_info
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@login_required
@teacher_required_api
@require_http_methods(["POST"])
def save_attendance(request):
    """Save attendance data for a class."""
    try:
        data = json.loads(request.body)
        class_id = data.get('class_id')
        attendance_date = data.get('date')
        attendance_data = data.get('attendance', {})
        
        timetable_entry = get_object_or_404(TimetableEntry, id=class_id, teacher=request.teacher)
        
        with transaction.atomic():
            saved_count = 0
            for student_id, status in attendance_data.items():
                student = get_object_or_404(StudentProfile, pk=student_id)
                
                attendance, created = Attendance.objects.get_or_create(
                    student=student,
                    timetable_entry=timetable_entry,
                    date=attendance_date,
                    defaults={
                        'status': status,
                        'marked_by': request.user
                    }
                )
                
                if not created and attendance.status != status:
                    attendance.status = status
                    attendance.marked_by = request.user
                    attendance.save()
                
                saved_count += 1
        
        # Broadcast change for real-time sync
        cache.set(f'attendance_updated_{timetable_entry.id}', True, timeout=300)
        
        return JsonResponse({
            'success': True, 
            'message': f'Attendance saved for {saved_count} students'
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@login_required
@teacher_required_api
@require_http_methods(["POST"])
def generate_attendance_report(request, subject_id):
    """Generate attendance report for a subject."""
    try:
        # Verify teacher teaches this subject
        subject = get_object_or_404(Subject, id=subject_id)
        teacher_subject = TeacherSubject.objects.filter(
            teacher=request.teacher,
            subject=subject,
            is_active=True
        ).first()
        
        if not teacher_subject:
            return JsonResponse({'success': False, 'message': 'You do not teach this subject'}, status=403)
        
        # Get attendance data
        attendance_records = Attendance.objects.filter(
            timetable_entry__subject=subject,
            timetable_entry__teacher=request.teacher
        ).select_related('student', 'student__user').order_by('date', 'student__roll_number')
        
        # Generate CSV report
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="attendance_report_{subject.code}_{datetime.now().strftime("%Y%m%d")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Date', 'Roll Number', 'Student Name', 'Status'])
        
        for record in attendance_records:
            writer.writerow([
                record.date.strftime('%Y-%m-%d'),
                record.student.roll_number,
                record.student.user.get_full_name(),
                record.status.title()
            ])
        
        return response
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@login_required
@teacher_required_api
@require_http_methods(["POST"])
def upload_study_material(request):
    """Upload study material for students."""
    try:
        title = request.POST.get('title')
        description = request.POST.get('description', '')
        subject_id = request.POST.get('subject_id')
        course = request.POST.get('course')
        year = int(request.POST.get('year'))
        section = request.POST.get('section')
        material_type = request.POST.get('material_type', 'document')
        content = request.POST.get('content', '')
        file_url = request.POST.get('file_url', '')
        is_published = bool(request.POST.get('is_published', False))
        
        # Verify teacher teaches this subject
        subject = get_object_or_404(Subject, id=subject_id)
        teacher_subject = TeacherSubject.objects.filter(
            teacher=request.teacher,
            subject=subject,
            is_active=True
        ).first()
        
        if not teacher_subject:
            return JsonResponse({'success': False, 'message': 'You do not teach this subject'}, status=403)
        
        material = StudyMaterial.objects.create(
            title=title,
            description=description,
            subject=subject,
            course=course,
            year=year,
            section=section,
            material_type=material_type,
            content=content,
            file_url=file_url,
            uploaded_by=request.user,
            is_published=is_published
        )
        
        # Broadcast change for real-time sync
        cache.set(f'materials_updated_{subject_id}', True, timeout=300)
        
        return JsonResponse({
            'success': True,
            'message': 'Study material uploaded successfully',
            'material_id': material.id
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@login_required
@teacher_required_api
@require_http_methods(["POST"])
def delete_study_material(request, material_id):
    """Delete study material."""
    try:
        material = get_object_or_404(StudyMaterial, id=material_id, uploaded_by=request.user)
        material.delete()
        
        # Broadcast change for real-time sync
        cache.set(f'materials_updated_{material.subject.id}', True, timeout=300)
        
        return JsonResponse({'success': True, 'message': 'Study material deleted successfully'})
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@login_required
@teacher_required_api
@require_http_methods(["POST"])
def send_announcement(request):
    """Send announcement to students."""
    try:
        data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
        
        title = data.get('title')
        message = data.get('message') or data.get('content')
        class_id = data.get('class_id')
        is_urgent = bool(data.get('is_urgent', False))
        
        # Get class information if class_id is provided
        if class_id:
            timetable_entry = get_object_or_404(TimetableEntry, id=class_id, teacher=request.teacher)
            target_audience = 'section'
            target_course = timetable_entry.course
            target_year = timetable_entry.year
            target_section = timetable_entry.section
        else:
            # General announcement to all students taught by this teacher
            target_audience = 'all'
            target_course = ''
            target_year = None
            target_section = ''
        
        announcement = Announcement.objects.create(
            title=title,
            content=message,
            posted_by=request.user,
            target_audience=target_audience,
            target_course=target_course,
            target_year=target_year,
            target_section=target_section,
            is_urgent=is_urgent
        )
        
        # Broadcast change for real-time sync
        cache.set(f'announcements_updated_{request.teacher.id}', True, timeout=300)
        
        return JsonResponse({
            'success': True,
            'message': 'Announcement sent successfully',
            'announcement_id': announcement.id
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@login_required
@teacher_required_api
@require_http_methods(["GET"])
def get_class_details(request, class_id):
    """Get detailed information about a class."""
    try:
        timetable_entry = get_object_or_404(TimetableEntry, id=class_id, teacher=request.teacher)
        
        # Get enrolled students
        enrollments = Enrollment.objects.filter(
            subject=timetable_entry.subject,
            is_active=True
        ).select_related('student', 'student__user')
        
        students = []
        total_present = 0
        total_classes = 0
        
        for enrollment in enrollments:
            # Get attendance statistics for this student in this subject
            student_attendance = Attendance.objects.filter(
                student=enrollment.student,
                timetable_entry__subject=timetable_entry.subject,
                timetable_entry__teacher=request.teacher
            )
            
            total_classes_student = student_attendance.count()
            present_classes = student_attendance.filter(status='present').count()
            attendance_percentage = (present_classes / total_classes_student * 100) if total_classes_student > 0 else 0
            
            students.append({
                'id': enrollment.student.pk,
                'name': enrollment.student.user.get_full_name(),
                'roll_number': enrollment.student.roll_number,
                'attendance_percentage': round(attendance_percentage, 1)
            })
            
            total_present += present_classes
            total_classes += total_classes_student
        
        # Calculate overall class statistics
        avg_attendance = (total_present / total_classes * 100) if total_classes > 0 else 0
        classes_held = Attendance.objects.filter(
            timetable_entry=timetable_entry
        ).values('date').distinct().count()
        
        class_info = {
            'id': timetable_entry.id,
            'subject_name': timetable_entry.subject.name,
            'subject_code': timetable_entry.subject.code,
            'subject_id': timetable_entry.subject.id,
            'course': timetable_entry.course,
            'year': timetable_entry.year,
            'section': timetable_entry.section,
            'room': timetable_entry.room.room_number,
            'total_students': len(students),
            'schedule': f"{timetable_entry.get_day_of_week_display()} - Period {timetable_entry.time_slot.period_number}",
            'attendance_stats': {
                'average_percentage': round(avg_attendance, 1),
                'classes_held': classes_held,
                'total_present': total_present
            },
            'students': students
        }
        
        return JsonResponse({'success': True, 'class_info': class_info})
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@login_required
@teacher_required_api
@require_http_methods(["GET"])
def get_attendance_summary(request):
    """Get attendance summary for teacher's subjects."""
    try:
        # Get filters
        course = request.GET.get('course', '')
        year = request.GET.get('year', '')
        section = request.GET.get('section', '')
        subject_id = request.GET.get('subject', '')
        
        # Base query for attendance
        attendance_query = Attendance.objects.filter(
            timetable_entry__teacher=request.teacher
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
        
        # Get statistics
        total_classes = attendance_query.count()
        present_count = attendance_query.filter(status='present').count()
        attendance_percentage = (present_count / total_classes * 100) if total_classes > 0 else 0
        
        # Get recent attendance records
        recent_attendance = attendance_query.order_by('-date', '-marked_at')[:20]
        
        attendance_data = []
        for record in recent_attendance:
            attendance_data.append({
                'student_name': record.student.user.get_full_name(),
                'roll_number': record.student.roll_number,
                'subject': record.timetable_entry.subject.name,
                'date': record.date.strftime('%Y-%m-%d'),
                'status': record.status,
                'marked_at': record.marked_at.strftime('%Y-%m-%d %H:%M')
            })
        
        summary = {
            'total_classes': total_classes,
            'present_count': present_count,
            'absent_count': total_classes - present_count,
            'attendance_percentage': round(attendance_percentage, 1),
            'recent_records': attendance_data
        }
        
        return JsonResponse({'success': True, 'summary': summary})
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@login_required
@teacher_required_api
@require_http_methods(["GET"])
def check_teacher_updates(request):
    """Check for real-time updates for teacher interface."""
    try:
        teacher_id = request.teacher.id
        updates = {
            'has_updates': False,
            'timestamp': timezone.now().isoformat()
        }
        
        # Check for various update types
        update_keys = [
            f'attendance_updated_{teacher_id}',
            f'materials_updated_{teacher_id}',
            f'announcements_updated_{teacher_id}',
            f'timetable_updated_{teacher_id}'
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
