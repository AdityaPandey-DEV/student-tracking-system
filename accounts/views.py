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

from .models import User, StudentProfile, AdminProfile, TeacherProfile, OTP, EmailOTP
from utils.notifications import send_otp_notification
import logging

logger = logging.getLogger(__name__)

def handle_otp_notification(email, otp_code, purpose='registration', method='email'):
    """
    Helper function to handle OTP notification and return standardized result.
    Returns: (success: bool, otp_code: str, error_message: str)
    """
    result = send_otp_notification(email, otp_code, purpose, method=method)
    if isinstance(result, tuple):
        return result
    else:
        # Backward compatibility for old return format (boolean)
        return (result, otp_code, None if result else "OTP sending failed")

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
    """Handle step 1 of student registration - collect info and send Email OTP (FREE)."""
    try:
        # Get form data
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        roll_number = request.POST.get('roll_number', '').strip().upper()
        course = request.POST.get('course', '').strip()
        year = int(request.POST.get('year', 0))
        section = request.POST.get('section', '').strip().upper()
        email = request.POST.get('email', '').strip().lower()
        phone_number = request.POST.get('phone_number', '').strip()  # Optional now
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        
        # Validation
        errors = []
        
        if not all([first_name, last_name, roll_number, course, year, section, email, password]):
            errors.append('All required fields must be filled.')
        
        if year not in [1, 2, 3, 4]:
            errors.append('Invalid year. Must be 1-4.')
        
        if len(section) != 1 or not section.isalpha():
            errors.append('Section must be a single letter (A, B, C, etc.)')
        
        if not re.match(r'^[A-Z0-9]+$', roll_number):
            errors.append('Roll number should contain only uppercase letters and numbers.')
        
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            errors.append('Invalid email format.')
        
        if phone_number and not re.match(r'^\+?[\d\s\-\(\)]{10,15}$', phone_number):
            errors.append('Invalid phone number format.')
        
        if len(password) < 6:
            errors.append('Password must be at least 6 characters long.')
        
        if password != confirm_password:
            errors.append('Passwords do not match.')
        
        # Check uniqueness - prevent duplicate registration
        if StudentProfile.objects.filter(roll_number=roll_number).exists():
            errors.append('Roll number already exists.')
        
        if User.objects.filter(email=email).exists():
            errors.append('Email already registered. If you already have an account, please login instead.')
        
        if User.objects.filter(username=roll_number).exists():
            errors.append('This roll number is already taken.')
        
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'accounts/student_register.html')
        
        # Generate and send Email OTP (FREE!)
        otp_code = EmailOTP.generate_otp(email, 'registration')
        
        # Send OTP notification (returns tuple: success, otp_code, error_message)
        result = send_otp_notification(email, otp_code, 'registration', method='email')
        if isinstance(result, tuple):
            success, otp_code, error_message = result
        else:
            # Backward compatibility for old return format
            success = result
            error_message = None
        
        if success:
            # Store registration data in session
            request.session['reg_data'] = {
                'first_name': first_name,
                'last_name': last_name,
                'roll_number': roll_number,
                'course': course,
                'year': year,
                'section': section,
                'email': email,
                'phone_number': phone_number or '',  # Optional
                'password': password,
                'user_type': 'student'
            }
            
            # Check if there was an error but OTP is still valid
            if error_message:
                # Network error - show OTP in message as fallback
                if 'Network' in error_message or 'unreachable' in error_message:
                    messages.warning(request, f'⚠️ Email sending failed due to network issue. Your OTP code is: <strong>{otp_code}</strong>. Please use this code to complete registration.')
                    logger.warning(f"Showing OTP in UI due to network error: {otp_code} for {email}")
                else:
                    messages.warning(request, f'⚠️ {error_message}. Your OTP code is: <strong>{otp_code}</strong>. Please use this code to complete registration.')
            else:
                messages.success(request, f'📧 OTP sent to {email}. Please check your email and enter the 6-digit code to complete registration.')
            
            return render(request, 'accounts/student_register.html', {
                'step': 2,
                'email': email,
                'show_otp': bool(error_message),  # Show OTP in template if email failed
                'otp_code': otp_code if error_message else None  # Pass OTP code to template
            })
        else:
            messages.error(request, f'Failed to send OTP email: {error_message if error_message else "Unknown error"}. Please try again or contact support.')
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
                'email': reg_data['email']
            })
        
        # Verify Email OTP
        if EmailOTP.verify_otp(reg_data['email'], otp_code, 'registration'):
            # Create user and profile
            with transaction.atomic():
                user = User.objects.create_user(
                    username=reg_data['roll_number'],
                    email=reg_data['email'],
                    first_name=reg_data['first_name'],
                    last_name=reg_data['last_name'],
                    phone_number=reg_data.get('phone_number') or '',
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
            
            messages.success(request, '✅ Registration successful! Your email has been verified. You can now log in.')
            return redirect('accounts:login')
        else:
            messages.error(request, 'Invalid or expired OTP. Please try again.')
            return render(request, 'accounts/student_register.html', {
                'step': 2,
                'email': reg_data['email']
            })
            
    except Exception as e:
        messages.error(request, 'An error occurred during verification. Please try again.')
        return render(request, 'accounts/student_register.html', {
            'step': 2,
            'email': request.session.get('reg_data', {}).get('email', '')
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
    """Handle step 1 of admin registration - collect info and send Email OTP (FREE)."""
    try:
        # Get form data
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        admin_id = request.POST.get('admin_id', '').strip().upper()
        department = request.POST.get('department', '').strip()
        designation = request.POST.get('designation', '').strip()
        email = request.POST.get('email', '').strip().lower()
        phone_number = request.POST.get('phone_number', '').strip()  # Optional now
        password = request.POST.get('password', '')
        confirm_password = request.POST.get('confirm_password', '')
        
        # Validation
        errors = []
        
        if not all([first_name, last_name, admin_id, department, email, password]):
            errors.append('All required fields must be filled.')
        
        if not re.match(r'^[A-Z0-9]+$', admin_id):
            errors.append('Admin ID should contain only uppercase letters and numbers.')
        
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            errors.append('Invalid email format.')
        
        if phone_number and not re.match(r'^\+?[\d\s\-\(\)]{10,15}$', phone_number):
            errors.append('Invalid phone number format.')
        
        if len(password) < 6:
            errors.append('Password must be at least 6 characters long.')
        
        if password != confirm_password:
            errors.append('Passwords do not match.')
        
        # Check uniqueness
        if AdminProfile.objects.filter(admin_id=admin_id).exists():
            errors.append('Admin ID already exists.')
        
        if User.objects.filter(email=email).exists():
            errors.append('Email already registered.')
        
        if phone_number and User.objects.filter(phone_number=phone_number).exists():
            errors.append('Phone number already registered.')
        
        if User.objects.filter(username=admin_id).exists():
            errors.append('This admin ID is already taken.')
        
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'accounts/admin_register.html')
        
        # Generate and send Email OTP (FREE!)
        otp_code = EmailOTP.generate_otp(email, 'registration')
        
        success, otp_code, error_message = handle_otp_notification(email, otp_code, 'registration')
        
        if success:
            # Store registration data in session
            request.session['reg_data'] = {
                'first_name': first_name,
                'last_name': last_name,
                'admin_id': admin_id,
                'department': department,
                'designation': designation,
                'email': email,
                'phone_number': phone_number or '',  # Optional
                'password': password,
                'user_type': 'admin'
            }
            
            # Check if there was an error but OTP is still valid
            if error_message:
                if 'Network' in error_message or 'unreachable' in error_message:
                    messages.warning(request, f'⚠️ Email sending failed due to network issue. Your OTP code is: <strong>{otp_code}</strong>. Please use this code to complete registration.')
                else:
                    messages.warning(request, f'⚠️ {error_message}. Your OTP code is: <strong>{otp_code}</strong>. Please use this code to complete registration.')
            else:
                messages.success(request, f'📧 OTP sent to {email}. Please check your email and enter the 6-digit code to complete registration.')
            
            return render(request, 'accounts/admin_register.html', {
                'step': 2,
                'email': email,
                'show_otp': bool(error_message),
                'otp_code': otp_code if error_message else None
            })
        else:
            messages.error(request, f'Failed to send OTP email: {error_message if error_message else "Unknown error"}. Please try again or contact support.')
            return render(request, 'accounts/admin_register.html')
            
    except Exception as e:
        messages.error(request, 'An error occurred. Please try again.')
        return render(request, 'accounts/admin_register.html')

def handle_admin_registration_step2(request):
    """Handle step 2 of admin registration - verify Email OTP and create account."""
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
                'email': reg_data['email']
            })
        
        # Verify Email OTP
        if EmailOTP.verify_otp(reg_data['email'], otp_code, 'registration'):
            # Create user and profile
            with transaction.atomic():
                user = User.objects.create_user(
                    username=reg_data['admin_id'],
                    email=reg_data['email'],
                    first_name=reg_data['first_name'],
                    last_name=reg_data['last_name'],
                    phone_number=reg_data.get('phone_number') or '',
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
            
            messages.success(request, '✅ Admin registration successful! Your email has been verified. You can now log in.')
            return redirect('accounts:login')
        else:
            messages.error(request, 'Invalid or expired OTP. Please try again.')
            return render(request, 'accounts/admin_register.html', {
                'step': 2,
                'email': reg_data['email']
            })
            
    except Exception as e:
        messages.error(request, 'An error occurred during verification. Please try again.')
        return render(request, 'accounts/admin_register.html', {
            'step': 2,
            'email': request.session.get('reg_data', {}).get('email', '')
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
        username = employee_id if employee_id else email
        if User.objects.filter(username=username).exists():
            if employee_id:
                errors.append('Employee ID already taken.')
            else:
                errors.append('Email already used as username. Please provide an Employee ID or use a different email.')
        
        if errors:
            for error in errors:
                messages.error(request, error)
            return render(request, 'accounts/teacher_register.html')
        
        # Generate and send Email OTP (FREE!)
        otp_code = EmailOTP.generate_otp(email, 'registration')
        
        if send_otp_notification(email, otp_code, 'registration', method='email'):
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
            
            # Check if there was an error but OTP is still valid
            if error_message:
                if 'Network' in error_message or 'unreachable' in error_message:
                    messages.warning(request, f'⚠️ Email sending failed due to network issue. Your OTP code is: <strong>{otp_code}</strong>. Please use this code to complete registration.')
                else:
                    messages.warning(request, f'⚠️ {error_message}. Your OTP code is: <strong>{otp_code}</strong>. Please use this code to complete registration.')
            else:
                messages.success(request, f'📧 OTP sent to {email}. Please check your email and enter the 6-digit code to complete registration.')
            
            return render(request, 'accounts/teacher_register.html', {
                'step': 2,
                'email': email,
                'show_otp': bool(error_message),
                'otp_code': otp_code if error_message else None
            })
        else:
            messages.error(request, f'Failed to send OTP email: {error_message if error_message else "Unknown error"}. Please try again or contact support.')
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
                'email': reg_data['email']
            })
        
        # Verify Email OTP
        if EmailOTP.verify_otp(reg_data['email'], otp_code, 'registration'):
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
            
            messages.success(request, '✅ Teacher registration successful! Your email has been verified. You can now log in.')
            return redirect('accounts:login')
        else:
            messages.error(request, 'Invalid or expired OTP. Please try again.')
            return render(request, 'accounts/teacher_register.html', {
                'step': 2,
                'email': reg_data['email']
            })
            
    except Exception as e:
        messages.error(request, 'An error occurred during verification. Please try again.')
        return render(request, 'accounts/teacher_register.html', {
            'step': 2,
            'email': request.session.get('reg_data', {}).get('email', '')
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
        
        # For teachers, also try email if employee_id fails
        user = None
        if user_type == 'teacher':
            # First try with the provided user_id as username
            user = authenticate(request, username=user_id, password=password)
            
            # If that fails and user_id looks like email, try finding by email
            if user is None and '@' in user_id:
                try:
                    # Find user by email and teacher type
                    email_user = User.objects.get(email=user_id, user_type='teacher')
                    user = authenticate(request, username=email_user.username, password=password)
                except User.DoesNotExist:
                    pass
        else:
            # For students and admins, normalize to uppercase (IDs are stored uppercase)
            normalized_id = user_id.upper()
            user = authenticate(request, username=normalized_id, password=password)
            if user is None and user_id != normalized_id:
                # Fallback: try as-is just in case
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
            if user_type == 'teacher':
                messages.error(request, 'Invalid credentials. Please check your Employee ID/Email and password.')
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
    """Forgot password - send OTP to user's email for verification."""
    if request.method == 'POST':
        user_id = request.POST.get('user_id', '').strip()
        user_type = request.POST.get('user_type', 'student')
        
        if not user_id:
            messages.error(request, 'Please enter your user ID or email.')
            return render(request, 'accounts/forgot_password.html')
        
        user = None
        # Try email lookup first if it looks like an email
        if '@' in user_id:
            try:
                user = User.objects.get(email=user_id.lower(), user_type=user_type)
            except User.DoesNotExist:
                user = None
        
        # Fallback to username lookup (normalize for student/admin)
        if user is None:
            try:
                lookup_id = user_id.upper() if user_type in ['student', 'admin'] else user_id
                user = User.objects.get(username=lookup_id, user_type=user_type)
            except User.DoesNotExist:
                user = None
        
        if user:
            if not user.email:
                messages.error(request, 'No email is registered with this account. Please contact administrator.')
                return render(request, 'accounts/forgot_password.html')
            
            # Generate Email OTP for password reset
            otp_code = EmailOTP.generate_otp(user.email, 'password_reset')
            
            # Send Email OTP
            success, otp_code, error_message = handle_otp_notification(user.email, otp_code, 'password_reset')
            
            if success:
                request.session['reset_email'] = user.email
                request.session['reset_user_id'] = user.username  # Always store actual username
                request.session['reset_user_type'] = user_type
                
                if error_message:
                    if 'Network' in error_message or 'unreachable' in error_message:
                        messages.warning(request, f'⚠️ Email sending failed. Your OTP code is: <strong>{otp_code}</strong>. Use this code to reset your password.')
                    else:
                        messages.warning(request, f'⚠️ {error_message}. Your OTP code is: <strong>{otp_code}</strong>.')
                else:
                    messages.info(request, f'OTP sent to your registered email {user.email}.')
                return redirect('accounts:verify_otp')
            else:
                messages.error(request, f'Failed to send OTP email: {error_message if error_message else "Unknown error"}. Please try again later.')
        else:
            messages.error(request, 'Account not found. Please check your details and try again.')
    
    return render(request, 'accounts/forgot_password.html')

def verify_otp(request):
    """Verify Email OTP for password reset."""
    if 'reset_email' not in request.session:
        messages.error(request, 'Invalid session. Please start the password reset process again.')
        return redirect('accounts:forgot_password')
    
    if request.method == 'POST':
        otp_code = request.POST.get('otp_code', '').strip()
        
        if not otp_code:
            messages.error(request, 'Please enter the OTP.')
            return render(request, 'accounts/verify_otp.html')
        
        email = request.session['reset_email']
        
        if EmailOTP.verify_otp(email, otp_code, 'password_reset'):
            messages.success(request, 'OTP verified successfully. Please set your new password.')
            return redirect('accounts:reset_password')
        else:
            messages.error(request, 'Invalid or expired OTP. Please try again.')
    
    return render(request, 'accounts/verify_otp.html')

def reset_password(request):
    """Reset password after OTP verification."""
    if 'reset_email' not in request.session or 'reset_user_id' not in request.session:
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
            del request.session['reset_email']
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
    import threading
    
    if 'reg_data' not in request.session:
        return JsonResponse({
            'success': False,
            'message': 'Registration session expired. Please start again.'
        }, status=400)
    
    try:
        reg_data = request.session['reg_data']
        email = reg_data.get('email')
        
        if not email:
            return JsonResponse({
                'success': False,
                'message': 'Email address not found in session.'
            }, status=400)
        
        # Generate new Email OTP
        otp_code = EmailOTP.generate_otp(email, 'registration')
        
        # Send Email OTP in background to prevent timeout (fire-and-forget in production)
        # Return immediately with success, OTP will be sent async
        def send_email_async():
            try:
                handle_otp_notification(email, otp_code, 'registration')
            except Exception as e:
                logger.error(f"Background email send failed: {str(e)}")
        
        # Start email sending in background thread
        email_thread = threading.Thread(target=send_email_async, daemon=True)
        email_thread.start()
        
        # Return success immediately (email is being sent in background)
        # In production, email sending is already non-blocking, but we return immediately here
        # to prevent any potential timeout
        return JsonResponse({
            'success': True,
            'message': f'OTP code sent to {email}. Please check your email inbox.',
            'otp_code': None  # Don't send OTP in response, user should check email
        })
            
    except Exception as e:
        logger.error(f"Error in resend_registration_otp: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'An error occurred while sending OTP. Please try again.'
        }, status=500)

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
