"""
URL configuration for AI features app.
"""

from django.urls import path
from . import views

app_name = 'ai_features'

urlpatterns = [
    path('chat/', views.ai_chat_api, name='ai_chat_api'),
    path('recommendations/', views.generate_recommendation, name='generate_recommendation'),
    path('analytics/', views.analytics_dashboard, name='analytics_dashboard'),
    path('insights/', views.performance_insights, name='performance_insights'),
]
