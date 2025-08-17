"""
URL configuration for accounts app.
"""

from django.urls import path
from . import views
from .student_views import (
    student_dashboard, student_timetable, student_subjects,
    ai_chat, student_recommendations, student_attendance
)
from .admin_views import (
    admin_dashboard, manage_courses, manage_teachers, manage_timetable, 
    manage_students, manage_announcements, ai_analytics
)
from .teacher_views import (
    teacher_dashboard, teacher_timetable, teacher_classes, teacher_students,
    mark_attendance, manage_materials, teacher_announcements, attendance_reports
)

app_name = 'accounts'

urlpatterns = [
    # Authentication URLs
    path('', views.landing_page, name='landing'),
    path('register/', views.register_choice, name='register_choice'),
    path('register/student/', views.student_register, name='student_register'),
    path('register/teacher/', views.teacher_register, name='teacher_register'),
    path('register/admin/', views.admin_register, name='admin_register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('reset-password/', views.reset_password, name='reset_password'),
    path('resend-registration-otp/', views.resend_registration_otp, name='resend_registration_otp'),
    path('profile/', views.profile, name='profile'),
    
    # Student URLs
    path('student/dashboard/', student_dashboard, name='student_dashboard'),
    path('student/timetable/', student_timetable, name='student_timetable'),
    path('student/subjects/', student_subjects, name='student_subjects'),
    path('student/ai-chat/', ai_chat, name='student_ai_chat'),
    path('student/recommendations/', student_recommendations, name='student_recommendations'),
    path('student/attendance/', student_attendance, name='student_attendance'),
    
    # Admin URLs
    path('admin/dashboard/', admin_dashboard, name='admin_dashboard'),
    path('admin/courses/', manage_courses, name='manage_courses'),
    path('admin/teachers/', manage_teachers, name='manage_teachers'),
    path('admin/timetable/', manage_timetable, name='manage_timetable'),
    path('admin/students/', manage_students, name='manage_students'),
    path('admin/announcements/', manage_announcements, name='manage_announcements'),
    path('admin/ai-analytics/', ai_analytics, name='ai_analytics'),
    
    # Teacher URLs
    path('teacher/dashboard/', teacher_dashboard, name='teacher_dashboard'),
    path('teacher/timetable/', teacher_timetable, name='teacher_timetable'),
    path('teacher/classes/', teacher_classes, name='teacher_classes'),
    path('teacher/students/', teacher_students, name='teacher_students'),
    path('teacher/attendance/', mark_attendance, name='mark_attendance'),
    path('teacher/materials/', manage_materials, name='manage_materials'),
    path('teacher/announcements/', teacher_announcements, name='teacher_announcements'),
    path('teacher/reports/', attendance_reports, name='attendance_reports'),
]
