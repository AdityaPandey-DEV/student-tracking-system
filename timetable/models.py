from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from accounts.models import User, StudentProfile
from django.utils import timezone
# from phonenumber_field.modelfields import PhoneNumberField

class Course(models.Model):
    """Course model for different academic programs."""
    name = models.CharField(max_length=100, unique=True)  # B.Tech, BCA, B.Sc, etc.
    full_name = models.CharField(max_length=200)
    duration_years = models.IntegerField(default=4, validators=[MinValueValidator(1), MaxValueValidator(6)])
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Subject(models.Model):
    """Subject model for different academic subjects."""
    SEMESTER_CHOICES = [(i, f"Semester {i}") for i in range(1, 9)]
    
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='subjects')
    year = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(4)])
    semester = models.IntegerField(choices=SEMESTER_CHOICES)
    credits = models.IntegerField(default=3, validators=[MinValueValidator(1), MaxValueValidator(6)])
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['course', 'year', 'semester', 'name']
        unique_together = ['code', 'course']
    
    def __str__(self):
        return f"{self.code} - {self.name}"

class Teacher(models.Model):
    """Teacher model for faculty members."""
    employee_id = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    department = models.CharField(max_length=100)
    designation = models.CharField(max_length=100, blank=True)
    specialization = models.CharField(max_length=200, blank=True)
    subjects = models.ManyToManyField(Subject, through='TeacherSubject', related_name='teachers')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.employee_id} - {self.name}"

class TeacherSubject(models.Model):
    """Many-to-many relationship between teachers and subjects."""
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['teacher', 'subject']
    
    def __str__(self):
        return f"{self.teacher.name} - {self.subject.name}"

class TimeSlot(models.Model):
    """Time slot model for different periods in a day."""
    period_number = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_break = models.BooleanField(default=False)
    break_duration = models.IntegerField(default=0, help_text="Break duration in minutes")
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['period_number']
        unique_together = ['period_number']
    
    def __str__(self):
        period_type = "Break" if self.is_break else "Period"
        return f"{period_type} {self.period_number}: {self.start_time} - {self.end_time}"
    
    @property
    def duration_minutes(self):
        """Calculate duration in minutes."""
        start = timezone.datetime.combine(timezone.datetime.today(), self.start_time)
        end = timezone.datetime.combine(timezone.datetime.today(), self.end_time)
        return int((end - start).total_seconds() / 60)

class Room(models.Model):
    """Room model for classrooms and labs."""
    ROOM_TYPE_CHOICES = [
        ('classroom', 'Classroom'),
        ('lab', 'Laboratory'),
        ('auditorium', 'Auditorium'),
        ('seminar', 'Seminar Hall'),
    ]
    
    room_number = models.CharField(max_length=20, unique=True)
    room_name = models.CharField(max_length=100, blank=True)
    room_type = models.CharField(max_length=20, choices=ROOM_TYPE_CHOICES, default='classroom')
    capacity = models.IntegerField(validators=[MinValueValidator(1)])
    floor = models.CharField(max_length=10, blank=True)
    building = models.CharField(max_length=50, blank=True)
    facilities = models.TextField(blank=True, help_text="Available facilities in the room")
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['room_number']
    
    def __str__(self):
        return f"{self.room_number} ({self.room_type})"

class TimetableEntry(models.Model):
    """Individual timetable entry for a specific class."""
    DAY_CHOICES = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
    ]
    
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='timetable_entries')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='timetable_entries')
    course = models.CharField(max_length=50)  # Denormalized for quick queries
    year = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(4)])
    section = models.CharField(max_length=5)
    day_of_week = models.IntegerField(choices=DAY_CHOICES)
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='timetable_entries')
    academic_year = models.CharField(max_length=10, help_text="e.g., 2023-24")
    semester = models.IntegerField(choices=Subject.SEMESTER_CHOICES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['day_of_week', 'time_slot__period_number']
        unique_together = [
            ['day_of_week', 'time_slot', 'room', 'academic_year', 'semester'],  # No room conflicts
            ['day_of_week', 'time_slot', 'teacher', 'academic_year', 'semester'],  # No teacher conflicts
            ['day_of_week', 'time_slot', 'course', 'year', 'section', 'academic_year', 'semester'],  # No class conflicts
        ]
    
    def __str__(self):
        day_name = self.get_day_of_week_display()
        return f"{self.subject.code} - {day_name} P{self.time_slot.period_number} - {self.course} Y{self.year}{self.section}"
    
    def get_students(self):
        """Get all students for this timetable entry."""
        return StudentProfile.objects.filter(
            course=self.course,
            year=self.year,
            section=self.section
        )

class Enrollment(models.Model):
    """Student enrollment in subjects."""
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='enrollments')
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='enrollments')
    academic_year = models.CharField(max_length=10)
    semester = models.IntegerField(choices=Subject.SEMESTER_CHOICES)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        unique_together = ['student', 'subject', 'academic_year', 'semester']
    
    def __str__(self):
        return f"{self.student.roll_number} - {self.subject.code}"

class Attendance(models.Model):
    """Student attendance tracking."""
    STATUS_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused'),
    ]
    
    student = models.ForeignKey(StudentProfile, on_delete=models.CASCADE, related_name='attendance_records')
    timetable_entry = models.ForeignKey(TimetableEntry, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='absent')
    marked_at = models.DateTimeField(auto_now_add=True)
    marked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-date', '-marked_at']
        unique_together = ['student', 'timetable_entry', 'date']
    
    def __str__(self):
        return f"{self.student.roll_number} - {self.timetable_entry.subject.code} - {self.date} - {self.status}"

class Announcement(models.Model):
    """Announcements posted by admins."""
    AUDIENCE_CHOICES = [
        ('all', 'All Students'),
        ('course', 'Specific Course'),
        ('year', 'Specific Year'),
        ('section', 'Specific Section'),
    ]
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='announcements')
    target_audience = models.CharField(max_length=20, choices=AUDIENCE_CHOICES, default='all')
    target_course = models.CharField(max_length=50, blank=True)
    target_year = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(4)])
    target_section = models.CharField(max_length=5, blank=True)
    is_active = models.BooleanField(default=True)
    is_urgent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-is_urgent', '-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.target_audience}"
    
    def get_target_students(self):
        """Get students who should see this announcement."""
        queryset = StudentProfile.objects.all()
        
        if self.target_audience == 'course' and self.target_course:
            queryset = queryset.filter(course=self.target_course)
        elif self.target_audience == 'year' and self.target_year:
            queryset = queryset.filter(year=self.target_year)
        elif self.target_audience == 'section' and self.target_course and self.target_year and self.target_section:
            queryset = queryset.filter(
                course=self.target_course,
                year=self.target_year,
                section=self.target_section
            )
        
        return queryset
