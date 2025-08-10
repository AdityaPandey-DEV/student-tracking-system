from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import StudentProfile, TeacherProfile, AdminProfile
from timetable.models import (
    Course, Subject, Teacher, TeacherSubject, TimeSlot, Room, 
    TimetableEntry, Enrollment, Attendance, Announcement
)
from ai_features.models import AIChat, ChatMessage, StudyRecommendation, PerformanceInsight
from django.utils import timezone
import random
from datetime import datetime, time, date, timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'Populate database with sample data for demonstration'

    def handle(self, *args, **options):
        self.stdout.write('🚀 Starting sample data population...\n')
        
        # Create sample data
        self.create_time_slots()
        self.create_rooms()
        self.create_courses()
        self.create_subjects()
        self.create_admin_users()
        self.create_teachers()
        self.create_students()
        self.assign_teachers_to_subjects()
        self.create_timetable_entries()
        self.enroll_students()
        self.create_attendance_records()
        self.create_announcements()
        self.create_ai_data()
        
        self.stdout.write(self.style.SUCCESS('\n✅ Sample data population completed successfully!'))
        self.stdout.write('📖 You can now login with these demo accounts:')
        self.stdout.write('   Admin: admin / admin123')
        self.stdout.write('   Teacher: teacher1 / teacher123')
        self.stdout.write('   Student: student1 / student123')
        self.stdout.write('\n🌐 Visit http://127.0.0.1:8000/ to see the demo!')

    def create_time_slots(self):
        self.stdout.write('⏰ Creating time slots...')
        time_slots_data = [
            (1, time(9, 0), time(9, 50), False),
            (2, time(9, 50), time(10, 40), False),
            (3, time(10, 40), time(11, 0), True),  # Break
            (4, time(11, 0), time(11, 50), False),
            (5, time(11, 50), time(12, 40), False),
            (6, time(12, 40), time(13, 30), True),  # Lunch break
            (7, time(13, 30), time(14, 20), False),
            (8, time(14, 20), time(15, 10), False),
            (9, time(15, 10), time(16, 0), False),
            (10, time(16, 0), time(16, 50), False),
        ]
        
        for period, start, end, is_break in time_slots_data:
            TimeSlot.objects.get_or_create(
                period_number=period,
                defaults={
                    'start_time': start,
                    'end_time': end,
                    'is_break': is_break,
                    'break_duration': 20 if is_break else 0
                }
            )
        self.stdout.write('   ✓ Time slots created')

    def create_rooms(self):
        self.stdout.write('🏢 Creating rooms...')
        rooms_data = [
            ('101', 'Computer Lab 1', 'lab', 30, '1st Floor'),
            ('102', 'Computer Lab 2', 'lab', 30, '1st Floor'),
            ('201', 'Classroom A', 'classroom', 60, '2nd Floor'),
            ('202', 'Classroom B', 'classroom', 60, '2nd Floor'),
            ('203', 'Classroom C', 'classroom', 50, '2nd Floor'),
            ('301', 'Physics Lab', 'lab', 25, '3rd Floor'),
            ('302', 'Chemistry Lab', 'lab', 25, '3rd Floor'),
            ('401', 'Seminar Hall', 'seminar', 100, '4th Floor'),
            ('501', 'Main Auditorium', 'auditorium', 200, '5th Floor'),
        ]
        
        for room_num, name, room_type, capacity, floor in rooms_data:
            Room.objects.get_or_create(
                room_number=room_num,
                defaults={
                    'room_name': name,
                    'room_type': room_type,
                    'capacity': capacity,
                    'floor': floor,
                    'building': 'Main Building'
                }
            )
        self.stdout.write('   ✓ Rooms created')

    def create_courses(self):
        self.stdout.write('📚 Creating courses...')
        courses_data = [
            ('B.Tech', 'Bachelor of Technology', 4),
            ('BCA', 'Bachelor of Computer Applications', 3),
            ('B.Sc', 'Bachelor of Science', 3),
            ('MCA', 'Master of Computer Applications', 2),
            ('M.Tech', 'Master of Technology', 2),
        ]
        
        for name, full_name, duration in courses_data:
            Course.objects.get_or_create(
                name=name,
                defaults={
                    'full_name': full_name,
                    'duration_years': duration,
                    'description': f'A comprehensive {duration}-year program in {full_name}'
                }
            )
        self.stdout.write('   ✓ Courses created')

    def create_subjects(self):
        self.stdout.write('📖 Creating subjects...')
        
        # B.Tech subjects
        btech_course = Course.objects.get(name='B.Tech')
        btech_subjects = [
            ('CS101', 'Programming Fundamentals', 1, 1, 4),
            ('CS102', 'Data Structures', 1, 2, 4),
            ('CS201', 'Algorithms', 2, 3, 4),
            ('CS202', 'Database Systems', 2, 4, 4),
            ('CS301', 'Operating Systems', 3, 5, 4),
            ('CS302', 'Computer Networks', 3, 6, 4),
            ('CS401', 'Software Engineering', 4, 7, 3),
            ('CS402', 'Machine Learning', 4, 8, 3),
            ('MA101', 'Engineering Mathematics I', 1, 1, 3),
            ('MA102', 'Engineering Mathematics II', 1, 2, 3),
            ('PH101', 'Engineering Physics', 1, 1, 3),
            ('CH101', 'Engineering Chemistry', 1, 2, 3),
        ]
        
        for code, name, year, semester, credits in btech_subjects:
            Subject.objects.get_or_create(
                code=code,
                course=btech_course,
                defaults={
                    'name': name,
                    'year': year,
                    'semester': semester,
                    'credits': credits,
                    'description': f'Core subject for {btech_course.name} Year {year}'
                }
            )
        
        # BCA subjects
        bca_course = Course.objects.get(name='BCA')
        bca_subjects = [
            ('BCA101', 'Computer Fundamentals', 1, 1, 4),
            ('BCA102', 'C Programming', 1, 2, 4),
            ('BCA201', 'Java Programming', 2, 3, 4),
            ('BCA202', 'Web Technologies', 2, 4, 4),
            ('BCA301', 'Software Testing', 3, 5, 3),
            ('BCA302', 'Project Management', 3, 6, 3),
            ('MA201', 'Discrete Mathematics', 2, 3, 3),
            ('EN101', 'Business Communication', 1, 1, 2),
        ]
        
        for code, name, year, semester, credits in bca_subjects:
            Subject.objects.get_or_create(
                code=code,
                course=bca_course,
                defaults={
                    'name': name,
                    'year': year,
                    'semester': semester,
                    'credits': credits,
                    'description': f'Core subject for {bca_course.name} Year {year}'
                }
            )
        
        self.stdout.write('   ✓ Subjects created')

    def create_admin_users(self):
        self.stdout.write('👨‍💼 Creating admin users...')
        
        # Create main admin
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'first_name': 'System',
                'last_name': 'Administrator',
                'email': 'admin@college.edu',
                'user_type': 'admin',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            
        try:
            AdminProfile.objects.get_or_create(
                user=admin_user,
                defaults={
                    'admin_id': 'ADM001',
                    'department': 'Administration',
                    'designation': 'Principal'
                }
            )
        except Exception as e:
            self.stdout.write(f'   Admin profile already exists: {e}')
        
        # Create additional admin
        admin2_user, created = User.objects.get_or_create(
            username='hod_cs',
            defaults={
                'first_name': 'Rajesh',
                'last_name': 'Sharma',
                'email': 'hod.cs@college.edu',
                'user_type': 'admin',
                'is_staff': True,
            }
        )
        if created:
            admin2_user.set_password('hod123')
            admin2_user.save()
            
        AdminProfile.objects.get_or_create(
            user=admin2_user,
            defaults={
                'admin_id': 'HOD001',
                'department': 'Computer Science',
                'designation': 'Head of Department'
            }
        )
        
        self.stdout.write('   ✓ Admin users created')

    def create_teachers(self):
        self.stdout.write('👨‍🏫 Creating teachers...')
        
        teachers_data = [
            ('teacher1', 'Priya', 'Patel', 'priya.patel@college.edu', 'EMP001', 'Computer Science', 'Professor', 'Machine Learning, Data Science'),
            ('teacher2', 'Amit', 'Kumar', 'amit.kumar@college.edu', 'EMP002', 'Computer Science', 'Associate Professor', 'Database Systems, Software Engineering'),
            ('teacher3', 'Sunita', 'Singh', 'sunita.singh@college.edu', 'EMP003', 'Computer Science', 'Assistant Professor', 'Programming, Algorithms'),
            ('teacher4', 'Ravi', 'Gupta', 'ravi.gupta@college.edu', 'EMP004', 'Mathematics', 'Professor', 'Applied Mathematics, Statistics'),
            ('teacher5', 'Meera', 'Joshi', 'meera.joshi@college.edu', 'EMP005', 'Physics', 'Associate Professor', 'Engineering Physics, Electronics'),
            ('teacher6', 'Anil', 'Verma', 'anil.verma@college.edu', 'EMP006', 'Chemistry', 'Assistant Professor', 'Organic Chemistry, Materials Science'),
        ]
        
        for username, first_name, last_name, email, emp_id, dept, designation, specialization in teachers_data:
            # Create user account
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'user_type': 'teacher',
                }
            )
            if created:
                user.set_password('teacher123')
                user.save()
            
            # Create teacher record
            teacher, _ = Teacher.objects.get_or_create(
                employee_id=emp_id,
                defaults={
                    'name': f'{first_name} {last_name}',
                    'email': email,
                    'department': dept,
                    'designation': designation,
                    'specialization': specialization,
                    'phone_number': f'+91{random.randint(7000000000, 9999999999)}'
                }
            )
            
            # Create teacher profile
            TeacherProfile.objects.get_or_create(
                user=user,
                defaults={
                    'teacher': teacher,
                    'employee_id': emp_id,
                    'department': dept,
                    'designation': designation,
                    'specialization': specialization,
                }
            )
        
        self.stdout.write('   ✓ Teachers created')

    def create_students(self):
        self.stdout.write('👨‍🎓 Creating students...')
        
        # B.Tech students
        btech_students = [
            ('student1', 'Arjun', 'Singh', 'arjun.singh@student.edu', 'BT21CS001', 'B.Tech', 2, 'A'),
            ('student2', 'Priya', 'Sharma', 'priya.sharma@student.edu', 'BT21CS002', 'B.Tech', 2, 'A'),
            ('student3', 'Vikram', 'Kumar', 'vikram.kumar@student.edu', 'BT21CS003', 'B.Tech', 2, 'A'),
            ('student4', 'Neha', 'Gupta', 'neha.gupta@student.edu', 'BT21CS004', 'B.Tech', 2, 'A'),
            ('student5', 'Rohit', 'Patel', 'rohit.patel@student.edu', 'BT21CS005', 'B.Tech', 2, 'A'),
            ('student6', 'Kavya', 'Reddy', 'kavya.reddy@student.edu', 'BT22CS001', 'B.Tech', 1, 'A'),
            ('student7', 'Ankit', 'Jain', 'ankit.jain@student.edu', 'BT22CS002', 'B.Tech', 1, 'A'),
            ('student8', 'Pooja', 'Nair', 'pooja.nair@student.edu', 'BT22CS003', 'B.Tech', 1, 'A'),
        ]
        
        # BCA students
        bca_students = [
            ('student9', 'Ravi', 'Mehta', 'ravi.mehta@student.edu', 'BCA21001', 'BCA', 2, 'A'),
            ('student10', 'Shreya', 'Das', 'shreya.das@student.edu', 'BCA21002', 'BCA', 2, 'A'),
            ('student11', 'Karan', 'Agarwal', 'karan.agarwal@student.edu', 'BCA22001', 'BCA', 1, 'A'),
            ('student12', 'Tanya', 'Mishra', 'tanya.mishra@student.edu', 'BCA22002', 'BCA', 1, 'A'),
        ]
        
        all_students = btech_students + bca_students
        
        for username, first_name, last_name, email, roll_no, course, year, section in all_students:
            # Create user account
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'email': email,
                    'user_type': 'student',
                }
            )
            if created:
                user.set_password('student123')
                user.save()
            
            # Create student profile
            StudentProfile.objects.get_or_create(
                user=user,
                defaults={
                    'roll_number': roll_no,
                    'course': course,
                    'year': year,
                    'section': section,
                }
            )
        
        self.stdout.write('   ✓ Students created')

    def assign_teachers_to_subjects(self):
        self.stdout.write('🔗 Assigning teachers to subjects...')
        
        # Get teachers and subjects
        priya = Teacher.objects.get(employee_id='EMP001')
        amit = Teacher.objects.get(employee_id='EMP002')
        sunita = Teacher.objects.get(employee_id='EMP003')
        ravi = Teacher.objects.get(employee_id='EMP004')
        meera = Teacher.objects.get(employee_id='EMP005')
        anil = Teacher.objects.get(employee_id='EMP006')
        
        # Teacher-Subject assignments
        assignments = [
            (priya, ['CS402', 'CS301']),  # Machine Learning, OS
            (amit, ['CS202', 'CS401']),   # Database, Software Engineering
            (sunita, ['CS101', 'CS201']), # Programming, Algorithms
            (ravi, ['MA101', 'MA102', 'MA201']),  # Math subjects
            (meera, ['PH101']),           # Physics
            (anil, ['CH101']),            # Chemistry
        ]
        
        for teacher, subject_codes in assignments:
            for code in subject_codes:
                try:
                    subject = Subject.objects.get(code=code)
                    TeacherSubject.objects.get_or_create(
                        teacher=teacher,
                        subject=subject
                    )
                except Subject.DoesNotExist:
                    pass
        
        self.stdout.write('   ✓ Teacher assignments created')

    def create_timetable_entries(self):
        self.stdout.write('📅 Creating timetable entries...')
        
        academic_year = "2024-25"
        current_semester = 3  # Odd semester
        
        # B.Tech Year 2 Section A timetable
        btech_y2_subjects = ['CS201', 'CS202', 'MA201']  # Current semester subjects
        btech_schedule = [
            # Monday
            (0, 1, 'CS201', 'EMP003', '201'),  # Algorithms - Sunita
            (0, 2, 'CS202', 'EMP002', '102'),  # Database - Amit (Lab)
            (0, 4, 'MA201', 'EMP004', '201'),  # Discrete Math - Ravi
            
            # Tuesday
            (1, 1, 'CS202', 'EMP002', '201'),  # Database - Amit
            (1, 2, 'CS201', 'EMP003', '101'),  # Algorithms - Sunita (Lab)
            (1, 4, 'MA201', 'EMP004', '201'),  # Discrete Math - Ravi
            
            # Wednesday
            (2, 1, 'CS201', 'EMP003', '201'),  # Algorithms - Sunita
            (2, 2, 'CS202', 'EMP002', '201'),  # Database - Amit
            (2, 4, 'MA201', 'EMP004', '201'),  # Discrete Math - Ravi
            
            # Thursday
            (3, 1, 'CS202', 'EMP002', '102'),  # Database - Amit (Lab)
            (3, 2, 'CS201', 'EMP003', '201'),  # Algorithms - Sunita
            (3, 4, 'MA201', 'EMP004', '201'),  # Discrete Math - Ravi
            
            # Friday
            (4, 1, 'CS201', 'EMP003', '101'),  # Algorithms - Sunita (Lab)
            (4, 2, 'CS202', 'EMP002', '201'),  # Database - Amit
        ]
        
        for day, period, subject_code, teacher_emp_id, room_no in btech_schedule:
            try:
                subject = Subject.objects.get(code=subject_code)
                teacher = Teacher.objects.get(employee_id=teacher_emp_id)
                time_slot = TimeSlot.objects.get(period_number=period, is_break=False)
                room = Room.objects.get(room_number=room_no)
                
                TimetableEntry.objects.get_or_create(
                    subject=subject,
                    teacher=teacher,
                    course='B.Tech',
                    year=2,
                    section='A',
                    day_of_week=day,
                    time_slot=time_slot,
                    room=room,
                    academic_year=academic_year,
                    semester=current_semester
                )
            except (Subject.DoesNotExist, Teacher.DoesNotExist, TimeSlot.DoesNotExist, Room.DoesNotExist):
                continue
        
        # B.Tech Year 1 Section A timetable (Semester 1 subjects)
        btech_y1_subjects = ['CS101', 'MA101', 'PH101']
        btech_y1_schedule = [
            # Monday
            (0, 7, 'CS101', 'EMP003', '201'),  # Programming - Sunita
            (0, 8, 'MA101', 'EMP004', '202'),  # Math - Ravi
            
            # Tuesday
            (1, 7, 'PH101', 'EMP005', '301'),  # Physics - Meera (Lab)
            (1, 8, 'CS101', 'EMP003', '101'),  # Programming - Sunita (Lab)
            
            # Wednesday
            (2, 7, 'MA101', 'EMP004', '202'),  # Math - Ravi
            (2, 8, 'CS101', 'EMP003', '201'),  # Programming - Sunita
            
            # Thursday
            (3, 7, 'CS101', 'EMP003', '101'),  # Programming - Sunita (Lab)
            (3, 8, 'PH101', 'EMP005', '202'),  # Physics - Meera
            
            # Friday
            (4, 7, 'MA101', 'EMP004', '202'),  # Math - Ravi
            (4, 8, 'PH101', 'EMP005', '301'),  # Physics - Meera (Lab)
        ]
        
        for day, period, subject_code, teacher_emp_id, room_no in btech_y1_schedule:
            try:
                subject = Subject.objects.get(code=subject_code)
                teacher = Teacher.objects.get(employee_id=teacher_emp_id)
                time_slot = TimeSlot.objects.get(period_number=period, is_break=False)
                room = Room.objects.get(room_number=room_no)
                
                TimetableEntry.objects.get_or_create(
                    subject=subject,
                    teacher=teacher,
                    course='B.Tech',
                    year=1,
                    section='A',
                    day_of_week=day,
                    time_slot=time_slot,
                    room=room,
                    academic_year=academic_year,
                    semester=1  # First semester
                )
            except (Subject.DoesNotExist, Teacher.DoesNotExist, TimeSlot.DoesNotExist, Room.DoesNotExist):
                continue
        
        self.stdout.write('   ✓ Timetable entries created')

    def enroll_students(self):
        self.stdout.write('📝 Enrolling students in subjects...')
        
        academic_year = "2024-25"
        
        # Enroll B.Tech Year 2 students in their subjects
        btech_y2_students = StudentProfile.objects.filter(course='B.Tech', year=2)
        btech_y2_subjects = Subject.objects.filter(code__in=['CS201', 'CS202', 'MA201'])
        
        for student in btech_y2_students:
            for subject in btech_y2_subjects:
                Enrollment.objects.get_or_create(
                    student=student,
                    subject=subject,
                    academic_year=academic_year,
                    semester=3
                )
        
        # Enroll B.Tech Year 1 students in their subjects
        btech_y1_students = StudentProfile.objects.filter(course='B.Tech', year=1)
        btech_y1_subjects = Subject.objects.filter(code__in=['CS101', 'MA101', 'PH101'])
        
        for student in btech_y1_students:
            for subject in btech_y1_subjects:
                Enrollment.objects.get_or_create(
                    student=student,
                    subject=subject,
                    academic_year=academic_year,
                    semester=1
                )
        
        # Enroll BCA students in their subjects
        bca_y2_students = StudentProfile.objects.filter(course='BCA', year=2)
        bca_y1_students = StudentProfile.objects.filter(course='BCA', year=1)
        
        self.stdout.write('   ✓ Student enrollments created')

    def create_attendance_records(self):
        self.stdout.write('📊 Creating attendance records...')
        
        # Get recent timetable entries
        timetable_entries = TimetableEntry.objects.all()[:10]  # Limit for demo
        
        # Create attendance for the last 30 days
        for i in range(30):
            record_date = timezone.now().date() - timedelta(days=i)
            
            # Skip weekends
            if record_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
                continue
            
            for entry in timetable_entries:
                # Only create attendance for the correct day of week
                if record_date.weekday() != entry.day_of_week:
                    continue
                    
                students = entry.get_students()
                
                for student in students:
                    # Random attendance with 85% present rate
                    status = random.choices(
                        ['present', 'absent', 'late'],
                        weights=[85, 10, 5]
                    )[0]
                    
                    Attendance.objects.get_or_create(
                        student=student,
                        timetable_entry=entry,
                        date=record_date,
                        defaults={
                            'status': status,
                            'marked_by': entry.teacher.teacherprofile.user if hasattr(entry.teacher, 'teacherprofile') else None,
                            'notes': f'Marked during {entry.subject.name} class' if status == 'late' else ''
                        }
                    )
        
        self.stdout.write('   ✓ Attendance records created')

    def create_announcements(self):
        self.stdout.write('📢 Creating announcements...')
        
        admin_user = User.objects.filter(user_type='admin').first()
        if not admin_user:
            return
        
        announcements_data = [
            ("Welcome to New Academic Year", "Welcome students to the new academic year 2024-25. Classes will commence from next Monday. All students are requested to collect their ID cards from the office.", 'all', False),
            ("Holiday Notice", "College will remain closed on October 2nd due to Gandhi Jayanti. Regular classes will resume from October 3rd.", 'all', True),
            ("Exam Schedule Update", "Mid-semester examinations for B.Tech students will be conducted from November 15th to November 25th. Detailed schedule will be published soon.", 'course', False),
            ("Library Extended Hours", "Library timings have been extended till 9 PM on weekdays for better study facilities.", 'all', False),
            ("CS Department Seminar", "Guest lecture on 'Artificial Intelligence in Modern Applications' by Dr. Sarah Johnson on October 20th at 2 PM in Main Auditorium.", 'course', False),
        ]
        
        for title, content, audience, is_urgent in announcements_data:
            Announcement.objects.get_or_create(
                title=title,
                defaults={
                    'content': content,
                    'posted_by': admin_user,
                    'target_audience': audience,
                    'target_course': 'B.Tech' if audience == 'course' else '',
                    'is_urgent': is_urgent,
                }
            )
        
        self.stdout.write('   ✓ Announcements created')

    def create_ai_data(self):
        self.stdout.write('🤖 Creating AI features data...')
        
        # Create some sample chat sessions and messages
        students = StudentProfile.objects.all()[:3]  # First 3 students
        
        sample_chats = [
            ("Hello! Can you help me with my computer science assignments?", "Of course! I'd be happy to help you with your CS assignments. What specific topic are you working on?"),
            ("What is the difference between arrays and linked lists?", "Great question! Arrays and linked lists are both data structures, but they have key differences:\n\n1. **Memory allocation**: Arrays use contiguous memory, while linked lists use non-contiguous memory.\n2. **Access time**: Arrays provide O(1) random access, while linked lists require O(n) sequential access.\n3. **Memory overhead**: Arrays have less memory overhead, while linked lists require extra memory for pointers.\n\nWould you like me to explain any of these points in more detail?"),
            ("How can I improve my attendance?", "Here are some tips to improve your attendance:\n1. Set a regular sleep schedule\n2. Prepare everything the night before\n3. Set multiple alarms\n4. Find a study buddy for accountability\n5. Remember that attendance affects your grades\n\nYour current attendance in most subjects is good - keep it up!"),
        ]
        
        for i, student in enumerate(students):
            if i < len(sample_chats):
                user_msg, ai_msg = sample_chats[i]
                
                # Create chat session
                chat_session, _ = AIChat.objects.get_or_create(
                    user=student.user,
                    session_id=f"session_{student.user.id}_{i+1}",
                    defaults={
                        'chat_type': 'academic_help' if i < 2 else 'general_query',
                    }
                )
                
                # User message
                ChatMessage.objects.get_or_create(
                    chat=chat_session,
                    sender='user',
                    message=user_msg,
                    defaults={'timestamp': timezone.now() - timedelta(hours=i*2)}
                )
                
                # AI response
                ChatMessage.objects.get_or_create(
                    chat=chat_session,
                    sender='ai', 
                    message=ai_msg,
                    defaults={'timestamp': timezone.now() - timedelta(hours=i*2) + timedelta(minutes=1)}
                )
        
        # Create study recommendations
        for i, student in enumerate(students):
            subjects = Subject.objects.filter(code__in=['CS201', 'CS202', 'MA201'])[:2]  # Get 2 subjects
            
            recommendation, _ = StudyRecommendation.objects.get_or_create(
                student=student,
                recommendation_type='subject_focus',
                defaults={
                    'title': f'Focus on {subjects.first().name if subjects else "Core Subjects"}',
                    'description': 'Based on your recent performance, I recommend spending more time on this subject. Practice regularly and attend all lectures.',
                    'priority': random.choice(['medium', 'high']),
                    'confidence_score': random.uniform(80, 95),
                    'generated_data': {
                        'analysis': 'Student performance analysis',
                        'current_score': random.uniform(70, 85),
                        'target_score': random.uniform(85, 95)
                    }
                }
            )
            # Add subjects to the recommendation
            recommendation.subjects.set(subjects)
        
        # Create performance insights
        for student in students:
            PerformanceInsight.objects.get_or_create(
                student=student,
                insight_type='performance_trend',
                scope='individual',
                defaults={
                    'title': f'Performance Analysis for {student.user.get_full_name()}',
                    'description': 'Your academic performance shows a positive trend with consistent attendance and good grades in technical subjects.',
                    'insight_data': {
                        'attendance_rate': random.uniform(85, 95),
                        'average_grade': random.uniform(75, 90),
                        'subject_performance': {
                            'CS201': random.uniform(80, 95),
                            'CS202': random.uniform(75, 90),
                            'MA201': random.uniform(70, 85),
                        },
                        'trend': 'improving'
                    },
                    'confidence_score': random.uniform(85, 95),
                    'impact_score': random.uniform(70, 90),
                    'recommendations': 'Continue the good work! Focus more on mathematics to improve overall performance.',
                    'is_actionable': True
                }
            )
        
        self.stdout.write('   ✓ AI features data created')
