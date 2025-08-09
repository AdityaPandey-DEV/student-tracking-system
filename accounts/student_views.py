"""
Student dashboard and related views.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, Count
from django.utils import timezone
from datetime import datetime, timedelta
import json

from accounts.models import User, StudentProfile
from timetable.models import TimetableEntry, Subject, Enrollment, Attendance, Announcement
from ai_features.models import AIChat, ChatMessage, StudyRecommendation, SmartNotification
from utils.ai_service import ai_service

def student_required(view_func):
    """Decorator to ensure user is a student."""
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('login')
        if not hasattr(request.user, 'studentprofile'):
            messages.error(request, 'Access denied. Student account required.')
            return redirect('landing')
        return view_func(request, *args, **kwargs)
    return wrapper

@login_required
@student_required
def student_dashboard(request):
    """Student dashboard with AI-powered insights."""
    student = request.user.studentprofile
    today = timezone.now().date()
    
    # Get today's classes
    today_classes = TimetableEntry.objects.filter(
        course=student.course,
        year=student.year,
        section=student.section,
        day_of_week=today.weekday(),
        is_active=True
    ).select_related('subject', 'teacher', 'time_slot', 'room').order_by('time_slot__period_number')
    
    # Get upcoming classes (next 3 days)
    upcoming_classes = []
    for i in range(1, 4):
        future_date = today + timedelta(days=i)
        classes = TimetableEntry.objects.filter(
            course=student.course,
            year=student.year,
            section=student.section,
            day_of_week=future_date.weekday(),
            is_active=True
        ).select_related('subject', 'teacher', 'time_slot')[:3]
        if classes:
            upcoming_classes.extend([(future_date, cls) for cls in classes])
    
    # Get recent announcements
    announcements = Announcement.objects.filter(
        Q(target_audience='all') |
        Q(target_audience='course', target_course=student.course) |
        Q(target_audience='year', target_year=student.year) |
        Q(target_audience='section', target_course=student.course, 
          target_year=student.year, target_section=student.section),
        is_active=True
    ).order_by('-is_urgent', '-created_at')[:5]
    
    # Get study recommendations
    recommendations = StudyRecommendation.objects.filter(
        student=student,
        is_read=False
    ).order_by('-priority', '-confidence_score')[:3]
    
    # Get smart notifications
    notifications = SmartNotification.objects.filter(
        recipient=request.user,
        is_read=False,
        is_dismissed=False
    ).order_by('-priority', '-created_at')[:5]
    
    # AI-powered timetable summary
    if today_classes.exists():
        ai_summary = ai_service.chat_response(
            f"Summarize today's schedule for a {student.course} Year {student.year} student with {today_classes.count()} classes",
            context={'student_info': {
                'name': student.user.get_full_name(),
                'course': student.course,
                'year': student.year,
                'section': student.section
            }}
        )
    else:
        ai_summary = "No classes scheduled for today. Great time to catch up on assignments and review previous lessons!"
    
    context = {
        'student': student,
        'today_classes': today_classes,
        'upcoming_classes': upcoming_classes[:6],  # Limit to 6 items
        'announcements': announcements,
        'recommendations': recommendations,
        'notifications': notifications,
        'ai_summary': ai_summary,
        'today': today
    }
    
    return render(request, 'student/dashboard.html', context)

@login_required
@student_required
def student_timetable(request):
    """Full weekly timetable view for student."""
    student = request.user.studentprofile
    
    # Get all timetable entries for the student's class
    timetable_entries = TimetableEntry.objects.filter(
        course=student.course,
        year=student.year,
        section=student.section,
        is_active=True
    ).select_related('subject', 'teacher', 'time_slot', 'room').order_by('day_of_week', 'time_slot__period_number')
    
    # Organize by day and period
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    timetable = {}
    periods = set()
    
    for entry in timetable_entries:
        day_name = days[entry.day_of_week]
        period = entry.time_slot.period_number
        
        if day_name not in timetable:
            timetable[day_name] = {}
        
        timetable[day_name][period] = entry
        periods.add(period)
    
    # Sort periods
    sorted_periods = sorted(periods)
    
    context = {
        'student': student,
        'timetable': timetable,
        'days': days,
        'periods': sorted_periods,
        'timetable_entries': timetable_entries
    }
    
    return render(request, 'student/timetable.html', context)

@login_required
@student_required
def student_subjects(request):
    """Student subjects and enrollments."""
    student = request.user.studentprofile
    
    # Get enrolled subjects
    enrollments = Enrollment.objects.filter(
        student=student,
        is_active=True
    ).select_related('subject', 'subject__course').order_by('subject__name')
    
    # Get subject-wise attendance summary
    subject_attendance = {}
    for enrollment in enrollments:
        total_classes = Attendance.objects.filter(
            student=student,
            timetable_entry__subject=enrollment.subject
        ).count()
        
        present_classes = Attendance.objects.filter(
            student=student,
            timetable_entry__subject=enrollment.subject,
            status='present'
        ).count()
        
        attendance_percentage = (present_classes / total_classes * 100) if total_classes > 0 else 0
        
        subject_attendance[enrollment.subject.id] = {
            'total': total_classes,
            'present': present_classes,
            'percentage': round(attendance_percentage, 1)
        }
    
    context = {
        'student': student,
        'enrollments': enrollments,
        'subject_attendance': subject_attendance
    }
    
    return render(request, 'student/subjects.html', context)

@login_required
@student_required
@csrf_exempt
def ai_chat(request):
    """AI chat interface for students."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message', '').strip()
            session_id = data.get('session_id', '')
            
            if not message:
                return JsonResponse({'error': 'Message is required'}, status=400)
            
            student = request.user.studentprofile
            
            # Get or create chat session
            chat, created = AIChat.objects.get_or_create(
                user=request.user,
                session_id=session_id,
                defaults={'chat_type': 'general_query'}
            )
            
            # Save user message
            ChatMessage.objects.create(
                chat=chat,
                sender='user',
                message=message
            )
            
            # Generate AI response
            context = {
                'student_info': {
                    'name': student.user.get_full_name(),
                    'course': student.course,
                    'year': student.year,
                    'section': student.section
                }
            }
            
            ai_response = ai_service.chat_response(message, context)
            
            # Save AI response
            ChatMessage.objects.create(
                chat=chat,
                sender='ai',
                message=ai_response
            )
            
            # Update chat timestamp
            chat.updated_at = timezone.now()
            chat.save()
            
            return JsonResponse({
                'response': ai_response,
                'session_id': session_id
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': 'An error occurred'}, status=500)
    
    # GET request - show chat interface
    student = request.user.studentprofile
    
    # Get recent chat sessions
    recent_chats = AIChat.objects.filter(
        user=request.user
    ).order_by('-updated_at')[:5]
    
    context = {
        'student': student,
        'recent_chats': recent_chats
    }
    
    return render(request, 'student/ai_chat.html', context)

@login_required
@student_required
def student_recommendations(request):
    """View study recommendations."""
    student = request.user.studentprofile
    
    # Get all recommendations
    all_recommendations = StudyRecommendation.objects.filter(
        student=student
    ).order_by('-created_at')
    
    # Mark as read if viewing
    unread_recommendations = all_recommendations.filter(is_read=False)
    unread_recommendations.update(is_read=True)
    
    # Generate new recommendation if requested
    if request.method == 'POST' and request.POST.get('action') == 'generate':
        try:
            # Get student data for AI
            enrollments = Enrollment.objects.filter(student=student, is_active=True)
            subjects = [e.subject.name for e in enrollments]
            
            # Get recent attendance
            total_attendance = Attendance.objects.filter(student=student).count()
            present_attendance = Attendance.objects.filter(student=student, status='present').count()
            attendance_rate = (present_attendance / total_attendance * 100) if total_attendance > 0 else 0
            
            student_data = {
                'name': student.user.get_full_name(),
                'course': student.course,
                'year': student.year,
                'subjects': subjects,
                'attendance_rate': round(attendance_rate, 1),
                'performance_trend': 'Average'  # This could be calculated from grades
            }
            
            # Generate AI recommendation
            recommendation_data = ai_service.generate_study_recommendation(student_data)
            
            # Create recommendation
            StudyRecommendation.objects.create(
                student=student,
                recommendation_type='study_schedule',
                title=recommendation_data['title'],
                description=recommendation_data['description'],
                priority=recommendation_data['priority'],
                confidence_score=recommendation_data['confidence_score']
            )
            
            messages.success(request, 'New study recommendation generated!')
            return redirect('student_recommendations')
            
        except Exception as e:
            messages.error(request, 'Failed to generate recommendation. Please try again.')
    
    context = {
        'student': student,
        'recommendations': all_recommendations
    }
    
    return render(request, 'student/recommendations.html', context)

@login_required
@student_required
def student_attendance(request):
    """View attendance records."""
    student = request.user.studentprofile
    
    # Get attendance records
    attendance_records = Attendance.objects.filter(
        student=student
    ).select_related('timetable_entry__subject', 'timetable_entry__teacher').order_by('-date')
    
    # Calculate overall statistics
    total_classes = attendance_records.count()
    present_classes = attendance_records.filter(status='present').count()
    absent_classes = attendance_records.filter(status='absent').count()
    late_classes = attendance_records.filter(status='late').count()
    
    overall_percentage = (present_classes / total_classes * 100) if total_classes > 0 else 0
    
    context = {
        'student': student,
        'attendance_records': attendance_records[:50],  # Limit to recent 50
        'total_classes': total_classes,
        'present_classes': present_classes,
        'absent_classes': absent_classes,
        'late_classes': late_classes,
        'overall_percentage': round(overall_percentage, 1)
    }
    
    return render(request, 'student/attendance.html', context)
