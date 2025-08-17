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
    help = 'Populate database with realistic sample data for demonstration'

    def handle(self, *args, **options):
        self.stdout.write('🚀 Starting realistic sample data population...\n')
        
        # Clear existing data for fresh start
        self.stdout.write('🧹 Clearing existing sample data...')
        self.clear_existing_data()
        
        # Create comprehensive sample data
        self.create_time_slots()
        self.create_rooms()
        self.create_courses()
        self.create_subjects()
        self.create_admin_users()
        self.create_teachers()
        self.create_diverse_students()
        self.assign_teachers_to_subjects()
        self.create_comprehensive_timetable()
        self.enroll_students_properly()
        self.create_realistic_attendance()
        self.create_announcements()
        self.create_ai_data()
        
        self.stdout.write(self.style.SUCCESS('\n✅ Realistic sample data population completed successfully!'))
        self.stdout.write('📖 You can now login with these demo accounts:')
        self.stdout.write('   Admin: admin / admin123')
        self.stdout.write('   Teacher: teacher1 / teacher123 (or teacher2, teacher3, etc.)')
        self.stdout.write('   Student: student1 / student123 (or student2, student3, etc.)')
        self.stdout.write('\n🌐 Visit http://127.0.0.1:8000/ to see the enhanced demo!')

    def clear_existing_data(self):
        """Clear existing sample data to avoid conflicts"""
        # Clear in reverse dependency order
        from ai_features.models import AIChat, ChatMessage, StudyRecommendation, PerformanceInsight
        
        # Clear AI data
        ChatMessage.objects.all().delete()
        AIChat.objects.all().delete()
        PerformanceInsight.objects.all().delete()
        StudyRecommendation.objects.all().delete()
        
        # Clear attendance and enrollment data
        Attendance.objects.all().delete()
        Enrollment.objects.all().delete()
        
        # Clear timetable data
        TimetableEntry.objects.all().delete()
        TeacherSubject.objects.all().delete()
        
        # Clear announcements
        Announcement.objects.all().delete()
        
        # Clear subjects (but keep core structure)
        Subject.objects.all().delete()
        
        # Clear profiles but keep User accounts with specific usernames
        from accounts.models import StudentProfile, TeacherProfile, AdminProfile
        StudentProfile.objects.exclude(user__username__in=['admin']).delete()
        TeacherProfile.objects.exclude(user__username__in=['admin']).delete()
        
        # Clear Teacher records (not User accounts)
        Teacher.objects.all().delete()
        
        # Clear users except core admin
        User.objects.exclude(username='admin').delete()
        
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
            ('103', 'Computer Lab 3', 'lab', 25, '1st Floor'),
            ('201', 'Classroom A', 'classroom', 60, '2nd Floor'),
            ('202', 'Classroom B', 'classroom', 60, '2nd Floor'),
            ('203', 'Classroom C', 'classroom', 50, '2nd Floor'),
            ('204', 'Classroom D', 'classroom', 50, '2nd Floor'),
            ('301', 'Physics Lab', 'lab', 25, '3rd Floor'),
            ('302', 'Chemistry Lab', 'lab', 25, '3rd Floor'),
            ('303', 'Mathematics Room', 'classroom', 45, '3rd Floor'),
            ('401', 'Seminar Hall 1', 'seminar', 80, '4th Floor'),
            ('402', 'Seminar Hall 2', 'seminar', 60, '4th Floor'),
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
        
        # B.Tech subjects - More comprehensive
        btech_course = Course.objects.get(name='B.Tech')
        btech_subjects = [
            # Year 1
            ('CS101', 'Programming Fundamentals', 1, 1, 4),
            ('CS102', 'Data Structures', 1, 2, 4),
            ('MA101', 'Engineering Mathematics I', 1, 1, 3),
            ('MA102', 'Engineering Mathematics II', 1, 2, 3),
            ('PH101', 'Engineering Physics', 1, 1, 3),
            ('CH101', 'Engineering Chemistry', 1, 2, 3),
            ('EN101', 'Technical Communication', 1, 1, 2),
            ('EN102', 'Professional Ethics', 1, 2, 2),
            
            # Year 2
            ('CS201', 'Algorithms', 2, 3, 4),
            ('CS202', 'Database Systems', 2, 4, 4),
            ('CS203', 'Object Oriented Programming', 2, 3, 4),
            ('CS204', 'Computer Graphics', 2, 4, 3),
            ('MA201', 'Discrete Mathematics', 2, 3, 3),
            ('MA202', 'Probability and Statistics', 2, 4, 3),
            
            # Year 3
            ('CS301', 'Operating Systems', 3, 5, 4),
            ('CS302', 'Computer Networks', 3, 6, 4),
            ('CS303', 'Software Engineering', 3, 5, 4),
            ('CS304', 'Web Technologies', 3, 6, 3),
            ('CS305', 'Theory of Computation', 3, 5, 3),
            
            # Year 4
            ('CS401', 'Machine Learning', 4, 7, 4),
            ('CS402', 'Artificial Intelligence', 4, 8, 4),
            ('CS403', 'Compiler Design', 4, 7, 3),
            ('CS404', 'Distributed Systems', 4, 8, 3),
            ('CS405', 'Cyber Security', 4, 7, 3),
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
            # Year 1
            ('BCA101', 'Computer Fundamentals', 1, 1, 4),
            ('BCA102', 'C Programming', 1, 2, 4),
            ('BCA103', 'Digital Electronics', 1, 1, 3),
            ('BCA104', 'Mathematics for Computing', 1, 2, 3),
            
            # Year 2
            ('BCA201', 'Java Programming', 2, 3, 4),
            ('BCA202', 'Web Technologies', 2, 4, 4),
            ('BCA203', 'Database Management', 2, 3, 4),
            ('BCA204', 'System Analysis', 2, 4, 3),
            
            # Year 3
            ('BCA301', 'Software Testing', 3, 5, 3),
            ('BCA302', 'Project Management', 3, 6, 3),
            ('BCA303', 'Mobile App Development', 3, 5, 4),
            ('BCA304', 'Cloud Computing', 3, 6, 3),
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
            
        AdminProfile.objects.get_or_create(
            user=admin_user,
            defaults={
                'admin_id': 'ADM001',
                'department': 'Administration',
                'designation': 'Principal'
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
            ('teacher7', 'Sita', 'Sharma', 'sita.sharma@college.edu', 'EMP007', 'Computer Science', 'Assistant Professor', 'Web Development, Networks'),
            ('teacher8', 'Rajesh', 'Yadav', 'rajesh.yadav@college.edu', 'EMP008', 'Computer Science', 'Associate Professor', 'Operating Systems, Security'),
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

    def create_diverse_students(self):
        self.stdout.write('👨‍🎓 Creating diverse student population...')
        
        # B.Tech students - All years and multiple sections
        btech_students = []
        
        # Year 1 B.Tech - Sections A, B
        for section in ['A', 'B']:
            for i in range(1, 16):  # 15 students per section
                roll = f'BT23CS{section}{i:03d}'
                username = f'btech_y1_{section.lower()}_{i}'
                first_names = ['Arjun', 'Priya', 'Vikram', 'Neha', 'Rohit', 'Kavya', 'Ankit', 'Pooja', 'Sanjay', 'Anjali', 'Rakesh', 'Shreya', 'Karan', 'Divya', 'Harsh']
                last_names = ['Singh', 'Sharma', 'Kumar', 'Gupta', 'Patel', 'Reddy', 'Jain', 'Nair', 'Yadav', 'Mishra', 'Agarwal', 'Verma', 'Chauhan', 'Mehta', 'Sinha']
                first_name = first_names[i-1]
                last_name = random.choice(last_names)
                email = f'{username}@student.edu'
                btech_students.append((username, first_name, last_name, email, roll, 'B.Tech', 1, section))
        
        # Year 2 B.Tech - Sections A, B
        for section in ['A', 'B']:
            for i in range(1, 16):
                roll = f'BT22CS{section}{i:03d}'
                username = f'btech_y2_{section.lower()}_{i}'
                first_names = ['Amit', 'Ritu', 'Suresh', 'Geeta', 'Manoj', 'Sunita', 'Deepak', 'Rekha', 'Vinod', 'Seema', 'Ashok', 'Meera', 'Rajeev', 'Nisha', 'Sunil']
                last_names = ['Singh', 'Sharma', 'Kumar', 'Gupta', 'Patel', 'Reddy', 'Jain', 'Nair', 'Yadav', 'Mishra', 'Agarwal', 'Verma', 'Chauhan', 'Mehta', 'Sinha']
                first_name = first_names[i-1]
                last_name = random.choice(last_names)
                email = f'{username}@student.edu'
                btech_students.append((username, first_name, last_name, email, roll, 'B.Tech', 2, section))
        
        # Year 3 B.Tech - Sections A, B
        for section in ['A', 'B']:
            for i in range(1, 16):
                roll = f'BT21CS{section}{i:03d}'
                username = f'btech_y3_{section.lower()}_{i}'
                first_names = ['Rajesh', 'Kavita', 'Santosh', 'Usha', 'Ramesh', 'Lata', 'Mukesh', 'Sushma', 'Naresh', 'Vandana', 'Dinesh', 'Kalpana', 'Mahesh', 'Shanti', 'Yogesh']
                last_names = ['Singh', 'Sharma', 'Kumar', 'Gupta', 'Patel', 'Reddy', 'Jain', 'Nair', 'Yadav', 'Mishra', 'Agarwal', 'Verma', 'Chauhan', 'Mehta', 'Sinha']
                first_name = first_names[i-1]
                last_name = random.choice(last_names)
                email = f'{username}@student.edu'
                btech_students.append((username, first_name, last_name, email, roll, 'B.Tech', 3, section))
        
        # Year 4 B.Tech - Sections A, B
        for section in ['A', 'B']:
            for i in range(1, 16):
                roll = f'BT20CS{section}{i:03d}'
                username = f'btech_y4_{section.lower()}_{i}'
                first_names = ['Arun', 'Radha', 'Mohan', 'Kamala', 'Gopal', 'Sita', 'Hari', 'Gita', 'Krishna', 'Sarita', 'Shyam', 'Mala', 'Raman', 'Sonal', 'Gagan']
                last_names = ['Singh', 'Sharma', 'Kumar', 'Gupta', 'Patel', 'Reddy', 'Jain', 'Nair', 'Yadav', 'Mishra', 'Agarwal', 'Verma', 'Chauhan', 'Mehta', 'Sinha']
                first_name = first_names[i-1]
                last_name = random.choice(last_names)
                email = f'{username}@student.edu'
                btech_students.append((username, first_name, last_name, email, roll, 'B.Tech', 4, section))
        
        # BCA students - All years and sections
        bca_students = []
        
        # Year 1 BCA - Sections A, B
        for section in ['A', 'B']:
            for i in range(1, 11):  # 10 students per section
                roll = f'BCA23{section}{i:03d}'
                username = f'bca_y1_{section.lower()}_{i}'
                first_names = ['Ravi', 'Shreya', 'Karan', 'Tanya', 'Nitin', 'Priyanka', 'Manish', 'Swati', 'Varun', 'Jyoti']
                last_names = ['Mehta', 'Das', 'Agarwal', 'Mishra', 'Tripathi', 'Saxena', 'Pandey', 'Tiwari', 'Shukla', 'Dubey']
                first_name = first_names[i-1]
                last_name = random.choice(last_names)
                email = f'{username}@student.edu'
                bca_students.append((username, first_name, last_name, email, roll, 'BCA', 1, section))
        
        # Year 2 BCA - Sections A, B  
        for section in ['A', 'B']:
            for i in range(1, 11):
                roll = f'BCA22{section}{i:03d}'
                username = f'bca_y2_{section.lower()}_{i}'
                first_names = ['Sachin', 'Pooja', 'Ajay', 'Nidhi', 'Vikash', 'Komal', 'Deepak', 'Sarita', 'Akhil', 'Rashmi']
                last_names = ['Mehta', 'Das', 'Agarwal', 'Mishra', 'Tripathi', 'Saxena', 'Pandey', 'Tiwari', 'Shukla', 'Dubey']
                first_name = first_names[i-1]
                last_name = random.choice(last_names)
                email = f'{username}@student.edu'
                bca_students.append((username, first_name, last_name, email, roll, 'BCA', 2, section))
        
        # Year 3 BCA - Sections A, B
        for section in ['A', 'B']:
            for i in range(1, 11):
                roll = f'BCA21{section}{i:03d}'
                username = f'bca_y3_{section.lower()}_{i}'
                first_names = ['Prakash', 'Sapna', 'Aditya', 'Namita', 'Rohit', 'Anjana', 'Sumit', 'Ragini', 'Tarun', 'Shilpa']
                last_names = ['Mehta', 'Das', 'Agarwal', 'Mishra', 'Tripathi', 'Saxena', 'Pandey', 'Tiwari', 'Shukla', 'Dubey']
                first_name = first_names[i-1]
                last_name = random.choice(last_names)
                email = f'{username}@student.edu'
                bca_students.append((username, first_name, last_name, email, roll, 'BCA', 3, section))
        
        all_students = btech_students + bca_students
        
        # Create student accounts
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
        
        self.stdout.write(f'   ✓ {len(all_students)} students created across all years and sections')

    def assign_teachers_to_subjects(self):
        self.stdout.write('🔗 Assigning teachers to subjects...')
        
        # Get teachers and subjects
        teachers = {t.employee_id: t for t in Teacher.objects.all()}
        
        # Comprehensive teacher-subject assignments
        assignments = [
            ('EMP001', ['CS401', 'CS402']),  # Priya - ML, AI (Year 4)
            ('EMP002', ['CS202', 'CS303']),  # Amit - Database, Software Engineering (Year 2, 3)
            ('EMP003', ['CS101', 'CS201']),  # Sunita - Programming, Algorithms (Year 1, 2)
            ('EMP004', ['MA101', 'MA102', 'MA201', 'MA202']),  # Ravi - All Math subjects
            ('EMP005', ['PH101']),  # Meera - Physics
            ('EMP006', ['CH101']),  # Anil - Chemistry
            ('EMP007', ['CS204', 'CS304', 'BCA202']),  # Sita - Graphics, Web Tech, BCA Web
            ('EMP008', ['CS301', 'CS405']),  # Rajesh - OS, Security
            
            # BCA subject assignments
            ('EMP003', ['BCA101', 'BCA102']),  # Sunita - BCA Programming
            ('EMP002', ['BCA203']),  # Amit - BCA Database
            ('EMP007', ['BCA201', 'BCA303']),  # Sita - BCA Java, Mobile Dev
            ('EMP001', ['BCA304']),  # Priya - BCA Cloud Computing
        ]
        
        for emp_id, subject_codes in assignments:
            if emp_id in teachers:
                teacher = teachers[emp_id]
                for code in subject_codes:
                    try:
                        subject = Subject.objects.get(code=code)
                        TeacherSubject.objects.get_or_create(
                            teacher=teacher,
                            subject=subject
                        )
                    except Subject.DoesNotExist:
                        continue
        
        self.stdout.write('   ✓ Teacher-subject assignments created')

    def create_comprehensive_timetable(self):
        self.stdout.write('📅 Creating comprehensive timetable entries...')
        
        academic_year = "2024-25"
        
        # Simplified timetable to avoid constraint violations
        # Each teacher gets unique time slots to prevent conflicts
        
        all_schedules = [
            # B.Tech Year 1 Semester 1 - Section A
            (0, 1, 'CS101', 'EMP003', '201', 1, 'A'),  # Mon 9:00-9:50
            (0, 2, 'MA101', 'EMP004', '303', 1, 'A'),  # Mon 9:50-10:40
            (0, 4, 'PH101', 'EMP005', '301', 1, 'A'),  # Mon 11:00-11:50
            (1, 1, 'CS101', 'EMP003', '101', 1, 'A'),  # Tue 9:00-9:50
            (1, 2, 'MA101', 'EMP004', '303', 1, 'A'),  # Tue 9:50-10:40
            (2, 1, 'PH101', 'EMP005', '301', 1, 'A'),  # Wed 9:00-9:50
            
            # B.Tech Year 1 Semester 1 - Section B
            (0, 7, 'CS101', 'EMP003', '202', 1, 'B'),  # Mon 1:30-2:20 PM
            (0, 8, 'MA101', 'EMP004', '303', 1, 'B'),  # Mon 2:20-3:10 PM
            (0, 9, 'PH101', 'EMP005', '301', 1, 'B'),  # Mon 3:10-4:00 PM
            (1, 7, 'CS101', 'EMP003', '102', 1, 'B'),  # Tue 1:30-2:20 PM
            (1, 8, 'MA101', 'EMP004', '303', 1, 'B'),  # Tue 2:20-3:10 PM
            
            # B.Tech Year 2 Semester 3 - Section A
            (2, 2, 'CS201', 'EMP003', '201', 2, 'A'),  # Wed 9:50-10:40
            (2, 4, 'CS202', 'EMP002', '102', 2, 'A'),  # Wed 11:00-11:50
            (3, 1, 'MA201', 'EMP004', '303', 2, 'A'),  # Thu 9:00-9:50
            (3, 2, 'CS201', 'EMP003', '101', 2, 'A'),  # Thu 9:50-10:40
            (4, 1, 'CS202', 'EMP002', '201', 2, 'A'),  # Fri 9:00-9:50
            
            # B.Tech Year 2 Semester 3 - Section B
            (2, 7, 'CS201', 'EMP003', '202', 2, 'B'),  # Wed 1:30-2:20 PM
            (2, 8, 'CS202', 'EMP002', '103', 2, 'B'),  # Wed 2:20-3:10 PM
            (3, 7, 'MA201', 'EMP004', '303', 2, 'B'),  # Thu 1:30-2:20 PM
            (3, 8, 'CS201', 'EMP003', '103', 2, 'B'),  # Thu 2:20-3:10 PM
            
            # BCA Year 1 - Section A
            (0, 5, 'BCA101', 'EMP003', '204', 1, 'A'),  # Mon 11:50-12:40
            (1, 4, 'BCA102', 'EMP003', '102', 1, 'A'),  # Tue 11:00-11:50
            (1, 5, 'BCA103', 'EMP005', '301', 1, 'A'),  # Tue 11:50-12:40
            (2, 5, 'BCA104', 'EMP004', '303', 1, 'A'),  # Wed 11:50-12:40
            
            # BCA Year 1 - Section B
            (0, 10, 'BCA101', 'EMP003', '204', 1, 'B'),  # Mon 4:00-4:50 PM
            (1, 9, 'BCA102', 'EMP003', '103', 1, 'B'),   # Tue 3:10-4:00 PM
            (1, 10, 'BCA103', 'EMP005', '301', 1, 'B'),  # Tue 4:00-4:50 PM
            (2, 9, 'BCA104', 'EMP004', '303', 1, 'B'),   # Wed 3:10-4:00 PM
            
            # BCA Year 2 - Section A
            (3, 4, 'BCA201', 'EMP007', '201', 2, 'A'),  # Thu 11:00-11:50
            (3, 5, 'BCA203', 'EMP002', '102', 2, 'A'),  # Thu 11:50-12:40
            (4, 2, 'BCA202', 'EMP007', '204', 2, 'A'),  # Fri 9:50-10:40
            (4, 4, 'BCA204', 'EMP002', '201', 2, 'A'),  # Fri 11:00-11:50
            
            # BCA Year 2 - Section B
            (3, 9, 'BCA201', 'EMP007', '202', 2, 'B'),  # Thu 3:10-4:00 PM
            (3, 10, 'BCA203', 'EMP002', '103', 2, 'B'), # Thu 4:00-4:50 PM
            (4, 7, 'BCA202', 'EMP007', '204', 2, 'B'),  # Fri 1:30-2:20 PM
            (4, 8, 'BCA204', 'EMP002', '202', 2, 'B'),  # Fri 2:20-3:10 PM
        ]
        
        created_count = 0
        for day, period, subject_code, teacher_emp_id, room_no, year, section in all_schedules:
            try:
                subject = Subject.objects.get(code=subject_code)
                teacher = Teacher.objects.get(employee_id=teacher_emp_id)
                time_slot = TimeSlot.objects.get(period_number=period, is_break=False)
                room = Room.objects.get(room_number=room_no)
                course = subject.course.name
                
                # Use more specific get_or_create to avoid constraint violations
                entry, created = TimetableEntry.objects.get_or_create(
                    day_of_week=day,
                    time_slot=time_slot,
                    teacher=teacher,
                    academic_year=academic_year,
                    semester=subject.semester,
                    defaults={
                        'subject': subject,
                        'course': course,
                        'year': year,
                        'section': section,
                        'room': room,
                    }
                )
                if created:
                    created_count += 1
                    
            except (Subject.DoesNotExist, Teacher.DoesNotExist, TimeSlot.DoesNotExist, Room.DoesNotExist) as e:
                self.stdout.write(f'   ⚠️ Skipped entry for {subject_code} - {teacher_emp_id}: {str(e)}')
                continue
        
        self.stdout.write(f'   ✓ {created_count} timetable entries created')

    def enroll_students_properly(self):
        self.stdout.write('📝 Enrolling students in subjects...')
        
        academic_year = "2024-25"
        
        # Enroll students in subjects based on their year and course
        all_students = StudentProfile.objects.all()
        
        for student in all_students:
            # Get subjects for student's course and year
            subjects = Subject.objects.filter(
                course__name=student.course,
                year=student.year
            )
            
            # Enroll in all subjects for their year
            for subject in subjects:
                Enrollment.objects.get_or_create(
                    student=student,
                    subject=subject,
                    academic_year=academic_year,
                    semester=subject.semester
                )
        
        self.stdout.write(f'   ✓ All students enrolled in appropriate subjects')

    def create_realistic_attendance(self):
        self.stdout.write('📊 Creating realistic attendance records...')
        
        # Get all timetable entries
        timetable_entries = TimetableEntry.objects.all()
        
        # Create attendance for the last 60 days
        for i in range(60):
            record_date = timezone.now().date() - timedelta(days=i)
            
            # Skip weekends
            if record_date.weekday() >= 5:
                continue
            
            for entry in timetable_entries:
                # Only create attendance for the correct day of week
                if record_date.weekday() != entry.day_of_week:
                    continue
                
                # Get students enrolled in this subject
                enrolled_students = Enrollment.objects.filter(
                    subject=entry.subject,
                    is_active=True
                ).select_related('student')
                
                for enrollment in enrolled_students:
                    # Skip if student doesn't match the class
                    if (enrollment.student.course != entry.course or 
                        enrollment.student.year != entry.year or 
                        enrollment.student.section != entry.section):
                        continue
                    
                    # Realistic attendance patterns
                    attendance_rate = random.uniform(0.75, 0.95)  # 75-95% attendance
                    status = random.choices(
                        ['present', 'absent', 'late'],
                        weights=[attendance_rate * 100, (1 - attendance_rate) * 80, (1 - attendance_rate) * 20]
                    )[0]
                    
                    Attendance.objects.get_or_create(
                        student=enrollment.student,
                        timetable_entry=entry,
                        date=record_date,
                        defaults={
                            'status': status,
                            'marked_by': entry.teacher.teacherprofile.user if hasattr(entry.teacher, 'teacherprofile') else None,
                            'notes': f'Regular class attendance for {entry.subject.name}' if status == 'present' else ''
                        }
                    )
        
        self.stdout.write('   ✓ Realistic attendance records created')

    def create_announcements(self):
        self.stdout.write('📢 Creating announcements...')
        
        admin_user = User.objects.filter(user_type='admin').first()
        if not admin_user:
            return
        
        announcements_data = [
            ("Welcome to Academic Year 2024-25", "Welcome all students to the new academic year 2024-25. Classes have commenced and regular attendance is mandatory.", 'all', False),
            ("Holiday Notice - Diwali", "College will remain closed from November 10-15 for Diwali celebrations. Classes will resume on November 16th.", 'all', True),
            ("B.Tech Mid-Semester Exams", "Mid-semester examinations for B.Tech students will be conducted from December 1-15. Detailed schedule will be published soon.", 'course', False),
            ("Library Extended Hours", "Library timings have been extended till 10 PM on all weekdays for better study facilities during exam season.", 'all', False),
            ("Computer Science Department Seminar", "Technical seminar on 'Future of AI in Software Development' by industry expert on November 25th at 3 PM in Main Auditorium.", 'course', False),
            ("BCA Industrial Visit", "BCA students will have an industrial visit to Tech Mahindra on December 5th. Attendance is mandatory.", 'course', False),
            ("Sports Week Announcement", "Annual sports week will be conducted from January 15-20. Students can register with the sports department.", 'all', False),
        ]
        
        for title, content, audience, is_urgent in announcements_data:
            target_course = ''
            if audience == 'course':
                target_course = random.choice(['B.Tech', 'BCA'])
            
            Announcement.objects.get_or_create(
                title=title,
                defaults={
                    'content': content,
                    'posted_by': admin_user,
                    'target_audience': audience,
                    'target_course': target_course,
                    'is_urgent': is_urgent,
                }
            )
        
        self.stdout.write('   ✓ Announcements created')

    def create_ai_data(self):
        self.stdout.write('🤖 Creating AI features data...')
        
        # Create diverse AI chat data and insights
        students = StudentProfile.objects.all()[:10]  # First 10 students
        
        sample_chats = [
            ("Can you help me understand database normalization?", "Database normalization is the process of organizing data to minimize redundancy. The main forms are:\n1NF: Eliminate repeating groups\n2NF: Remove partial dependencies\n3NF: Remove transitive dependencies\n\nWould you like me to explain any specific form in detail?"),
            ("What are the differences between procedural and object-oriented programming?", "Great question! Here are the key differences:\n\n**Procedural Programming:**\n- Functions are the main building blocks\n- Data and functions are separate\n- Top-down approach\n- Example: C, Pascal\n\n**Object-Oriented Programming:**\n- Objects contain both data and methods\n- Encapsulation, inheritance, polymorphism\n- Bottom-up approach\n- Example: Java, C++, Python\n\nWhich concept would you like me to elaborate on?"),
            ("How can I improve my programming skills?", "Here are proven ways to improve your programming skills:\n\n1. **Practice daily** - Even 30 minutes helps\n2. **Build projects** - Start small, gradually increase complexity\n3. **Read others' code** - Learn from open source projects\n4. **Join coding communities** - Stack Overflow, GitHub\n5. **Debug systematically** - Understand your errors\n6. **Learn algorithms** - They improve problem-solving\n\nWhat programming language are you focusing on?"),
        ]
        
        for i, student in enumerate(students):
            if i < len(sample_chats):
                user_msg, ai_msg = sample_chats[i % len(sample_chats)]
                
                # Create chat session
                chat_session, _ = AIChat.objects.get_or_create(
                    user=student.user,
                    session_id=f"session_{student.user.id}_{i+1}",
                    defaults={
                        'chat_type': random.choice(['academic_help', 'general_query', 'study_guidance']),
                    }
                )
                
                # User message
                ChatMessage.objects.get_or_create(
                    chat=chat_session,
                    sender='user',
                    message=user_msg,
                    defaults={'timestamp': timezone.now() - timedelta(hours=random.randint(1, 72))}
                )
                
                # AI response
                ChatMessage.objects.get_or_create(
                    chat=chat_session,
                    sender='ai',
                    message=ai_msg,
                    defaults={'timestamp': timezone.now() - timedelta(hours=random.randint(1, 72)) + timedelta(minutes=1)}
                )
        
        # Create study recommendations
        recommendation_templates = [
            ("Focus on Database Systems", "Your attendance in CS202 is excellent, but consider spending more time on complex queries and transaction management."),
            ("Strengthen Mathematical Foundation", "Mathematics scores show room for improvement. Practice more problem-solving exercises daily."),
            ("Programming Practice Needed", "Increase coding practice time. Try solving problems on platforms like HackerRank or LeetCode."),
            ("Excellent Progress in Algorithms", "Keep up the great work in CS201! Your consistent performance is commendable."),
        ]
        
        for i, student in enumerate(students[:8]):
            title, desc = random.choice(recommendation_templates)
            subjects = Subject.objects.filter(
                code__in=['CS101', 'CS201', 'CS202', 'MA201', 'BCA201']
            )[:random.randint(1, 2)]
            
            recommendation, _ = StudyRecommendation.objects.get_or_create(
                student=student,
                recommendation_type=random.choice(['subject_focus', 'study_habit', 'attendance_improvement']),
                defaults={
                    'title': title,
                    'description': desc,
                    'priority': random.choice(['low', 'medium', 'high']),
                    'confidence_score': random.uniform(75, 95),
                    'generated_data': {
                        'analysis': 'AI-generated student performance analysis',
                        'current_score': random.uniform(65, 85),
                        'target_score': random.uniform(80, 95),
                        'improvement_areas': ['attendance', 'assignment_scores', 'participation']
                    }
                }
            )
            recommendation.subjects.set(subjects)
        
        # Create performance insights
        for i, student in enumerate(students[:6]):
            PerformanceInsight.objects.get_or_create(
                student=student,
                insight_type=random.choice(['performance_trend', 'subject_analysis', 'attendance_pattern']),
                scope='individual',
                defaults={
                    'title': f'Academic Performance Analysis - {student.user.get_full_name()}',
                    'description': f'Comprehensive analysis shows {random.choice(["positive", "stable", "improving"])} trend in academic performance with consistent {random.choice(["attendance", "assignment completion", "class participation"])}.',
                    'insight_data': {
                        'overall_grade': random.uniform(70, 90),
                        'attendance_rate': random.uniform(80, 95),
                        'subject_performance': {
                            'CS201': random.uniform(75, 90),
                            'CS202': random.uniform(70, 85),
                            'MA201': random.uniform(65, 80),
                        },
                        'trend_direction': random.choice(['improving', 'stable', 'declining']),
                        'strength_areas': ['programming', 'logical thinking'],
                        'improvement_areas': ['mathematics', 'theory subjects']
                    },
                    'confidence_score': random.uniform(80, 95),
                    'impact_score': random.uniform(70, 90),
                    'recommendations': 'Continue current study patterns. Consider forming study groups for theoretical subjects.',
                    'is_actionable': True
                }
            )
        
        self.stdout.write('   ✓ Comprehensive AI features data created')
