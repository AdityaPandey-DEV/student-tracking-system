"""
AI Service integration for Enhanced Timetable System.
Handles OpenAI API calls for chat, recommendations, and analytics.
"""

from django.conf import settings
import logging
from typing import Dict, List
import json
from datetime import datetime, timedelta

try:
    from openai import OpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# Configure logging
logger = logging.getLogger(__name__)

class AIService:
    """AI service wrapper for OpenAI integration."""
    
    def __init__(self):
        self.client = None
        if OPENAI_AVAILABLE and hasattr(settings, 'OPENAI_API_KEY') and settings.OPENAI_API_KEY:
            self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.mock_mode = settings.DEBUG or not OPENAI_AVAILABLE or not hasattr(settings, 'OPENAI_API_KEY') or not settings.OPENAI_API_KEY
    
    def chat_with_ai(self, message: str, context: Dict = None) -> str:
        """Chat with AI for student queries."""
        try:
            if self.mock_mode:
                return self._mock_chat_response(message, context)
            
            system_prompt = self._build_system_prompt(context)
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI chat error: {str(e)}")
            return self._mock_chat_response(message, context)
    
    def generate_study_recommendation(self, student_data: Dict) -> Dict:
        """Generate personalized study recommendations."""
        try:
            if self.mock_mode:
                return self._mock_study_recommendations(student_data)
            
            if not hasattr(settings, 'OPENAI_API_KEY') or not settings.OPENAI_API_KEY:
                return self._mock_study_recommendations(student_data)
            
            prompt = self._build_recommendation_prompt(student_data)
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an AI study advisor for students. Provide personalized study recommendations based on their academic data."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=800,
                temperature=0.6
            )
            
            # Parse the response to structured format
            content = response.choices[0].message.content.strip()
            return self._parse_recommendation_response(content)
            
        except Exception as e:
            logger.error(f"Study recommendation error: {str(e)}")
            return self._mock_study_recommendations(student_data)
    
    def optimize_timetable(self, timetable_data: Dict) -> Dict:
        """Optimize timetable using AI suggestions."""
        try:
            if self.mock_mode:
                return self._mock_timetable_optimization(timetable_data)
            
            if not hasattr(settings, 'OPENAI_API_KEY') or not settings.OPENAI_API_KEY:
                return self._mock_timetable_optimization(timetable_data)
            
            prompt = self._build_optimization_prompt(timetable_data)
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a timetable optimization expert. Analyze schedules and suggest improvements for better learning outcomes."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=600,
                temperature=0.5
            )
            
            content = response.choices[0].message.content.strip()
            return self._parse_optimization_response(content)
            
        except Exception as e:
            logger.error(f"Timetable optimization error: {str(e)}")
            return self._mock_timetable_optimization(timetable_data)
    
    def analyze_performance(self, performance_data: Dict) -> Dict:
        """Analyze student performance using AI."""
        try:
            if self.mock_mode:
                return self._mock_performance_analysis(performance_data)
            
            if not hasattr(settings, 'OPENAI_API_KEY') or not settings.OPENAI_API_KEY:
                return self._mock_performance_analysis(performance_data)
            
            prompt = self._build_analysis_prompt(performance_data)
            
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an educational data analyst. Analyze student performance data and provide insights."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=700,
                temperature=0.4
            )
            
            content = response.choices[0].message.content.strip()
            return self._parse_analysis_response(content)
            
        except Exception as e:
            logger.error(f"Performance analysis error: {str(e)}")
            return self._mock_performance_analysis(performance_data)
    
    # Helper methods for building prompts
    def _build_system_prompt(self, context: Dict = None) -> str:
        """Build system prompt for chat."""
        base_prompt = "You are an AI assistant for an Enhanced Timetable System. Help students with their academic queries, schedule questions, and study advice."
        
        if context:
            if context.get('student_name'):
                base_prompt += f" You are helping {context['student_name']}."
            if context.get('current_courses'):
                courses = ", ".join(context['current_courses'])
                base_prompt += f" They are currently enrolled in: {courses}."
        
        return base_prompt
    
    def _build_recommendation_prompt(self, student_data: Dict) -> str:
        """Build prompt for study recommendations."""
        return f"""
        Generate study recommendations for a student with the following data:
        - Current GPA: {student_data.get('gpa', 'N/A')}
        - Subjects: {', '.join(student_data.get('subjects', []))}
        - Weak subjects: {', '.join(student_data.get('weak_subjects', []))}
        - Study hours per day: {student_data.get('study_hours', 'N/A')}
        - Upcoming exams: {student_data.get('upcoming_exams', 'None')}
        
        Please provide specific, actionable study recommendations.
        """
    
    def _build_optimization_prompt(self, timetable_data: Dict) -> str:
        """Build prompt for timetable optimization."""
        return f"""
        Analyze this timetable and suggest optimizations:
        - Total classes per day: {timetable_data.get('classes_per_day', 'N/A')}
        - Subject distribution: {timetable_data.get('subject_distribution', {})}
        - Break times: {timetable_data.get('break_times', [])}
        - Peak learning hours: {timetable_data.get('peak_hours', 'N/A')}
        
        Suggest improvements for better learning outcomes.
        """
    
    def _build_analysis_prompt(self, performance_data: Dict) -> str:
        """Build prompt for performance analysis."""
        return f"""
        Analyze this student performance data:
        - Attendance rate: {performance_data.get('attendance_rate', 'N/A')}%
        - Grade trends: {performance_data.get('grade_trends', {})}
        - Subject performance: {performance_data.get('subject_performance', {})}
        - Assignment completion: {performance_data.get('assignment_completion', 'N/A')}%
        
        Provide insights and recommendations for improvement.
        """
    
    # Mock response methods for development
    def _mock_chat_response(self, message: str, context: Dict = None) -> str:
        """Generate mock chat response."""
        responses = [
            "I understand your question about the timetable. Let me help you with that.",
            "That's a great question! Based on your current schedule, I'd recommend...",
            "I can help you with that. Here's what you should know about your classes:",
            "Let me provide some guidance on that topic for your studies.",
        ]
        
        # Simple keyword-based responses
        if 'schedule' in message.lower() or 'timetable' in message.lower():
            return "Your next class is in 30 minutes. You have Mathematics in Room 101. Don't forget to bring your calculator!"
        elif 'study' in message.lower() or 'exam' in message.lower():
            return "For your upcoming exams, I recommend creating a study schedule. Focus on your weaker subjects first, and allocate more time to practice problems."
        elif 'assignment' in message.lower():
            return "You have 2 assignments due this week. The Physics assignment is due tomorrow, and the English essay is due on Friday."
        else:
            return f"Thanks for your question: '{message}'. I'm here to help with your academic needs. Feel free to ask about your schedule, assignments, or study tips!"
    
    def _mock_study_recommendations(self, student_data: Dict) -> Dict:
        """Generate mock study recommendations."""
        return {
            "priority_subjects": ["Mathematics", "Physics", "Chemistry"],
            "study_plan": [
                {
                    "subject": "Mathematics",
                    "hours_per_week": 8,
                    "focus_areas": ["Calculus", "Algebra", "Trigonometry"],
                    "resources": ["Khan Academy", "Textbook Chapter 5-7", "Practice Problems"]
                },
                {
                    "subject": "Physics", 
                    "hours_per_week": 6,
                    "focus_areas": ["Mechanics", "Thermodynamics"],
                    "resources": ["Lab experiments", "Video lectures", "Problem sets"]
                }
            ],
            "daily_schedule": {
                "morning": "Review previous day's topics (30 min)",
                "afternoon": "Practice problems (1-2 hours)",
                "evening": "Read ahead for next day (45 min)"
            },
            "exam_strategy": "Focus on weak areas first, create summary notes, take practice tests",
            "confidence_score": 85
        }
    
    def _mock_timetable_optimization(self, timetable_data: Dict) -> Dict:
        """Generate mock timetable optimization suggestions."""
        return {
            "optimization_score": 78,
            "suggestions": [
                {
                    "type": "scheduling",
                    "priority": "high",
                    "description": "Move Mathematics to morning hours (9-11 AM) for better concentration"
                },
                {
                    "type": "breaks",
                    "priority": "medium", 
                    "description": "Add 15-minute break between consecutive theory classes"
                },
                {
                    "type": "subject_distribution",
                    "priority": "medium",
                    "description": "Balance theory and practical subjects throughout the week"
                }
            ],
            "predicted_improvements": {
                "learning_efficiency": "+15%",
                "student_satisfaction": "+12%",
                "attendance_rate": "+8%"
            }
        }
    
    def _mock_performance_analysis(self, performance_data: Dict) -> Dict:
        """Generate mock performance analysis."""
        return {
            "overall_score": 82,
            "strengths": ["Mathematics", "Computer Science", "Regular attendance"],
            "areas_for_improvement": ["Physics lab reports", "English essays", "Time management"],
            "trends": {
                "attendance": "Stable at 92%",
                "grades": "Improving trend over last 3 months",
                "assignment_completion": "98% completion rate"
            },
            "recommendations": [
                "Join Physics study group for better lab understanding",
                "Use writing center resources for English improvements", 
                "Consider time management workshops"
            ],
            "predicted_gpa": 3.7,
            "confidence_interval": "±0.2"
        }
    
    # Response parsing methods (for real API responses)
    def _parse_recommendation_response(self, content: str) -> Dict:
        """Parse AI recommendation response to structured format."""
        # This would parse the AI response into structured data
        # For now, return a mock structure
        return self._mock_study_recommendations({})
    
    def _parse_optimization_response(self, content: str) -> Dict:
        """Parse AI optimization response to structured format."""
        return self._mock_timetable_optimization({})
    
    def _parse_analysis_response(self, content: str) -> Dict:
        """Parse AI analysis response to structured format."""
        return self._mock_performance_analysis({})

# Create a singleton instance
ai_service = AIService()
