from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.utils import timezone
import json
import re

from .models import User, StudentProfile, AdminProfile, TeacherProfile, OTP
from utils.notifications import send_otp_notification

def landing_page(request):
    """Landing page with login/register options."""
    if request.user.is_authenticated:
        if hasattr(request.user, 'studentprofile'):
            return redirect('accounts:student_dashboard')
        elif hasattr(request.user, 'adminprofile'):
            return redirect('accounts:admin_dashboard')
        elif hasattr(request.user, 'teacherprofile'):
            return redirect('accounts:teacher_dashboard')
    return render(request, 'accounts/landing.html')

def register_choice(request):
    """Registration choice page."""
    return render(request, 'accounts/register_choice.html')

def student_register(request):
    """Student registration view with OTP verification."""
    if request.method == 'POST':
        step = request.POST.get('step', '1')
        
        if step == '1':
            # Step 1: Collect basic info and send OTP
            return handle_student_registration_step1(request)
        elif step == '2':
            # Step 2: Verify OTP and complete registration
            return handle_student_registration_step2(request)
    
    return render(request, 'accounts/student_register.html')

def handle_student_registration_step1(request):
    """Handle step 1 of student registration - collect info and send OTP."""
    try:
        # Get form data
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        roll_number = request.POST.get('roll_number', '').strip().upper()
        course = request.POST.get('course', '').strip()
        year = int(request.POST.get('year', 0))
        section = request.POST.get('section', '').strip().upper()
        phone_number = request.POST.get('phone_number', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        
        # Validation
        errors = []
        
        if not all([first_name, last_name, roll_number, course, year, section, phone_number, password]):
            errors.append('All fields are required.')
        
        if year not in [1, 2, 3, 4]:
            errors.append('Invalid year. Must be 1-4.')
        
        if len(section) != 1 or not section.isalpha():
            errors.append('Section must be a single letter (A, B, C, etc.)')
        
        if not re.match(r'^[A-Z0-9]+$', roll_number):
            errors.append('Roll number should contain only uppercase letters and numbers.')
        
        if not re.match(r'^\+?[\d\s\-\(\)]{10,15}$', phone_number):
            errors.append('Invalid phone number format.')
        
        if len(password) < 6:
            errors.append('Password must be at least 6 characters long.')
        
        if password != confirm_password:
            errors.append('Passwords do not match.')
        
        # Check uniqueness
        if StudentProfile.objects.filter(roll_number=roll_number).exists():
            errors.append('Roll number already exists.')
        
        if User.objects.filter(phone_number=phone_number).exists():
            errors.append('Phone number already registered.')
        
        if User.objects.filter(username=roll_number).exists():
            errors.append('This roll number is already taken.')
        
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'accounts/student_register.html')
        
        # Generate and send OTP
        otp_code = OTP.generate_otp(phone_number, 'registration')
        
        if send_otp_notification(phone_number, otp_code, 'registration'):
            # Store registration data in session
            request.session['reg_data'] = {
                'first_name': first_name,
                'last_name': last_name,
                'roll_number': roll_number,
                'course': course,
                'year': year,
                'section': section,
                'phone_number': phone_number,
                'password': password,
                'user_type': 'student'
            }
            
            messages.info(request, f'OTP sent to {phone_number}. Please enter the 6-digit code to complete registration.')
            return render(request, 'accounts/student_register.html', {
                'step': 2,
                'phone_number': phone_number
            })
        else:
            messages.error(request, 'Failed to send OTP. Please try again.')
            return render(request, 'accounts/student_register.html')
            
    except Exception as e:
        messages.error(request, 'An error occurred. Please try again.')
        return render(request, 'accounts/student_register.html')

def handle_student_registration_step2(request):
    """Handle step 2 of student registration - verify OTP and create account."""
    if 'reg_data' not in request.session:
        messages.error(request, 'Registration session expired. Please start again.')
        return redirect('accounts:student_register')
    
    try:
        otp_code = request.POST.get('otp_code', '').strip()
        reg_data = request.session['reg_data']
        
        if not otp_code:
            messages.error(request, 'Please enter the OTP code.')
            return render(request, 'accounts/student_register.html', {
                'step': 2,
                'phone_number': reg_data['phone_number']
            })
        
        # Verify OTP
        if OTP.verify_otp(reg_data['phone_number'], otp_code, 'registration'):
            # Create user and profile
            with transaction.atomic():
                user = User.objects.create_user(
                    username=reg_data['roll_number'],
                    first_name=reg_data['first_name'],
                    last_name=reg_data['last_name'],
                    phone_number=reg_data['phone_number'],
                    user_type='student'
                )
                user.set_password(reg_data['password'])
                user.save()
                
                StudentProfile.objects.create(
                    user=user,
                    roll_number=reg_data['roll_number'],
                    course=reg_data['course'],
                    year=reg_data['year'],
                    section=reg_data['section']
                )
            
            # Clear session data
            del request.session['reg_data']
            
            messages.success(request, 'Registration successful! Your account has been verified. You can now log in.')
            return redirect('accounts:login')
        else:
            messages.error(request, 'Invalid or expired OTP. Please try again.')
            return render(request, 'accounts/student_register.html', {
                'step': 2,
                'phone_number': reg_data['phone_number']
            })
            
    except Exception as e:
        messages.error(request, 'An error occurred during verification. Please try again.')
        return render(request, 'accounts/student_register.html', {
            'step': 2,
            'phone_number': request.session.get('reg_data', {}).get('phone_number', '')
        })

def admin_register(request):
    """Admin registration view with OTP verification."""
    if request.method == 'POST':
        step = request.POST.get('step', '1')
        
        if step == '1':
            return handle_admin_registration_step1(request)
        elif step == '2':
            return handle_admin_registration_step2(request)
    
    return render(request, 'accounts/admin_register.html')

def handle_admin_registration_step1(request):
    """Handle step 1 of admin registration."""
    try:
        # Get form data
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        admin_id = request.POST.get('admin_id', '').strip().upper()
        department = request.POST.get('department', '').strip()
        designation = request.POST.get('designation', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        
        # Validation
        errors = []
        
        if not all([first_name, last_name, admin_id, department, phone_number, password]):
            errors.append('All required fields must be filled.')
        
        if not re.match(r'^[A-Z0-9]+$', admin_id):
            errors.append('Admin ID should contain only uppercase letters and numbers.')
        
        if not re.match(r'^\+?[\d\s\-\(\)]{10,15}$', phone_number):
            errors.append('Invalid phone number format.')
        
        if len(password) < 6:
            errors.append('Password must be at least 6 characters long.')
        
        if password != confirm_password:
            errors.append('Passwords do not match.')
        
        # Check uniqueness
        if AdminProfile.objects.filter(admin_id=admin_id).exists():
            errors.append('Admin ID already exists.')
        
        if User.objects.filter(phone_number=phone_number).exists():
            errors.append('Phone number already registered.')
        
        if User.objects.filter(username=admin_id).exists():
            errors.append('This admin ID is already taken.')
        
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'accounts/admin_register.html')
        
        # Generate and send OTP
        otp_code = OTP.generate_otp(phone_number, 'registration')
        
        if send_otp_notification(phone_number, otp_code, 'registration'):
            # Store registration data in session
            request.session['reg_data'] = {
                'first_name': first_name,
                'last_name': last_name,
                'admin_id': admin_id,
                'department': department,
                'designation': designation,
                'phone_number': phone_number,
                'password': password,
                'user_type': 'admin'
            }
            
            messages.info(request, f'OTP sent to {phone_number}. Please enter the 6-digit code to complete registration.')
            return render(request, 'accounts/admin_register.html', {
                'step': 2,
                'phone_number': phone_number
            })
        else:
            messages.error(request, 'Failed to send OTP. Please try again.')
            return render(request, 'accounts/admin_register.html')
            
    except Exception as e:
        messages.error(request, 'An error occurred. Please try again.')
        return render(request, 'accounts/admin_register.html')

def handle_admin_registration_step2(request):
    """Handle step 2 of admin registration."""
    if 'reg_data' not in request.session or request.session['reg_data'].get('user_type') != 'admin':
        messages.error(request, 'Registration session expired. Please start again.')
        return redirect('accounts:admin_register')
    
    try:
        otp_code = request.POST.get('otp_code', '').strip()
        reg_data = request.session['reg_data']
        
        if not otp_code:
            messages.error(request, 'Please enter the OTP code.')
            return render(request, 'accounts/admin_register.html', {
                'step': 2,
                'phone_number': reg_data['phone_number']
            })
        
        # Verify OTP
        if OTP.verify_otp(reg_data['phone_number'], otp_code, 'registration'):
            # Create user and profile
            with transaction.atomic():
                user = User.objects.create_user(
                    username=reg_data['admin_id'],
                    first_name=reg_data['first_name'],
                    last_name=reg_data['last_name'],
                    phone_number=reg_data['phone_number'],
                    user_type='admin'
                )
                user.set_password(reg_data['password'])
                user.save()
                
                AdminProfile.objects.create(
                    user=user,
                    admin_id=reg_data['admin_id'],
                    department=reg_data['department'],
                    designation=reg_data['designation'] or None
                )
            
            # Clear session data
            del request.session['reg_data']
            
            messages.success(request, 'Admin registration successful! Your account has been verified. You can now log in.')
            return redirect('accounts:login')
        else:
            messages.error(request, 'Invalid or expired OTP. Please try again.')
            return render(request, 'accounts/admin_register.html', {
                'step': 2,
                'phone_number': reg_data['phone_number']
            })
            
    except Exception as e:
        messages.error(request, 'An error occurred during verification. Please try again.')
        return render(request, 'accounts/admin_register.html', {
            'step': 2,
            'phone_number': request.session.get('reg_data', {}).get('phone_number', '')
        })

def teacher_register(request):
    """Teacher registration view with OTP verification."""
    if request.method == 'POST':
        step = request.POST.get('step', '1')
        
        if step == '1':
            return handle_teacher_registration_step1(request)
        elif step == '2':
            return handle_teacher_registration_step2(request)
    
    return render(request, 'accounts/teacher_register.html')

def handle_teacher_registration_step1(request):
    """Handle step 1 of teacher registration."""
    try:
        # Get form data
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        employee_id = request.POST.get('employee_id', '').strip().upper()
        department = request.POST.get('department', '').strip()
        designation = request.POST.get('designation', '').strip()
        phone_number = request.POST.get('phone_number', '').strip()
        specialization = request.POST.get('specialization', '').strip()
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        
        # Validation
        errors = []
        
        if not all([first_name, last_name, email, phone_number, password]):
            errors.append('All required fields must be filled.')
        
        if employee_id and not re.match(r'^[A-Z0-9]+$', employee_id):
            errors.append('Employee ID should contain only uppercase letters and numbers.')
        
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            errors.append('Invalid email format.')
        
        if not re.match(r'^\+?[\d\s\-\(\)]{10,15}$', phone_number):
            errors.append('Invalid phone number format.')
        
        if len(password) < 6:
            errors.append('Password must be at least 6 characters long.')
        
        if password != confirm_password:
            errors.append('Passwords do not match.')
        
        # Check uniqueness
        if employee_id and TeacherProfile.objects.filter(employee_id=employee_id).exists():
            errors.append('Employee ID already exists.')
        
        if User.objects.filter(email=email).exists():
            errors.append('Email already registered.')
        
        if User.objects.filter(phone_number=phone_number).exists():
            errors.append('Phone number already registered.')
        
        # Use email as username if no employee_id provided
        username = employee_id or email
        if User.objects.filter(username=username).exists():
            errors.append('Username already taken.')
        
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'accounts/teacher_register.html')
        
        # Generate and send OTP
        otp_code = OTP.generate_otp(phone_number, 'registration')
        
        if send_otp_notification(phone_number, otp_code, 'registration'):
            # Store registration data in session
            request.session['reg_data'] = {
                'first_name': first_name,
                'last_name': last_name,
                'email': email,
                'employee_id': employee_id,
                'department': department,
                'designation': designation,
                'phone_number': phone_number,
                'specialization': specialization,
                'password': password,
                'username': username,
                'user_type': 'teacher'
            }
            
            messages.info(request, f'OTP sent to {phone_number}. Please enter the 6-digit code to complete registration.')
            return render(request, 'accounts/teacher_register.html', {
                'step': 2,
                'phone_number': phone_number
            })
        else:
            messages.error(request, 'Failed to send OTP. Please try again.')
            return render(request, 'accounts/teacher_register.html')
            
    except Exception as e:
        messages.error(request, 'An error occurred. Please try again.')
        return render(request, 'accounts/teacher_register.html')

def handle_teacher_registration_step2(request):
    """Handle step 2 of teacher registration."""
    if 'reg_data' not in request.session or request.session['reg_data'].get('user_type') != 'teacher':
        messages.error(request, 'Registration session expired. Please start again.')
        return redirect('accounts:teacher_register')
    
    try:
        otp_code = request.POST.get('otp_code', '').strip()
        reg_data = request.session['reg_data']
        
        if not otp_code:
            messages.error(request, 'Please enter the OTP code.')
            return render(request, 'accounts/teacher_register.html', {
                'step': 2,
                'phone_number': reg_data['phone_number']
            })
        
        # Verify OTP
        if OTP.verify_otp(reg_data['phone_number'], otp_code, 'registration'):
            # Create user and profile
            with transaction.atomic():
                user = User.objects.create_user(
                    username=reg_data['username'],
                    email=reg_data['email'],
                    first_name=reg_data['first_name'],
                    last_name=reg_data['last_name'],
                    phone_number=reg_data['phone_number'],
                    user_type='teacher'
                )
                user.set_password(reg_data['password'])
                user.save()
                
                TeacherProfile.objects.create(
                    user=user,
                    employee_id=reg_data['employee_id'] or None,
                    department=reg_data['department'],
                    designation=reg_data['designation'],
                    specialization=reg_data['specialization']
                )
            
            # Clear session data
            del request.session['reg_data']
            
            messages.success(request, 'Teacher registration successful! Your account has been verified. You can now log in.')
            return redirect('accounts:login')
        else:
            messages.error(request, 'Invalid or expired OTP. Please try again.')
            return render(request, 'accounts/teacher_register.html', {
                'step': 2,
                'phone_number': reg_data['phone_number']
            })
            
    except Exception as e:
        messages.error(request, 'An error occurred during verification. Please try again.')
        return render(request, 'accounts/teacher_register.html', {
            'step': 2,
            'phone_number': request.session.get('reg_data', {}).get('phone_number', '')
        })

def user_login(request):
    """User login view."""
    if request.method == 'POST':
        user_id = request.POST.get('user_id', '').strip()
        password = request.POST.get('password', '')
        user_type = request.POST.get('user_type', 'student')
        
        if not user_id or not password:
            messages.error(request, 'Please enter both user ID and password.')
            return render(request, 'accounts/login.html')
        
        # Authenticate user
        user = authenticate(request, username=user_id, password=password)
        
        if user is not None:
            if user.is_active:
                if user.user_type == user_type:
                    login(request, user)
                    
                    # Redirect based on user type
                    if user_type == 'student':
                        return redirect('accounts:student_dashboard')
                    elif user_type == 'admin':
                        return redirect('accounts:admin_dashboard')
                    elif user_type == 'teacher':
                        return redirect('accounts:teacher_dashboard')
                else:
                    messages.error(request, f'This account is not registered as a {user_type}.')
            else:
                messages.error(request, 'Your account is inactive. Please contact an administrator.')
        else:
            messages.error(request, 'Invalid credentials. Please try again.')
    
    return render(request, 'accounts/login.html')

@login_required
def user_logout(request):
    """User logout view."""
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('accounts:landing')

def forgot_password(request):
    """Forgot password - step 1: Enter user ID."""
    if request.method == 'POST':
        user_id = request.POST.get('user_id', '').strip()
        user_type = request.POST.get('user_type', 'student')
        
        if not user_id:
            messages.error(request, 'Please enter your user ID.')
            return render(request, 'accounts/forgot_password.html')
        
        try:
            user = User.objects.get(username=user_id, user_type=user_type)
            
            # Generate OTP
            otp_code = OTP.generate_otp(user.phone_number, 'password_reset')
            
            # Send OTP
            if send_otp_notification(user.phone_number, otp_code, 'password_reset'):
                request.session['reset_phone'] = user.phone_number
                request.session['reset_user_id'] = user_id
                request.session['reset_user_type'] = user_type
                
                messages.info(request, f'OTP sent to your registered phone number ending in ***{user.phone_number[-3:]}')
                return redirect('accounts:verify_otp')
            else:
                messages.error(request, 'Failed to send OTP. Please try again later.')
        
        except User.DoesNotExist:
            messages.error(request, 'User ID not found.')
    
    return render(request, 'accounts/forgot_password.html')

def verify_otp(request):
    """Verify OTP for password reset."""
    if 'reset_phone' not in request.session:
        messages.error(request, 'Invalid session. Please start the password reset process again.')
        return redirect('accounts:forgot_password')
    
    if request.method == 'POST':
        otp_code = request.POST.get('otp_code', '').strip()
        
        if not otp_code:
            messages.error(request, 'Please enter the OTP.')
            return render(request, 'accounts/verify_otp.html')
        
        phone_number = request.session['reset_phone']
        
        if OTP.verify_otp(phone_number, otp_code, 'password_reset'):
            messages.success(request, 'OTP verified successfully. Please set your new password.')
            return redirect('accounts:reset_password')
        else:
            messages.error(request, 'Invalid or expired OTP. Please try again.')
    
    return render(request, 'accounts/verify_otp.html')

def reset_password(request):
    """Reset password after OTP verification."""
    if 'reset_phone' not in request.session or 'reset_user_id' not in request.session:
        messages.error(request, 'Invalid session. Please start the password reset process again.')
        return redirect('accounts:forgot_password')
    
    if request.method == 'POST':
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        
        if not password:
            messages.error(request, 'Please enter a new password.')
            return render(request, 'accounts/reset_password.html')
        
        if len(password) < 6:
            messages.error(request, 'Password must be at least 6 characters long.')
            return render(request, 'accounts/reset_password.html')
        
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'accounts/reset_password.html')
        
        try:
            user_id = request.session['reset_user_id']
            user_type = request.session['reset_user_type']
            
            user = User.objects.get(username=user_id, user_type=user_type)
            user.set_password(password)
            user.save()
            
            # Clear session
            del request.session['reset_phone']
            del request.session['reset_user_id']
            del request.session['reset_user_type']
            
            messages.success(request, 'Password reset successful! You can now log in with your new password.')
            return redirect('accounts:login')
        
        except User.DoesNotExist:
            messages.error(request, 'User not found. Please try again.')
    
    return render(request, 'accounts/reset_password.html')

@csrf_exempt
@require_http_methods(["POST"])
def resend_registration_otp(request):
    """Resend OTP for registration verification."""
    if 'reg_data' not in request.session:
        return JsonResponse({
            'success': False,
            'message': 'Registration session expired. Please start again.'
        })
    
    try:
        reg_data = request.session['reg_data']
        phone_number = reg_data.get('phone_number')
        
        if not phone_number:
            return JsonResponse({
                'success': False,
                'message': 'Phone number not found in session.'
            })
        
        # Generate new OTP
        otp_code = OTP.generate_otp(phone_number, 'registration')
        
        # Send OTP
        if send_otp_notification(phone_number, otp_code, 'registration'):
            return JsonResponse({
                'success': True,
                'message': f'New OTP sent to {phone_number}'
            })
        else:
            return JsonResponse({
                'success': False,
                'message': 'Failed to send OTP. Please try again.'
            })
            
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'An error occurred while sending OTP.'
        })

@login_required
def profile(request):
    """User profile view."""
    context = {
        'user': request.user
    }
    
    if hasattr(request.user, 'studentprofile'):
        context['profile'] = request.user.studentprofile
        context['user_type'] = 'student'
    elif hasattr(request.user, 'adminprofile'):
        context['profile'] = request.user.adminprofile
        context['user_type'] = 'admin'
    elif hasattr(request.user, 'teacherprofile'):
        context['profile'] = request.user.teacherprofile
        context['user_type'] = 'teacher'
    
    return render(request, 'accounts/profile.html', context)
