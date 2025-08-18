"""
URL configuration for API endpoints
These URLs handle AJAX requests from the frontend JavaScript
"""

from django.urls import path
from . import api_views
from . import admin_api_views
from . import teacher_api_views
from . import student_api_views
from . import api_views as core_api_views

app_name = 'api'

urlpatterns = [
    # Announcement API endpoints
    path('announcements/<int:announcement_id>/', api_views.get_announcement_details, name='announcement_details'),
    path('announcements/<int:announcement_id>/delete/', api_views.delete_announcement, name='delete_announcement'),
    
    # Search API endpoints
    path('search/', api_views.search_content, name='search_content'),
    
    # Recommendation API endpoints
    path('recommendations/generate/', api_views.generate_recommendations, name='generate_recommendations'),
    path('recommendations/<int:recommendation_id>/dismiss/', api_views.dismiss_recommendation, name='dismiss_recommendation'),
    
    # Attendance API endpoints
    path('attendance/report/', api_views.generate_attendance_report, name='attendance_report'),
    
    # AI Chat API endpoints
    path('ai/chat/', api_views.ai_chat_response, name='ai_chat_response'),
    path('student/context/', api_views.get_student_context, name='student_context'),
    
    # Admin API endpoints
    path('admin/teachers/<int:teacher_id>/', admin_api_views.get_teacher_details, name='admin_teacher_details'),
    path('admin/teachers/<int:teacher_id>/update/', admin_api_views.update_teacher, name='admin_update_teacher'),
    path('admin/assignments/<int:assignment_id>/delete/', admin_api_views.delete_teacher_assignment, name='admin_delete_assignment'),
    path('admin/students/<int:student_id>/', admin_api_views.get_student_details, name='admin_student_details'),
    path('admin/students/<int:student_id>/toggle-status/', admin_api_views.toggle_student_status, name='admin_toggle_student_status'),
    path('admin/students/<int:student_id>/update/', admin_api_views.update_student, name='admin_update_student'),
    path('admin/students/export/', admin_api_views.export_students, name='admin_export_students'),
    path('admin/timetable/<int:entry_id>/', admin_api_views.get_timetable_entry, name='admin_timetable_entry'),
    path('admin/timetable/<int:entry_id>/update/', admin_api_views.update_timetable_entry, name='admin_update_timetable_entry'),
    path('admin/timetable/<int:entry_id>/delete/', admin_api_views.delete_timetable_entry, name='admin_delete_timetable_entry'),
    path('admin/timetable/export/', admin_api_views.export_timetable, name='admin_export_timetable'),
    path('admin/timetable/entries/', admin_api_views.get_filtered_timetable_entries, name='admin_filtered_timetable_entries'),
    path('admin/ai-suggestions/<int:suggestion_id>/', admin_api_views.get_ai_suggestion, name='admin_ai_suggestion'),
    path('admin/updates/', admin_api_views.check_updates, name='admin_check_updates'),
    
    # Teacher API endpoints
    path('teacher/class/<int:class_id>/students/', teacher_api_views.get_class_students, name='teacher_get_students'),
    path('teacher/attendance/save/', teacher_api_views.save_attendance, name='teacher_save_attendance'),
    path('teacher/attendance/report/<int:subject_id>/', teacher_api_views.generate_attendance_report, name='teacher_generate_report'),
    path('teacher/attendance/summary/', teacher_api_views.get_attendance_summary, name='teacher_attendance_summary'),
    path('teacher/material/upload/', teacher_api_views.upload_study_material, name='teacher_upload_material'),
    path('teacher/material/<int:material_id>/delete/', teacher_api_views.delete_study_material, name='teacher_delete_material'),
    path('teacher/announcement/send/', teacher_api_views.send_announcement, name='teacher_send_announcement'),
    path('teacher/class/<int:class_id>/details/', teacher_api_views.get_class_details, name='teacher_get_class_details'),
    path('teacher/updates/', teacher_api_views.check_teacher_updates, name='teacher_check_updates'),
    
    # Student API endpoints
    path('student/timetable/', student_api_views.get_my_timetable, name='student_get_timetable'),
    path('student/attendance/', student_api_views.get_my_attendance, name='student_get_attendance'),
    path('student/materials/', student_api_views.get_my_study_materials, name='student_get_materials'),
    path('student/materials/<int:material_id>/', student_api_views.get_material_details, name='student_material_details'),
    path('student/announcements/', student_api_views.get_my_announcements, name='student_get_announcements'),
    path('student/dashboard/stats/', student_api_views.get_dashboard_stats, name='student_dashboard_stats'),
    path('student/updates/', student_api_views.check_student_updates, name='student_check_updates'),
    # Health endpoint
    path('health/db/', core_api_views.db_health, name='db_health'),
]
