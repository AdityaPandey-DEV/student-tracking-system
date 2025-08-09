from django.contrib import admin
from .models import (
    Course, Subject, Teacher, TeacherSubject, TimeSlot, Room,
    TimetableEntry, Enrollment, Attendance, Announcement
)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'full_name', 'duration_years', 'is_active', 'created_at')
    list_filter = ('duration_years', 'is_active')
    search_fields = ('name', 'full_name')
    ordering = ('name',)

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'course', 'year', 'semester', 'credits', 'is_active')
    list_filter = ('course', 'year', 'semester', 'credits', 'is_active')
    search_fields = ('code', 'name', 'course__name')
    ordering = ('course', 'year', 'semester', 'name')

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'name', 'email', 'department', 'designation', 'is_active')
    list_filter = ('department', 'designation', 'is_active')
    search_fields = ('employee_id', 'name', 'email', 'department')
    ordering = ('name',)
    filter_horizontal = ('subjects',)

@admin.register(TeacherSubject)
class TeacherSubjectAdmin(admin.ModelAdmin):
    list_display = ('teacher', 'subject', 'assigned_at', 'is_active')
    list_filter = ('is_active', 'assigned_at')
    search_fields = ('teacher__name', 'subject__name', 'subject__code')
    ordering = ('-assigned_at',)

@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ('period_number', 'start_time', 'end_time', 'is_break', 'break_duration', 'is_active')
    list_filter = ('is_break', 'is_active')
    ordering = ('period_number',)

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ('room_number', 'room_name', 'room_type', 'capacity', 'building', 'floor', 'is_active')
    list_filter = ('room_type', 'building', 'is_active')
    search_fields = ('room_number', 'room_name', 'building')
    ordering = ('room_number',)

@admin.register(TimetableEntry)
class TimetableEntryAdmin(admin.ModelAdmin):
    list_display = ('subject', 'teacher', 'get_day_display', 'time_slot', 'room', 'course', 'year', 'section')
    list_filter = ('course', 'year', 'section', 'day_of_week', 'academic_year', 'semester', 'is_active')
    search_fields = ('subject__name', 'subject__code', 'teacher__name', 'room__room_number')
    ordering = ('day_of_week', 'time_slot__period_number')
    
    def get_day_display(self, obj):
        return obj.get_day_of_week_display()
    get_day_display.short_description = 'Day'

@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'subject', 'academic_year', 'semester', 'enrolled_at', 'is_active')
    list_filter = ('academic_year', 'semester', 'is_active', 'enrolled_at')
    search_fields = ('student__roll_number', 'student__user__first_name', 'subject__name', 'subject__code')
    ordering = ('-enrolled_at',)

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ('student', 'get_subject', 'date', 'status', 'marked_at', 'marked_by')
    list_filter = ('status', 'date', 'marked_at')
    search_fields = ('student__roll_number', 'timetable_entry__subject__name')
    ordering = ('-date', '-marked_at')
    
    def get_subject(self, obj):
        return obj.timetable_entry.subject.name
    get_subject.short_description = 'Subject'

@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'posted_by', 'target_audience', 'is_urgent', 'is_active', 'created_at')
    list_filter = ('target_audience', 'is_urgent', 'is_active', 'created_at')
    search_fields = ('title', 'content', 'posted_by__username')
    ordering = ('-is_urgent', '-created_at')
    readonly_fields = ('created_at', 'updated_at')
