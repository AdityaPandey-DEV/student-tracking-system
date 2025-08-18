"""
Admin API views for real-time synchronization and AJAX functionality
"""

from django.http import JsonResponse, Http404
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.core.cache import cache
from django.utils import timezone
import json

from .models import User, StudentProfile, AdminProfile, TeacherProfile
from timetable.models import (
    Course, Subject, Teacher, TeacherSubject, TimeSlot, Room,
    TimetableEntry, Enrollment, Attendance, Announcement
)
from ai_features.models import PerformanceInsight

def admin_required_api(view_func):
    """Decorator to ensure user is an admin for API calls."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return JsonResponse({'success': False, 'message': 'Authentication required'}, status=401)
        # Allow if user has an admin profile OR is superuser/staff OR user_type indicates admin
        is_admin_user = (
            hasattr(request.user, 'adminprofile') or
            getattr(request.user, 'is_superuser', False) or
            getattr(request.user, 'is_staff', False) or
            getattr(request.user, 'user_type', '') == 'admin'
        )
        if not is_admin_user:
            return JsonResponse({'success': False, 'message': 'Admin access required'}, status=403)
        return view_func(request, *args, **kwargs)
    return wrapper

@login_required
@admin_required_api
@require_http_methods(["GET"])
def get_teacher_details(request, teacher_id):
    """Get teacher details for modal display."""
    try:
        teacher = get_object_or_404(Teacher, id=teacher_id)
        
        # Get assigned subjects
        subjects = TeacherSubject.objects.filter(
            teacher=teacher, is_active=True
        ).select_related('subject', 'subject__course')
        
        subject_data = []
        for ts in subjects:
            subject_data.append({
                'code': ts.subject.code,
                'name': ts.subject.name,
                'course': ts.subject.course.name,
                'year': ts.subject.year,
                'credits': ts.subject.credits
            })
        
        teacher_data = {
            'id': teacher.id,
            'name': teacher.name,
            'employee_id': teacher.employee_id,
            'email': teacher.email,
            'phone_number': teacher.phone_number or '',
            'department': teacher.department,
            'designation': teacher.designation or '',
            'specialization': teacher.specialization or '',
            'is_active': teacher.is_active,
            'created_at': teacher.created_at.isoformat(),
            'subjects': subject_data
        }
        
        return JsonResponse({'success': True, 'teacher': teacher_data})
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@login_required
@admin_required_api
@require_http_methods(["POST"])
def update_teacher(request, teacher_id):
    """Update teacher information."""
    try:
        teacher = get_object_or_404(Teacher, id=teacher_id)
        
        # Update teacher fields
        teacher.name = request.POST.get('name', teacher.name)
        teacher.employee_id = request.POST.get('employee_id', teacher.employee_id)
        teacher.email = request.POST.get('email', teacher.email)
        teacher.phone_number = request.POST.get('phone_number', teacher.phone_number)
        teacher.department = request.POST.get('department', teacher.department)
        teacher.designation = request.POST.get('designation', teacher.designation)
        teacher.specialization = request.POST.get('specialization', teacher.specialization)
        
        teacher.save()
        
        # Broadcast change for real-time sync
        cache.set(f'teacher_updated_{teacher.id}', True, timeout=300)
        
        return JsonResponse({'success': True, 'message': 'Teacher updated successfully'})
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@login_required
@admin_required_api
@require_http_methods(["POST"])
def delete_teacher_assignment(request, assignment_id):
    """Remove teacher-subject assignment."""
    try:
        assignment = get_object_or_404(TeacherSubject, id=assignment_id)
        assignment.is_active = False
        assignment.save()
        
        # Broadcast change for real-time sync
        cache.set(f'assignment_deleted_{assignment_id}', True, timeout=300)
        
        return JsonResponse({'success': True, 'message': 'Assignment removed successfully'})
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@login_required
@admin_required_api
@require_http_methods(["GET"])
def get_student_details(request, student_id):
    """Get student details for modal display."""
    try:
        student = get_object_or_404(StudentProfile, pk=student_id)
        
        # Get enrollments
        enrollments = Enrollment.objects.filter(
            student=student, is_active=True
        ).select_related('subject')
        
        enrollment_data = []
        for enrollment in enrollments:
            enrollment_data.append({
                'subject_code': enrollment.subject.code,
                'subject_name': enrollment.subject.name,
                'semester': enrollment.semester,
                'academic_year': enrollment.academic_year
            })
        
        # Get attendance statistics
        total_attendance = Attendance.objects.filter(student=student).count()
        present_attendance = Attendance.objects.filter(student=student, status='present').count()
        absent_attendance = Attendance.objects.filter(student=student, status='absent').count()
        
        attendance_percentage = (present_attendance / total_attendance * 100) if total_attendance > 0 else 0
        
        student_data = {
            'id': student.pk,
            'name': student.user.get_full_name(),
            'roll_number': student.roll_number,
            'course': student.course,
            'year': student.year,
            'section': student.section,
            'email': student.user.email,
            'phone': student.user.phone_number or '',
            'is_active': student.user.is_active,
            'is_verified': student.user.is_verified,
            'enrollments': enrollment_data,
            'attendance_stats': {
                'percentage': round(attendance_percentage, 1),
                'present_days': present_attendance,
                'absent_days': absent_attendance,
                'total_days': total_attendance
            }
        }
        
        return JsonResponse({'success': True, 'student': student_data})
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@login_required
@admin_required_api
@require_http_methods(["POST"])
def toggle_student_status(request, student_id):
    """Toggle student account status."""
    try:
        data = json.loads(request.body)
        student = get_object_or_404(StudentProfile, pk=student_id)
        
        student.user.is_active = data.get('is_active', True)
        student.user.save()
        
        # Broadcast change for real-time sync
        cache.set(f'student_status_updated_{student.pk}', True, timeout=300)
        
        status = 'activated' if student.user.is_active else 'deactivated'
        return JsonResponse({'success': True, 'message': f'Student {status} successfully'})
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@login_required
@admin_required_api
@require_http_methods(["POST"])
def export_students(request):
    """Export students data as CSV."""
    try:
        from django.http import HttpResponse
        import csv
        from datetime import datetime
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="students_export_{datetime.now().strftime("%Y%m%d")}.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['Roll Number', 'Name', 'Course', 'Year', 'Section', 'Email', 'Phone', 'Status'])
        
        students = StudentProfile.objects.select_related('user').all()
        for student in students:
            writer.writerow([
                student.roll_number,
                student.user.get_full_name(),
                student.course,
                student.year,
                student.section,
                student.user.email,
                student.user.phone_number or '',
                'Active' if student.user.is_active else 'Inactive'
            ])
        
        return response
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@login_required
@admin_required_api
@require_http_methods(["POST"])
def update_student(request, student_id):
    """Update student profile and basic user fields."""
    try:
        student = get_object_or_404(StudentProfile, pk=student_id)
        user = student.user

        # Read from POST (form-data)
        first_name = request.POST.get('first_name', user.first_name)
        last_name = request.POST.get('last_name', user.last_name)
        email = request.POST.get('email', user.email)
        phone_number = request.POST.get('phone_number', getattr(user, 'phone_number', ''))
        roll_number = request.POST.get('roll_number', student.roll_number)
        course = request.POST.get('course', student.course)
        year = request.POST.get('year', student.year)
        section = request.POST.get('section', student.section)
        is_active = request.POST.get('is_active')

        # Update user fields
        user.first_name = first_name
        user.last_name = last_name
        user.email = email
        if hasattr(user, 'phone_number'):
            user.phone_number = phone_number
        if is_active is not None:
            user.is_active = str(is_active).lower() in ['1', 'true', 'yes', 'on']
        user.save()

        # Update student profile
        student.roll_number = roll_number.upper()
        student.course = course
        try:
            student.year = int(year)
        except (TypeError, ValueError):
            pass
        student.section = section.upper()
        student.save()

        # Broadcast change for real-time sync
        cache.set(f'student_status_updated_{student.pk}', True, timeout=300)

        return JsonResponse({'success': True, 'message': 'Student updated successfully'})

    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@login_required
@admin_required_api
@require_http_methods(["GET"])
def get_timetable_entry(request, entry_id):
    """Get timetable entry details for editing."""
    try:
        entry = get_object_or_404(TimetableEntry, id=entry_id)
        
        # Get available options
        courses = list(Course.objects.filter(is_active=True).values('id', 'name'))
        subjects = list(Subject.objects.filter(is_active=True).values('id', 'code', 'name'))
        teachers = list(Teacher.objects.filter(is_active=True).values('id', 'name'))
        time_slots = list(TimeSlot.objects.filter(is_active=True).values('id', 'period_number'))
        rooms = list(Room.objects.filter(is_active=True).values('id', 'room_number'))
        
        entry_data = {
            'id': entry.id,
            'subject_id': entry.subject.id,
            'teacher_id': entry.teacher.id,
            'course': entry.course,
            'year': entry.year,
            'section': entry.section,
            'day_of_week': entry.day_of_week,
            'time_slot_id': entry.time_slot.id,
            'room_id': entry.room.id,
            'academic_year': entry.academic_year,
            'semester': entry.semester
        }
        
        return JsonResponse({
            'success': True,
            'entry': entry_data,
            'courses': courses,
            'subjects': subjects,
            'teachers': teachers,
            'time_slots': time_slots,
            'rooms': rooms
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@login_required
@admin_required_api
@require_http_methods(["POST"])
def update_timetable_entry(request, entry_id):
    """Update timetable entry."""
    try:
        entry = get_object_or_404(TimetableEntry, id=entry_id)
        
        with transaction.atomic():
            entry.subject_id = request.POST.get('subject_id')
            entry.teacher_id = request.POST.get('teacher_id')
            entry.course = request.POST.get('course')
            entry.year = int(request.POST.get('year'))
            entry.section = request.POST.get('section').upper()
            entry.day_of_week = int(request.POST.get('day_of_week'))
            entry.time_slot_id = request.POST.get('time_slot_id')
            entry.room_id = request.POST.get('room_id')
            entry.semester = int(request.POST.get('semester'))
            
            entry.save()
        
        # Broadcast change for real-time sync
        cache.set(f'timetable_updated_{entry.id}', True, timeout=300)
        
        return JsonResponse({'success': True, 'message': 'Timetable entry updated successfully'})
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@login_required
@admin_required_api
@require_http_methods(["POST"])
def delete_timetable_entry(request, entry_id):
    """Delete timetable entry."""
    try:
        entry = get_object_or_404(TimetableEntry, id=entry_id)
        entry.is_active = False
        entry.save()
        
        # Broadcast change for real-time sync
        cache.set(f'timetable_deleted_{entry_id}', True, timeout=300)
        
        return JsonResponse({'success': True, 'message': 'Timetable entry deleted successfully'})
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@login_required
@admin_required_api
@require_http_methods(["POST"])
def export_timetable(request):
    """Export timetable as PDF."""
    try:
        from django.http import HttpResponse
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter, landscape
        from reportlab.lib import colors
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
        import io
        from datetime import datetime
        
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
        
        # Get timetable data
        entries = TimetableEntry.objects.filter(is_active=True).select_related(
            'subject', 'teacher', 'time_slot', 'room'
        ).order_by('course', 'year', 'section', 'day_of_week', 'time_slot__period_number')
        
        # Create table data
        data = [['Course/Year/Section', 'Day', 'Period', 'Subject', 'Teacher', 'Room']]
        
        for entry in entries:
            day_names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
            data.append([
                f"{entry.course} Y{entry.year}{entry.section}",
                day_names[entry.day_of_week],
                f"P{entry.time_slot.period_number}",
                f"{entry.subject.code}",
                entry.teacher.name,
                entry.room.room_number
            ])
        
        # Create table
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        doc.build([table])
        
        pdf = buffer.getvalue()
        buffer.close()
        
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="timetable_export_{datetime.now().strftime("%Y%m%d")}.pdf"'
        
        return response
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@login_required
@admin_required_api
@require_http_methods(["GET"])
def get_filtered_timetable_entries(request):
    """Get filtered timetable entries for grid view."""
    try:
        course = request.GET.get('course')
        year = request.GET.get('year')
        section = request.GET.get('section')
        
        entries = TimetableEntry.objects.filter(is_active=True).select_related(
            'subject', 'teacher', 'time_slot', 'room'
        )
        
        if course:
            entries = entries.filter(course=course)
        if year:
            entries = entries.filter(year=int(year))
        if section:
            entries = entries.filter(section=section)
        
        entry_data = []
        for entry in entries:
            entry_data.append({
                'day_of_week': entry.day_of_week,
                'period_number': entry.time_slot.period_number,
                'subject_code': entry.subject.code,
                'course': entry.course,
                'year': entry.year,
                'section': entry.section,
                'teacher_name': entry.teacher.name,
                'room_number': entry.room.room_number
            })
        
        return JsonResponse({'success': True, 'entries': entry_data})
    
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@login_required
@admin_required_api
@require_http_methods(["GET"])
def get_ai_suggestion(request, suggestion_id):
    """Get AI timetable suggestion details."""
    try:
        from ai_features.models import TimetableSuggestion
        
        suggestion = get_object_or_404(TimetableSuggestion, id=suggestion_id)
        
        suggestion_data = {
            'id': suggestion.id,
            'course': suggestion.course,
            'year': suggestion.year,
            'section': suggestion.section,
            'optimization_score': suggestion.optimization_score,
            'status': suggestion.status,
            'is_applied': suggestion.status in ['approved', 'implemented'],
            'created_at': suggestion.created_at.isoformat(),
            'analysis': 'AI-generated optimization suggestions for improved scheduling'
        }
        
        return JsonResponse({'success': True, 'suggestion': suggestion_data})
    
    except Http404:
        return JsonResponse({'success': False, 'message': 'Suggestion not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)

@login_required
@admin_required_api
@require_http_methods(["GET"])
def check_updates(request):
    """Check for real-time updates using cache."""
    try:
        updates = {}
        
        # Check for various update types
        cache_keys = [
            'teacher_updated_*', 'student_status_updated_*',
            'timetable_updated_*', 'assignment_deleted_*'
        ]
        
        # In a real implementation, you'd check specific cache keys
        # For now, return a simple response
        updates = {
            'has_updates': False,
            'timestamp': timezone.now().isoformat()
        }
        
        return JsonResponse(updates)
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


@login_required
@admin_required_api
@require_http_methods(["POST"])
def dismiss_insight(request, insight_id):
    """Persistently dismiss an AI PerformanceInsight so it doesn't reappear."""
    try:
        insight = get_object_or_404(PerformanceInsight, id=insight_id)
        insight.is_viewed = True
        insight.is_actionable = False
        insight.save(update_fields=['is_viewed', 'is_actionable'])
        return JsonResponse({'success': True})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=400)
