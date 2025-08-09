from django.db import models
from accounts.models import User, StudentProfile
from timetable.models import TimetableEntry, Subject
from django.utils import timezone
import json

class AIChat(models.Model):
    """AI Chat conversations with students and admins."""
    CHAT_TYPE_CHOICES = [
        ('timetable_query', 'Timetable Query'),
        ('academic_help', 'Academic Help'),
        ('schedule_optimization', 'Schedule Optimization'),
        ('general_query', 'General Query'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_chats')
    chat_type = models.CharField(max_length=30, choices=CHAT_TYPE_CHOICES, default='general_query')
    session_id = models.CharField(max_length=100, help_text="Unique session identifier")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"Chat {self.session_id} - {self.user.username} - {self.chat_type}"

class ChatMessage(models.Model):
    """Individual messages in AI chat conversations."""
    SENDER_CHOICES = [
        ('user', 'User'),
        ('ai', 'AI Assistant'),
    ]
    
    chat = models.ForeignKey(AIChat, on_delete=models.CASCADE, related_name='messages')
    sender = models.CharField(max_length=10, choices=SENDER_CHOICES)
    message = models.TextField()
    context_data = models.JSONField(default=dict, blank=True, help_text="Additional context for AI processing")
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['timestamp']
    
    def __str__(self):
        return f"{self.chat.session_id} - {self.sender}: {self.message[:50]}"

class TimetableSuggestion(models.Model):
    """AI-generated timetable suggestions and optimizations."""
    STATUS_CHOICES = [
        ('generated', 'Generated'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('implemented', 'Implemented'),
    ]
    
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='timetable_suggestions')
    course = models.CharField(max_length=50)
    year = models.IntegerField()
    section = models.CharField(max_length=5)
    academic_year = models.CharField(max_length=10)
    semester = models.IntegerField()
    suggestion_data = models.JSONField(help_text="Generated timetable data")
    optimization_score = models.FloatField(default=0.0, help_text="AI optimization score (0-100)")
    conflicts_resolved = models.IntegerField(default=0)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='generated')
    notes = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_suggestions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-optimization_score', '-created_at']
    
    def __str__(self):
        return f"Timetable Suggestion - {self.course} Y{self.year}{self.section} - Score: {self.optimization_score}"

class StudyRecommendation(models.Model):
    """AI-generated study recommendations for students."""
    RECOMMENDATION_TYPE_CHOICES = [
        ('subject_focus', 'Subject Focus'),
        ('study_schedule', 'Study Schedule'),
        ('exam_preparation', 'Exam Preparation'),
        ('attendance_improvement', 'Attendance Improvement'),
        ('performance_enhancement', 'Performance Enhancement'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='study_recommendations')
    recommendation_type = models.CharField(max_length=25, choices=RECOMMENDATION_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    subjects = models.ManyToManyField(Subject, blank=True, related_name='study_recommendations')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    is_read = models.BooleanField(default=False)
    is_implemented = models.BooleanField(default=False)
    confidence_score = models.FloatField(default=0.0, help_text="AI confidence score (0-100)")
    generated_data = models.JSONField(default=dict, help_text="AI analysis data used for recommendation")
    expires_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-priority', '-confidence_score', '-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.student.roll_number} - {self.priority}"
    
    def is_expired(self):
        """Check if recommendation is expired."""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False

class PerformanceInsight(models.Model):
    """AI-generated insights about student performance and trends."""
    INSIGHT_TYPE_CHOICES = [
        ('attendance_pattern', 'Attendance Pattern'),
        ('performance_trend', 'Performance Trend'),
        ('subject_difficulty', 'Subject Difficulty'),
        ('schedule_optimization', 'Schedule Optimization'),
        ('resource_allocation', 'Resource Allocation'),
        ('prediction', 'Performance Prediction'),
    ]
    
    SCOPE_CHOICES = [
        ('individual', 'Individual Student'),
        ('class', 'Class/Section'),
        ('course', 'Course'),
        ('year', 'Year'),
        ('institution', 'Institution-wide'),
    ]
    
    title = models.CharField(max_length=200)
    insight_type = models.CharField(max_length=25, choices=INSIGHT_TYPE_CHOICES)
    scope = models.CharField(max_length=15, choices=SCOPE_CHOICES)
    description = models.TextField()
    
    # Scope-specific fields
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, null=True, blank=True, related_name='performance_insights')
    course = models.CharField(max_length=50, blank=True)
    year = models.IntegerField(null=True, blank=True)
    section = models.CharField(max_length=5, blank=True)
    
    # Insight data
    insight_data = models.JSONField(help_text="Detailed analysis data")
    confidence_score = models.FloatField(help_text="AI confidence in this insight (0-100)")
    impact_score = models.FloatField(default=0.0, help_text="Potential impact score (0-100)")
    
    # Recommendations
    recommendations = models.TextField(blank=True, help_text="AI-generated recommendations based on this insight")
    
    # Metadata
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    is_actionable = models.BooleanField(default=True)
    is_viewed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-impact_score', '-confidence_score', '-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.scope} - Impact: {self.impact_score}"

class AIAnalyticsReport(models.Model):
    """Comprehensive AI-generated analytics reports."""
    REPORT_TYPE_CHOICES = [
        ('attendance_analytics', 'Attendance Analytics'),
        ('performance_analytics', 'Performance Analytics'),
        ('timetable_efficiency', 'Timetable Efficiency'),
        ('resource_utilization', 'Resource Utilization'),
        ('predictive_analysis', 'Predictive Analysis'),
        ('trend_analysis', 'Trend Analysis'),
    ]
    
    PERIOD_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('semester', 'Semester'),
        ('annual', 'Annual'),
    ]
    
    report_type = models.CharField(max_length=25, choices=REPORT_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    period = models.CharField(max_length=10, choices=PERIOD_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Scope filters
    course_filter = models.CharField(max_length=50, blank=True)
    year_filter = models.IntegerField(null=True, blank=True)
    section_filter = models.CharField(max_length=5, blank=True)
    
    # Report data
    report_data = models.JSONField(help_text="Complete analytics data")
    summary = models.TextField(help_text="AI-generated summary of key findings")
    key_insights = models.JSONField(default=list, help_text="List of key insights")
    recommendations = models.TextField(help_text="AI recommendations based on analysis")
    
    # Metadata
    generated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_reports')
    is_published = models.BooleanField(default=False)
    views_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.period} ({self.start_date} to {self.end_date})"
    
    def increment_views(self):
        """Increment the views count."""
        self.views_count += 1
        self.save(update_fields=['views_count'])

class SmartNotification(models.Model):
    """AI-generated smart notifications for users."""
    NOTIFICATION_TYPE_CHOICES = [
        ('schedule_reminder', 'Schedule Reminder'),
        ('deadline_alert', 'Deadline Alert'),
        ('performance_alert', 'Performance Alert'),
        ('attendance_warning', 'Attendance Warning'),
        ('optimization_suggestion', 'Optimization Suggestion'),
        ('system_update', 'System Update'),
    ]
    
    PRIORITY_CHOICES = [
        ('info', 'Info'),
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='smart_notifications')
    notification_type = models.CharField(max_length=25, choices=NOTIFICATION_TYPE_CHOICES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    
    # AI context
    ai_context = models.JSONField(default=dict, help_text="AI decision context for this notification")
    confidence_score = models.FloatField(default=0.0, help_text="AI confidence in notification relevance")
    
    # Notification state
    is_read = models.BooleanField(default=False)
    is_dismissed = models.BooleanField(default=False)
    read_at = models.DateTimeField(null=True, blank=True)
    
    # Scheduling
    scheduled_for = models.DateTimeField(null=True, blank=True, help_text="When to deliver this notification")
    expires_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-priority', '-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.recipient.username} - {self.priority}"
    
    def mark_as_read(self):
        """Mark notification as read."""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
    
    def is_expired(self):
        """Check if notification is expired."""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False

class StudyMaterial(models.Model):
    """Study materials uploaded by teachers for students."""
    MATERIAL_TYPE_CHOICES = [
        ('document', 'Document'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('presentation', 'Presentation'),
        ('link', 'External Link'),
        ('text', 'Text Content'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    subject = models.ForeignKey('timetable.Subject', on_delete=models.CASCADE)
    course = models.CharField(max_length=50)
    year = models.IntegerField()
    section = models.CharField(max_length=10, blank=True)
    material_type = models.CharField(max_length=20, choices=MATERIAL_TYPE_CHOICES, default='document')
    content = models.TextField(blank=True)  # For text content
    file_url = models.URLField(blank=True)  # For file/link content
    uploaded_by = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} - {self.subject.name} ({self.course} Year {self.year})"
    
    class Meta:
        ordering = ['-created_at']

class Assignment(models.Model):
    """Assignments created by teachers for students."""
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('closed', 'Closed'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    subject = models.ForeignKey('timetable.Subject', on_delete=models.CASCADE)
    course = models.CharField(max_length=50)
    year = models.IntegerField()
    section = models.CharField(max_length=10, blank=True)
    due_date = models.DateTimeField()
    max_marks = models.IntegerField(default=100)
    instructions = models.TextField(blank=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    is_published = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} - {self.subject.name} (Due: {self.due_date.strftime('%Y-%m-%d')})"
    
    @property
    def is_overdue(self):
        from django.utils import timezone
        return timezone.now() > self.due_date
    
    class Meta:
        ordering = ['-due_date']
