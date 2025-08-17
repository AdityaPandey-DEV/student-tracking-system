from django.contrib import admin
from .models import (
    AIChat, ChatMessage, TimetableSuggestion, StudyRecommendation,
    PerformanceInsight, AIAnalyticsReport, SmartNotification,
    StudyMaterial, Assignment
)

class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ('timestamp',)
    fields = ('sender', 'message', 'timestamp')

@admin.register(AIChat)
class AIChatAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'user', 'chat_type', 'created_at', 'updated_at')
    list_filter = ('chat_type', 'created_at')
    search_fields = ('session_id', 'user__username')
    ordering = ('-updated_at',)
    inlines = [ChatMessageInline]
    readonly_fields = ('created_at', 'updated_at')

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('chat', 'sender', 'get_message_preview', 'timestamp')
    list_filter = ('sender', 'timestamp')
    search_fields = ('chat__session_id', 'message')
    ordering = ('-timestamp',)
    readonly_fields = ('timestamp',)
    
    def get_message_preview(self, obj):
        return obj.message[:50] + ('...' if len(obj.message) > 50 else '')
    get_message_preview.short_description = 'Message Preview'

@admin.register(TimetableSuggestion)
class TimetableSuggestionAdmin(admin.ModelAdmin):
    list_display = ('get_class_info', 'optimization_score', 'conflicts_resolved', 'status', 'generated_by', 'created_at')
    list_filter = ('status', 'course', 'year', 'academic_year', 'semester', 'created_at')
    search_fields = ('course', 'generated_by__username')
    ordering = ('-optimization_score', '-created_at')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_class_info(self, obj):
        return f"{obj.course} Y{obj.year}{obj.section}"
    get_class_info.short_description = 'Class'

@admin.register(StudyRecommendation)
class StudyRecommendationAdmin(admin.ModelAdmin):
    list_display = ('title', 'student', 'recommendation_type', 'priority', 'confidence_score', 'is_read', 'created_at')
    list_filter = ('recommendation_type', 'priority', 'is_read', 'is_implemented', 'created_at')
    search_fields = ('title', 'student__roll_number', 'student__user__first_name')
    ordering = ('-priority', '-confidence_score', '-created_at')
    readonly_fields = ('created_at',)
    filter_horizontal = ('subjects',)

@admin.register(PerformanceInsight)
class PerformanceInsightAdmin(admin.ModelAdmin):
    list_display = ('title', 'insight_type', 'scope', 'confidence_score', 'impact_score', 'is_actionable', 'created_at')
    list_filter = ('insight_type', 'scope', 'is_actionable', 'is_viewed', 'created_at')
    search_fields = ('title', 'description')
    ordering = ('-impact_score', '-confidence_score', '-created_at')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(AIAnalyticsReport)
class AIAnalyticsReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'report_type', 'period', 'start_date', 'end_date', 'is_published', 'views_count', 'created_at')
    list_filter = ('report_type', 'period', 'is_published', 'created_at')
    search_fields = ('title', 'summary')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at', 'views_count')

@admin.register(SmartNotification)
class SmartNotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'recipient', 'notification_type', 'priority', 'confidence_score', 'is_read', 'created_at')
    list_filter = ('notification_type', 'priority', 'is_read', 'is_dismissed', 'created_at')
    search_fields = ('title', 'recipient__username', 'message')
    ordering = ('-priority', '-created_at')
    readonly_fields = ('created_at', 'read_at')

@admin.register(StudyMaterial)
class StudyMaterialAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'course', 'year', 'section', 'material_type', 'uploaded_by', 'is_published', 'created_at')
    list_filter = ('material_type', 'course', 'year', 'is_published', 'created_at')
    search_fields = ('title', 'description', 'subject__name', 'uploaded_by__username')
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    
@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'course', 'year', 'section', 'due_date', 'max_marks', 'status', 'created_by', 'created_at')
    list_filter = ('status', 'course', 'year', 'is_published', 'due_date', 'created_at')
    search_fields = ('title', 'description', 'subject__name', 'created_by__username')
    ordering = ('-due_date',)
    readonly_fields = ('created_at', 'updated_at')
    
    def get_overdue_status(self, obj):
        return obj.is_overdue
    get_overdue_status.boolean = True
    get_overdue_status.short_description = 'Overdue'
