from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import json

from utils.ai_service import ai_service
from .models import AIChat, ChatMessage, PerformanceInsight

@login_required
@csrf_exempt
def ai_chat_api(request):
    """AI Chat API endpoint."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            message = data.get('message', '').strip()
            
            if not message:
                return JsonResponse({'error': 'Message is required'}, status=400)
            
            # Generate AI response
            response = ai_service.chat_response(message)
            
            return JsonResponse({
                'response': response,
                'status': 'success'
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'error': 'An error occurred'}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@login_required
def generate_recommendation(request):
    """Generate AI recommendation."""
    if request.method == 'POST':
        try:
            # Sample student data
            student_data = {
                'name': request.user.get_full_name(),
                'course': 'B.Tech',
                'year': 2,
                'subjects': ['Data Structures', 'Algorithms', 'Math'],
                'attendance_rate': 85.5,
                'performance_trend': 'Good'
            }
            
            recommendation = ai_service.generate_study_recommendation(student_data)
            
            return JsonResponse({
                'recommendation': recommendation,
                'status': 'success'
            })
            
        except Exception as e:
            return JsonResponse({'error': 'Failed to generate recommendation'}, status=500)
    
    return JsonResponse({'error': 'Method not allowed'}, status=405)

@login_required
def analytics_dashboard(request):
    """Analytics dashboard."""
    insights = PerformanceInsight.objects.all()[:10]
    
    context = {
        'insights': insights
    }
    
    return render(request, 'ai_features/analytics.html', context)

@login_required
def performance_insights(request):
    """Performance insights view."""
    insights = PerformanceInsight.objects.filter(
        is_actionable=True
    ).order_by('-impact_score')[:5]
    
    context = {
        'insights': insights
    }
    
    return render(request, 'ai_features/insights.html', context)
