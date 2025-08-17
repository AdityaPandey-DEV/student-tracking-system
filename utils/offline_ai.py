"""
Offline AI Service - No external API required
Provides intelligent responses using pattern matching and predefined knowledge.
"""

import re
import random
from datetime import datetime, timedelta
from typing import Dict, List

class OfflineAI:
    """Intelligent offline AI that provides contextual responses without external APIs."""
    
    def __init__(self):
        self.knowledge_base = self._load_knowledge_base()
        self.conversation_memory = []
        
    def _load_knowledge_base(self) -> Dict:
        """Load predefined knowledge base for intelligent responses."""
        return {
            "study_tips": [
                "Use the Pomodoro Technique: Study for 25 minutes, then take a 5-minute break.",
                "Create a dedicated study space free from distractions.",
                "Practice active recall by testing yourself instead of just re-reading notes.",
                "Use spaced repetition to improve long-term retention.",
                "Break large topics into smaller, manageable chunks.",
                "Teach the concept to someone else to reinforce your understanding.",
                "Use visual aids like mind maps and diagrams for complex topics.",
                "Take regular breaks to maintain focus and prevent burnout."
            ],
            
            "schedule_advice": [
                "Schedule difficult subjects during your peak energy hours.",
                "Block similar subjects together to maintain mental flow.",
                "Leave buffer time between classes for transitions and unexpected delays.",
                "Plan your most challenging tasks when you're most alert.",
                "Include time for meals and adequate rest in your schedule.",
                "Review your timetable weekly and adjust as needed.",
                "Use color-coding to visually organize different subjects.",
                "Set reminders for important deadlines and exams."
            ],
            
            "exam_preparation": [
                "Start preparing at least 2-3 weeks before the exam.",
                "Create a study schedule that covers all topics systematically.",
                "Practice with past papers and sample questions.",
                "Form study groups to discuss difficult concepts.",
                "Focus more time on your weaker subjects.",
                "Get enough sleep, especially the night before the exam.",
                "Eat nutritious meals to maintain energy and focus.",
                "Stay calm and manage exam anxiety through relaxation techniques."
            ],
            
            "time_management": [
                "Prioritize tasks using the Eisenhower Matrix (urgent vs important).",
                "Set SMART goals: Specific, Measurable, Achievable, Relevant, Time-bound.",
                "Use a planner or digital calendar to track assignments and deadlines.",
                "Eliminate time-wasters and distractions during study time.",
                "Learn to say no to activities that don't align with your priorities.",
                "Batch similar tasks together for better efficiency.",
                "Set realistic expectations for what you can accomplish each day.",
                "Review your progress regularly and adjust your approach as needed."
            ],
            
            "subject_specific": {
                "mathematics": [
                    "Practice problems daily to build problem-solving skills.",
                    "Understand the underlying concepts, don't just memorize formulas.",
                    "Work through examples step by step before attempting problems alone.",
                    "Keep a formula sheet with key equations and theorems.",
                    "Check your work by substituting answers back into original problems."
                ],
                "physics": [
                    "Connect theoretical concepts to real-world applications.",
                    "Draw diagrams and visualize problems before solving.",
                    "Practice dimensional analysis to check your calculations.",
                    "Focus on understanding the physical meaning behind equations.",
                    "Solve numerical problems to reinforce theoretical knowledge."
                ],
                "chemistry": [
                    "Memorize the periodic table and common chemical formulas.",
                    "Practice balancing chemical equations regularly.",
                    "Understand the patterns and trends in chemical properties.",
                    "Connect molecular structure to chemical behavior.",
                    "Use visual aids to understand complex chemical processes."
                ],
                "biology": [
                    "Use diagrams and flowcharts to understand biological processes.",
                    "Connect different biological systems and their interactions.",
                    "Practice labeling anatomical diagrams and biological structures.",
                    "Understand the hierarchy from molecules to organisms to ecosystems.",
                    "Use mnemonics to remember complex biological terms and processes."
                ],
                "english": [
                    "Read regularly to improve vocabulary and comprehension.",
                    "Practice writing essays with clear structure and arguments.",
                    "Analyze literary techniques and their effects in texts.",
                    "Keep a vocabulary journal with new words and their meanings.",
                    "Practice different types of writing: narrative, persuasive, analytical."
                ],
                "history": [
                    "Create timelines to understand chronological relationships.",
                    "Focus on cause and effect relationships in historical events.",
                    "Use maps to understand geographical context of events.",
                    "Connect historical events to their modern implications.",
                    "Practice analyzing primary and secondary sources."
                ]
            }
        }
    
    def chat(self, message: str, context: Dict = None) -> str:
        """Process user message and return intelligent response."""
        # Store conversation for context
        self.conversation_memory.append({
            "user": message,
            "timestamp": datetime.now(),
            "context": context
        })
        
        # Keep only recent conversation history
        if len(self.conversation_memory) > 10:
            self.conversation_memory = self.conversation_memory[-10:]
        
        # Analyze message and generate response
        response = self._generate_response(message, context)
        
        # Store AI response
        self.conversation_memory[-1]["ai"] = response
        
        return response
    
    def _generate_response(self, message: str, context: Dict = None) -> str:
        """Generate intelligent response based on message content."""
        message_lower = message.lower()
        
        # Greeting responses
        if any(word in message_lower for word in ['hello', 'hi', 'hey', 'good morning', 'good afternoon']):
            greetings = [
                "Hello! I'm here to help you with your studies and academic planning.",
                "Hi there! How can I assist you with your timetable and learning today?",
                "Hey! Ready to make your academic journey more successful?",
                "Good to see you! What academic questions can I help you with?"
            ]
            return random.choice(greetings)
        
        # Schedule and timetable queries
        elif any(word in message_lower for word in ['schedule', 'timetable', 'class', 'when', 'time']):
            if 'next' in message_lower:
                return self._get_next_class_info(context)
            elif 'today' in message_lower:
                return self._get_today_schedule(context)
            elif 'optimize' in message_lower or 'improve' in message_lower:
                return self._get_schedule_optimization()
            else:
                return self._get_general_schedule_advice()
        
        # Study help and tips
        elif any(word in message_lower for word in ['study', 'learn', 'tip', 'how to study']):
            return self._get_study_tips(message_lower)
        
        # Exam preparation
        elif any(word in message_lower for word in ['exam', 'test', 'quiz', 'preparation']):
            return self._get_exam_advice(message_lower)
        
        # Assignment help
        elif any(word in message_lower for word in ['assignment', 'homework', 'project', 'deadline']):
            return self._get_assignment_help(context)
        
        # Subject-specific help
        elif any(subject in message_lower for subject in ['math', 'physics', 'chemistry', 'biology', 'english', 'history']):
            return self._get_subject_help(message_lower)
        
        # Time management
        elif any(word in message_lower for word in ['time', 'manage', 'organize', 'plan', 'priority']):
            return self._get_time_management_advice()
        
        # Grades and performance
        elif any(word in message_lower for word in ['grade', 'score', 'performance', 'improve', 'better']):
            return self._get_performance_advice()
        
        # Stress and motivation
        elif any(word in message_lower for word in ['stress', 'anxiety', 'worried', 'motivation', 'tired']):
            return self._get_wellness_advice()
        
        # Default intelligent response
        else:
            return self._get_contextual_response(message, context)
    
    def _get_next_class_info(self, context: Dict = None) -> str:
        """Generate next class information."""
        classes = ["Mathematics", "Physics", "Chemistry", "Biology", "English", "History", "Computer Science"]
        rooms = ["101", "102", "203", "Lab A", "Lab B", "Library", "Hall 1"]
        
        next_class = random.choice(classes)
        room = random.choice(rooms)
        time = (datetime.now() + timedelta(minutes=random.randint(15, 120))).strftime("%I:%M %p")
        
        return f"Your next class is {next_class} at {time} in Room {room}. " \
               f"Make sure to bring your textbook and any required materials!"
    
    def _get_today_schedule(self, context: Dict = None) -> str:
        """Generate today's schedule overview."""
        schedules = [
            "Today you have 4 classes: Math (9:00 AM), Physics (10:30 AM), Chemistry Lab (2:00 PM), and English (3:30 PM).",
            "Your schedule includes Biology (8:00 AM), History (10:00 AM), Math (1:00 PM), and Computer Science (3:00 PM).",
            "You have Physics Lab (9:00 AM), English (11:00 AM), Math (2:00 PM), and Chemistry (3:30 PM) today.",
        ]
        return random.choice(schedules) + " Don't forget to check for any last-minute changes!"
    
    def _get_schedule_optimization(self) -> str:
        """Provide schedule optimization advice."""
        advice = random.choice(self.knowledge_base["schedule_advice"])
        return f"Here's a tip to optimize your schedule: {advice} " \
               f"Would you like more specific advice about organizing your timetable?"
    
    def _get_general_schedule_advice(self) -> str:
        """Provide general schedule advice."""
        return "Your timetable is designed to balance different subjects throughout the week. " \
               "Make sure to check it regularly for any updates or changes. " \
               "If you need help optimizing your study schedule, I can provide personalized tips!"
    
    def _get_study_tips(self, message: str) -> str:
        """Provide study tips based on message content."""
        tip = random.choice(self.knowledge_base["study_tips"])
        return f"Here's a great study tip: {tip} " \
               f"Consistent application of good study techniques will significantly improve your learning outcomes!"
    
    def _get_exam_advice(self, message: str) -> str:
        """Provide exam preparation advice."""
        advice = random.choice(self.knowledge_base["exam_preparation"])
        return f"For exam preparation: {advice} " \
               f"Remember, consistent preparation is key to exam success. Start early and stay organized!"
    
    def _get_assignment_help(self, context: Dict = None) -> str:
        """Provide assignment help."""
        return "To manage assignments effectively: Break large projects into smaller tasks, " \
               "set mini-deadlines for each part, and start working on them as soon as possible. " \
               "Use a planner to track all due dates and prioritize based on deadlines and difficulty."
    
    def _get_subject_help(self, message: str) -> str:
        """Provide subject-specific help."""
        subjects = {
            'math': 'mathematics', 'physics': 'physics', 'chemistry': 'chemistry',
            'biology': 'biology', 'english': 'english', 'history': 'history'
        }
        
        for key, subject in subjects.items():
            if key in message:
                if subject in self.knowledge_base["subject_specific"]:
                    tip = random.choice(self.knowledge_base["subject_specific"][subject])
                    return f"For {subject.title()}: {tip} " \
                           f"Each subject has its own learning strategies. Focus on understanding rather than memorization!"
        
        return "Each subject requires different study approaches. Focus on understanding concepts, " \
               "practice regularly, and don't hesitate to ask for help when needed!"
    
    def _get_time_management_advice(self) -> str:
        """Provide time management advice."""
        tip = random.choice(self.knowledge_base["time_management"])
        return f"Time management tip: {tip} " \
               f"Effective time management is crucial for academic success!"
    
    def _get_performance_advice(self) -> str:
        """Provide performance improvement advice."""
        return "To improve your academic performance: Set specific goals, track your progress, " \
               "identify weak areas and focus extra effort there, seek help when needed, " \
               "and maintain consistent study habits. Remember, improvement takes time!"
    
    def _get_wellness_advice(self) -> str:
        """Provide wellness and motivation advice."""
        return "Academic stress is normal, but manageable! Take regular breaks, maintain a healthy " \
               "sleep schedule, exercise regularly, and don't hesitate to talk to someone if you're " \
               "feeling overwhelmed. Your mental health is just as important as your grades!"
    
    def _get_contextual_response(self, message: str, context: Dict = None) -> str:
        """Generate contextual response for general queries."""
        responses = [
            "That's an interesting question! I'm here to help you succeed academically. " +
            "I can assist with study tips, schedule management, exam preparation, and more.",
            
            "Thanks for asking! As your academic assistant, I can help you with timetable questions, " +
            "study strategies, subject-specific advice, and academic planning.",
            
            "I understand you're looking for guidance. I specialize in helping students with " +
            "their academic journey - from organizing schedules to developing effective study habits.",
            
            f"Regarding your question about '{message[:50]}...', I'd be happy to help! " +
            "I can provide advice on studying, time management, and academic success strategies."
        ]
        
        return random.choice(responses)

# Create singleton instance
offline_ai = OfflineAI()

def get_ai_response(message: str, context: Dict = None) -> str:
    """Get AI response using offline AI."""
    return offline_ai.chat(message, context)
