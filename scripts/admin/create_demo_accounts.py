#!/usr/bin/env python3
"""
Create Demo Accounts for Student Tracking System
This script creates demo accounts for admin, teacher, and student users.
"""

import os
import django
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'enhanced_timetable_system.settings')
django.setup()

from django.contrib.auth import get_user_model
from accounts.models import AdminProfile, TeacherProfile, StudentProfile
from timetable.models import Teacher
import random

User = get_user_model()

def create_demo_admin(username='admin', password='admin123', email='admin@demo.com', 
                     first_name='System', last_name='Administrator', 
                     admin_id='ADM001', department='Administration', designation='Principal'):
    """Create a demo admin account."""
    try:
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            user.set_password(password)
            user.save()
            print(f"✅ Updated existing admin user: {username}/{password}")
        else:
            # Create admin user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type='admin',
                is_staff=True,
                is_superuser=True,
                is_verified=True
            )
            print(f"✅ Created admin user: {username}/{password}")
        
        # Create or update admin profile
        admin_profile, created = AdminProfile.objects.get_or_create(
            user=user,
            defaults={
                'admin_id': admin_id,
                'department': department,
                'designation': designation
            }
        )
        if not created:
            admin_profile.admin_id = admin_id
            admin_profile.department = department
            admin_profile.designation = designation
            admin_profile.save()
            print(f"   Updated admin profile: {admin_id}")
        else:
            print(f"   Created admin profile: {admin_id}")
            
        return user
    except Exception as e:
        print(f"❌ Error creating admin {username}: {e}")
        return None

def create_demo_teacher(username, password, email, first_name, last_name, 
                       employee_id, department, designation, specialization):
    """Create a demo teacher account."""
    try:
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            user.set_password(password)
            user.save()
            print(f"✅ Updated existing teacher user: {username}/{password}")
        else:
            # Create teacher user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type='teacher',
                is_verified=True
            )
            print(f"✅ Created teacher user: {username}/{password}")
        
        # Create or update teacher record
        teacher, _ = Teacher.objects.get_or_create(
            employee_id=employee_id,
            defaults={
                'name': f'{first_name} {last_name}',
                'email': email,
                'department': department,
                'designation': designation,
                'specialization': specialization,
                'phone_number': f'+91{random.randint(7000000000, 9999999999)}'
            }
        )
        
        # Create or update teacher profile
        teacher_profile, created = TeacherProfile.objects.get_or_create(
            user=user,
            defaults={
                'teacher': teacher,
                'employee_id': employee_id,
                'department': department,
                'designation': designation,
                'specialization': specialization,
            }
        )
        if not created:
            teacher_profile.employee_id = employee_id
            teacher_profile.department = department
            teacher_profile.designation = designation
            teacher_profile.specialization = specialization
            teacher_profile.teacher = teacher
            teacher_profile.save()
            print(f"   Updated teacher profile: {employee_id}")
        else:
            print(f"   Created teacher profile: {employee_id}")
            
        return user
    except Exception as e:
        print(f"❌ Error creating teacher {username}: {e}")
        return None

def create_demo_student(username, password, email, first_name, last_name, 
                       roll_number, course, year, section):
    """Create a demo student account."""
    try:
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            user = User.objects.get(username=username)
            user.set_password(password)
            user.save()
            print(f"✅ Updated existing student user: {username}/{password}")
        else:
            # Create student user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                user_type='student',
                is_verified=True
            )
            print(f"✅ Created student user: {username}/{password}")
        
        # Create or update student profile
        student_profile, created = StudentProfile.objects.get_or_create(
            user=user,
            defaults={
                'roll_number': roll_number,
                'course': course,
                'year': year,
                'section': section
            }
        )
        if not created:
            student_profile.roll_number = roll_number
            student_profile.course = course
            student_profile.year = year
            student_profile.section = section
            student_profile.save()
            print(f"   Updated student profile: {roll_number}")
        else:
            print(f"   Created student profile: {roll_number}")
            
        return user
    except Exception as e:
        print(f"❌ Error creating student {username}: {e}")
        return None

def main():
    """Main function to create all demo accounts."""
    print("=" * 60)
    print("🎓 Creating Demo Accounts for Student Tracking System")
    print("=" * 60)
    print()
    
    # Create Admin Accounts
    print("👨‍💼 Creating Admin Accounts...")
    print("-" * 60)
    create_demo_admin(
        username='admin',
        password='admin123',
        email='admin@demo.com',
        first_name='System',
        last_name='Administrator',
        admin_id='ADM001',
        department='Administration',
        designation='Principal'
    )
    create_demo_admin(
        username='hod_cs',
        password='hod123',
        email='hod.cs@demo.com',
        first_name='Rajesh',
        last_name='Sharma',
        admin_id='HOD001',
        department='Computer Science',
        designation='Head of Department'
    )
    print()
    
    # Create Teacher Accounts
    print("👨‍🏫 Creating Teacher Accounts...")
    print("-" * 60)
    teachers = [
        ('teacher1', 'teacher123', 'priya.patel@demo.com', 'Priya', 'Patel', 
         'EMP001', 'Computer Science', 'Professor', 'Machine Learning, Data Science'),
        ('teacher2', 'teacher123', 'amit.kumar@demo.com', 'Amit', 'Kumar', 
         'EMP002', 'Computer Science', 'Associate Professor', 'Database Systems, Software Engineering'),
        ('teacher3', 'teacher123', 'sunita.singh@demo.com', 'Sunita', 'Singh', 
         'EMP003', 'Computer Science', 'Assistant Professor', 'Programming, Algorithms'),
        ('teacher4', 'teacher123', 'ravi.gupta@demo.com', 'Ravi', 'Gupta', 
         'EMP004', 'Mathematics', 'Professor', 'Applied Mathematics, Statistics'),
        ('teacher5', 'teacher123', 'meera.joshi@demo.com', 'Meera', 'Joshi', 
         'EMP005', 'Physics', 'Associate Professor', 'Engineering Physics, Electronics'),
    ]
    
    for username, password, email, first_name, last_name, emp_id, dept, designation, specialization in teachers:
        create_demo_teacher(username, password, email, first_name, last_name, 
                           emp_id, dept, designation, specialization)
    print()
    
    # Create Student Accounts
    print("👨‍🎓 Creating Student Accounts...")
    print("-" * 60)
    students = [
        # B.Tech Year 2
        ('student1', 'student123', 'arjun.singh@demo.com', 'Arjun', 'Singh', 'BT21CS001', 'B.Tech', 2, 'A'),
        ('student2', 'student123', 'priya.sharma@demo.com', 'Priya', 'Sharma', 'BT21CS002', 'B.Tech', 2, 'A'),
        ('student3', 'student123', 'vikram.kumar@demo.com', 'Vikram', 'Kumar', 'BT21CS003', 'B.Tech', 2, 'A'),
        ('student4', 'student123', 'neha.gupta@demo.com', 'Neha', 'Gupta', 'BT21CS004', 'B.Tech', 2, 'A'),
        ('student5', 'student123', 'rohit.patel@demo.com', 'Rohit', 'Patel', 'BT21CS005', 'B.Tech', 2, 'A'),
        # B.Tech Year 1
        ('student6', 'student123', 'kavya.reddy@demo.com', 'Kavya', 'Reddy', 'BT22CS001', 'B.Tech', 1, 'A'),
        ('student7', 'student123', 'ankit.jain@demo.com', 'Ankit', 'Jain', 'BT22CS002', 'B.Tech', 1, 'A'),
        ('student8', 'student123', 'pooja.nair@demo.com', 'Pooja', 'Nair', 'BT22CS003', 'B.Tech', 1, 'A'),
        # BCA Year 2
        ('student9', 'student123', 'ravi.mehta@demo.com', 'Ravi', 'Mehta', 'BCA21001', 'BCA', 2, 'A'),
        ('student10', 'student123', 'shreya.das@demo.com', 'Shreya', 'Das', 'BCA21002', 'BCA', 2, 'A'),
        # BCA Year 1
        ('student11', 'student123', 'karan.agarwal@demo.com', 'Karan', 'Agarwal', 'BCA22001', 'BCA', 1, 'A'),
        ('student12', 'student123', 'tanya.mishra@demo.com', 'Tanya', 'Mishra', 'BCA22002', 'BCA', 1, 'A'),
    ]
    
    for username, password, email, first_name, last_name, roll_no, course, year, section in students:
        create_demo_student(username, password, email, first_name, last_name, 
                           roll_no, course, year, section)
    print()
    
    # Summary
    print("=" * 60)
    print("✅ Demo Accounts Created Successfully!")
    print("=" * 60)
    print()
    print("📋 LOGIN CREDENTIALS:")
    print()
    print("👨‍💼 ADMIN ACCOUNTS:")
    print("   • admin / admin123 (Principal)")
    print("   • hod_cs / hod123 (Head of Department)")
    print()
    print("👨‍🏫 TEACHER ACCOUNTS:")
    print("   • teacher1 / teacher123 (Priya Patel)")
    print("   • teacher2 / teacher123 (Amit Kumar)")
    print("   • teacher3 / teacher123 (Sunita Singh)")
    print("   • teacher4 / teacher123 (Ravi Gupta)")
    print("   • teacher5 / teacher123 (Meera Joshi)")
    print()
    print("👨‍🎓 STUDENT ACCOUNTS:")
    print("   • student1 / student123 (Arjun Singh)")
    print("   • student2 / student123 (Priya Sharma)")
    print("   • student3 / student123 (Vikram Kumar)")
    print("   • student4 / student123 (Neha Gupta)")
    print("   • student5 / student123 (Rohit Patel)")
    print("   • student6-12 / student123 (More students...)")
    print()
    print("🌐 Access the application at: http://127.0.0.1:8000")
    print()
    print("💡 TIP: Run this script again to update passwords or recreate accounts.")
    print()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

