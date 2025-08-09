from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
# from phonenumber_field.modelfields import PhoneNumberField
import random
from datetime import timedelta

class User(AbstractUser):
    """Custom user model extending Django's AbstractUser."""
    USER_TYPE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('admin', 'Admin'),
    ]
    
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    phone_number = models.CharField(max_length=15, blank=True, null=True, unique=True, help_text="Phone number for OTP verification (optional)")
    is_verified = models.BooleanField(default=True)  # For future phone verification
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.username} ({self.user_type})"

class StudentProfile(models.Model):
    """Extended profile for students."""
    COURSE_CHOICES = [
        ('B.Tech', 'Bachelor of Technology'),
        ('BCA', 'Bachelor of Computer Applications'),
        ('B.Sc', 'Bachelor of Science'),
        ('MCA', 'Master of Computer Applications'),
        ('M.Tech', 'Master of Technology'),
        ('MBA', 'Master of Business Administration'),
    ]
    
    YEAR_CHOICES = [
        (1, 'First Year'),
        (2, 'Second Year'),
        (3, 'Third Year'),
        (4, 'Fourth Year'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    roll_number = models.CharField(
        max_length=20, 
        unique=True,
        validators=[RegexValidator(
            regex=r'^[A-Z0-9]+$',
            message='Roll number should contain only uppercase letters and numbers.'
        )]
    )
    course = models.CharField(max_length=50, choices=COURSE_CHOICES)
    year = models.IntegerField(choices=YEAR_CHOICES)
    section = models.CharField(
        max_length=5,
        validators=[RegexValidator(
            regex=r'^[A-Z]+$',
            message='Section should contain only uppercase letters.'
        )]
    )
    
    class Meta:
        unique_together = ['course', 'year', 'section', 'roll_number']
    
    def __str__(self):
        return f"{self.roll_number} - {self.user.get_full_name()}"
    
    @property
    def full_name(self):
        return self.user.get_full_name()

class AdminProfile(models.Model):
    """Extended profile for admins."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    admin_id = models.CharField(
        max_length=20, 
        unique=True,
        validators=[RegexValidator(
            regex=r'^[A-Z0-9]+$',
            message='Admin ID should contain only uppercase letters and numbers.'
        )]
    )
    department = models.CharField(max_length=100)
    designation = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return f"{self.admin_id} - {self.user.get_full_name()}"
    
    @property
    def full_name(self):
        return self.user.get_full_name()

class TeacherProfile(models.Model):
    """Extended profile for teachers."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    teacher = models.OneToOneField('timetable.Teacher', on_delete=models.CASCADE, null=True, blank=True)
    employee_id = models.CharField(
        max_length=20, 
        unique=True, 
        null=True, 
        blank=True,
        validators=[RegexValidator(
            regex=r'^[A-Z0-9]+$',
            message='Employee ID should contain only uppercase letters and numbers.'
        )]
    )
    department = models.CharField(max_length=100, blank=True)
    designation = models.CharField(max_length=100, blank=True)
    specialization = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.employee_id or 'No ID'} - {self.user.get_full_name()}"
    
    @property
    def full_name(self):
        return self.user.get_full_name()
    
    def save(self, *args, **kwargs):
        # Auto-link to Teacher model if employee_id matches
        if self.employee_id and not self.teacher:
            try:
                from timetable.models import Teacher
                teacher = Teacher.objects.get(employee_id=self.employee_id)
                self.teacher = teacher
            except Teacher.DoesNotExist:
                pass
        super().save(*args, **kwargs)

class OTP(models.Model):
    """OTP model for password reset and phone verification."""
    PURPOSE_CHOICES = [
        ('password_reset', 'Password Reset'),
        ('phone_verification', 'Phone Verification'),
        ('login_verification', 'Login Verification'),
        ('registration', 'Registration Verification'),
    ]
    
    phone_number = models.CharField(max_length=15)
    otp_code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES, default='password_reset')
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(minutes=10)
        super().save(*args, **kwargs)
    
    @classmethod
    def generate_otp(cls, phone_number, purpose='password_reset'):
        """Generate a new OTP for the given phone number."""
        # Invalidate existing OTPs for this phone number and purpose
        cls.objects.filter(
            phone_number=phone_number,
            purpose=purpose,
            is_used=False
        ).update(is_used=True)
        
        # Generate 6-digit OTP
        otp_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        
        # Create new OTP
        otp = cls.objects.create(
            phone_number=phone_number,
            otp_code=otp_code,
            purpose=purpose,
            expires_at=timezone.now() + timedelta(minutes=10)
        )
        
        return otp_code
    
    @classmethod
    def verify_otp(cls, phone_number, otp_code, purpose='password_reset'):
        """Verify OTP for the given phone number."""
        try:
            otp = cls.objects.get(
                phone_number=phone_number,
                otp_code=otp_code,
                purpose=purpose,
                is_used=False,
                expires_at__gt=timezone.now()
            )
            otp.is_used = True
            otp.save()
            return True
        except cls.DoesNotExist:
            return False
    
    def is_expired(self):
        """Check if OTP is expired."""
        return timezone.now() > self.expires_at
    
    def __str__(self):
        return f"OTP for {self.phone_number} - {self.purpose}"
