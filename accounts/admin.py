from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, StudentProfile, AdminProfile, TeacherProfile, OTP

class StudentProfileInline(admin.StackedInline):
    model = StudentProfile
    can_delete = False
    verbose_name_plural = 'Student Profile'
    fk_name = 'user'

class AdminProfileInline(admin.StackedInline):
    model = AdminProfile
    can_delete = False
    verbose_name_plural = 'Admin Profile'
    fk_name = 'user'

class TeacherProfileInline(admin.StackedInline):
    model = TeacherProfile
    can_delete = False
    verbose_name_plural = 'Teacher Profile'
    fk_name = 'user'

class CustomUserAdmin(UserAdmin):
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)
    
    def get_inlines(self, request, obj):
        inlines = []
        if obj and obj.user_type == 'student':
            inlines.append(StudentProfileInline)
        elif obj and obj.user_type == 'admin':
            inlines.append(AdminProfileInline)
        elif obj and obj.user_type == 'teacher':
            inlines.append(TeacherProfileInline)
        return inlines
    
    list_display = ('username', 'email', 'user_type', 'phone_number', 'is_active', 'date_joined')
    list_filter = ('user_type', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'email', 'phone_number')
    ordering = ('-date_joined',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('user_type', 'phone_number', 'is_verified')}),
    )
    
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Additional Info', {'fields': ('user_type', 'phone_number', 'email', 'first_name', 'last_name')}),
    )

@admin.register(StudentProfile)
class StudentProfileAdmin(admin.ModelAdmin):
    list_display = ('roll_number', 'user', 'course', 'year', 'section')
    list_filter = ('course', 'year', 'section')
    search_fields = ('roll_number', 'user__username', 'user__first_name', 'user__last_name')
    ordering = ('course', 'year', 'section', 'roll_number')

@admin.register(AdminProfile)
class AdminProfileAdmin(admin.ModelAdmin):
    list_display = ('admin_id', 'user', 'department', 'designation')
    list_filter = ('department',)
    search_fields = ('admin_id', 'user__username', 'user__first_name', 'user__last_name', 'department')
    ordering = ('department', 'admin_id')

@admin.register(TeacherProfile)
class TeacherProfileAdmin(admin.ModelAdmin):
    list_display = ('employee_id', 'user', 'department', 'designation', 'is_active')
    list_filter = ('department', 'designation', 'is_active')
    search_fields = ('employee_id', 'user__username', 'user__first_name', 'user__last_name', 'user__email', 'department')
    ordering = ('department', 'employee_id')

@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'purpose', 'otp_code', 'is_used', 'expires_at', 'created_at')
    list_filter = ('purpose', 'is_used', 'created_at')
    search_fields = ('phone_number',)
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)

# Register the custom user admin
admin.site.register(User, CustomUserAdmin)
