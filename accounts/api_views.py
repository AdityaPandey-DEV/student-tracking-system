"""
API views for AJAX functionality
Handles JSON responses for announcement viewing, search, and other interactive features
"""

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
import json
from django.db.models import Q
from django.utils import timezone
from django.db import connection

# Import models
from timetable.models import Announcement, Subject, TimetableEntry, Teacher, Course
from ai_features.models import StudyRecommendation, SmartNotification
from utils.ai_service import ai_service
from .models import StudentProfile, User


@login_required
@require_http_methods(["GET"])
def get_announcement_details(request, announcement_id):
    """Get announcement details for modal display"""
    try:
        announcement = get_object_or_404(Announcement, id=announcement_id)
        
        announcement_data = {
            'id': announcement.id,
            'title': announcement.title,
            'content': announcement.content,
            'is_urgent': announcement.is_urgent,
            'target_audience': announcement.target_audience,
            'target_audience_display': announcement.get_target_audience_display(),
            'target_course': announcement.target_course or '',
            'target_year': announcement.target_year,
            'target_section': announcement.target_section or '',
            'created_at': announcement.created_at.isoformat(),
            'posted_by_name': announcement.posted_by.get_full_name()
        }
        
        return JsonResponse(announcement_data)
    
    except Exception as e:
        return JsonResponse({
            'error': 'Failed to load announcement details',
            'message': str(e)
        }, status=400)


@login_required
@require_http_methods(["POST"])
def delete_announcement(request, announcement_id):
    """Delete announcement via AJAX"""
    try:
        announcement = get_object_or_404(Announcement, id=announcement_id)
        announcement.is_active = False
        announcement.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Announcement deleted successfully'
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


@login_required
@require_http_methods(["GET"])
def search_content(request):
    """Global search functionality"""
    try:
        query = request.GET.get('q', '').strip()
        
        if len(query) < 2:
            return JsonResponse({
                'subjects': [],
                'announcements': [],
                'teachers': [],
                'message': 'Query too short'
            })
        
        # Search subjects
        subjects = Subject.objects.filter(
            Q(name__icontains=query) | Q(code__icontains=query),
            is_active=True
        )[:10]
        
        subject_results = [{
            'id': subject.id,
            'name': subject.name,
            'code': subject.code,
            'course': subject.course.name,
            'year': subject.year,
            'credits': subject.credits
        } for subject in subjects]
        
        # Search announcements (visible to current user)
        announcements_query = Q(title__icontains=query) | Q(content__icontains=query)
        if hasattr(request.user, 'studentprofile'):
            student = request.user.studentprofile
            announcements_query &= (
                Q(target_audience='all') |
                Q(target_audience='course', target_course=student.course) |
                Q(target_audience='year', target_year=student.year) |
                Q(target_audience='section', target_course=student.course,
                  target_year=student.year, target_section=student.section)
            )
        
        announcements = Announcement.objects.filter(
            announcements_query, is_active=True
        )[:5]
        
        announcement_results = [{
            'id': ann.id,
            'title': ann.title,
            'content_preview': ann.content[:100] + '...' if len(ann.content) > 100 else ann.content,
            'is_urgent': ann.is_urgent,
            'created_at': ann.created_at.strftime('%Y-%m-%d %H:%M')
        } for ann in announcements]
        
        # Search teachers
        teachers = Teacher.objects.filter(
            Q(name__icontains=query) | Q(employee_id__icontains=query) |
            Q(department__icontains=query) | Q(specialization__icontains=query),
            is_active=True
        )[:5]
        
        teacher_results = [{
            'id': teacher.id,
            'name': teacher.name,
            'employee_id': teacher.employee_id,
            'department': teacher.department,
            'specialization': teacher.specialization[:50] + '...' if teacher.specialization and len(teacher.specialization) > 50 else teacher.specialization or ''
        } for teacher in teachers]
        
        return JsonResponse({
            'subjects': subject_results,
            'announcements': announcement_results,
            'teachers': teacher_results,
            'total_results': len(subject_results) + len(announcement_results) + len(teacher_results)
        })
    
    except Exception as e:
        return JsonResponse({
            'error': 'Search failed',
            'message': str(e)
        }, status=400)


@login_required
@require_http_methods(["POST"])
def generate_recommendations(request):
    """Generate AI recommendations for student"""
    try:
        # Mock recommendation generation - replace with actual AI logic
        recommendations = [
            {
                'title': 'Study Schedule Recommendation',
                'description': 'Based on your recent performance, we recommend focusing on Data Structures this week.'
            },
            {
                'title': 'Assignment Reminder',
                'description': 'You have an upcoming assignment in Database Systems due next week.'
            }
        ]
        
        # Here you would actually create StudentRecommendation objects
        # for rec in recommendations:
        #     StudentRecommendation.objects.create(
        #         student=request.user.studentprofile,
        #         title=rec['title'],
        #         description=rec['description'],
        #         recommendation_type='study_plan'
        #     )
        
        return JsonResponse({
            'success': True,
            'recommendations': recommendations,
            'message': f'{len(recommendations)} recommendations generated'
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


@login_required
@require_http_methods(["POST"])
def dismiss_recommendation(request, recommendation_id):
    """Dismiss a specific recommendation"""
    try:
        # Mock dismissal - replace with actual model update
        # recommendation = get_object_or_404(StudentRecommendation, id=recommendation_id, student=request.user.studentprofile)
        # recommendation.is_dismissed = True
        # recommendation.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Recommendation dismissed'
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': str(e)
        }, status=400)


@login_required
@require_http_methods(["POST"])
def generate_attendance_report(request):
    """Generate attendance report as PDF"""
    try:
        from django.http import HttpResponse
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        import io
        
        # Create a file-like buffer to receive PDF data
        buffer = io.BytesIO()
        
        # Create the PDF object, using the buffer as its "file"
        p = canvas.Canvas(buffer, pagesize=letter)
        
        # Draw some sample content
        p.drawString(100, 750, f"Attendance Report for {request.user.get_full_name()}")
        p.drawString(100, 700, "Subject: Data Structures")
        p.drawString(100, 680, "Total Classes: 45")
        p.drawString(100, 660, "Attended: 42")
        p.drawString(100, 640, "Percentage: 93.3%")
        
        # Close the PDF object cleanly
        p.showPage()
        p.save()
        
        # Get the value of the BytesIO buffer and create response
        pdf = buffer.getvalue()
        buffer.close()
        
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename="attendance_report.pdf"'
        
        return response
    
    except Exception as e:
        return JsonResponse({
            'error': 'Failed to generate report',
            'message': str(e)
        }, status=400)


@login_required
@require_http_methods(["POST"])
def ai_chat_response(request):
    """Handle AI chat messages"""
    try:
        data = json.loads(request.body)
        message = data.get('message', '')
        session_id = data.get('session_id', '')
        
        if not message:
            return JsonResponse({
                'error': 'No message provided'
            }, status=400)
        
        # Build lightweight context
        context = {
            'student_name': request.user.get_full_name(),
            'current_courses': list(Subject.objects.filter(is_active=True).values_list('name', flat=True)[:5])
        }
        response = ai_service.chat_response(message, context)
        
        return JsonResponse({
            'response': response,
            'session_id': session_id
        })
    
    except Exception as e:
        return JsonResponse({
            'error': 'Failed to process AI request',
            'message': str(e)
        }, status=400)


@login_required
@require_http_methods(["GET"])
def get_student_context(request):
    """Get student context for AI chat"""
    try:
        # Mock student context - replace with actual profile data
        context = {
            'name': request.user.get_full_name(),
            'course': 'Computer Science',
            'year': '3',
            'section': 'A',
            'subjects': [
                {'name': 'Data Structures', 'code': 'CS301'},
                {'name': 'Database Systems', 'code': 'CS401'},
                {'name': 'Operating Systems', 'code': 'CS402'}
            ],
            'attendance_summary': {
                'overall_percentage': 85.5,
                'total_classes': 120,
                'attended': 102
            }
        }
        
        return JsonResponse(context)
    
    except Exception as e:
        return JsonResponse({
            'error': 'Failed to load student context',
            'message': str(e)
        }, status=400)


@require_http_methods(["GET"])
def db_health(request):
    """Lightweight DB health endpoint to indicate if DB is ready."""
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        return JsonResponse({
            'ready': True,
            'timestamp': timezone.now().isoformat()
        })
    except Exception as e:
        return JsonResponse({
            'ready': False,
            'message': str(e)
        }, status=503)