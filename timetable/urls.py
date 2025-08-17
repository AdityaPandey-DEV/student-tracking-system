"""
URL configuration for timetable app.
"""

from django.urls import path
from . import views

app_name = 'timetable'

urlpatterns = [
    path('setup/', views.initial_setup, name='initial_setup'),
    path('courses/', views.course_list, name='course_list'),
    path('subjects/', views.subject_list, name='subject_list'),
    path('teachers/', views.teacher_list, name='teacher_list'),
    path('rooms/', views.room_list, name='room_list'),
]
