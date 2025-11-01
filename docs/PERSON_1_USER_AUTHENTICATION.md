# 👤 Person 1: User Management & Authentication System

**Name**: ________________  
**Roll Number**: ________________  
**Module**: User Authentication, Profiles, and OTP System  
**Files Handled**: `accounts/models.py`, `accounts/views.py`, `accounts/api_views.py`

---

## 📋 Table of Contents
1. [Project Overview](#project-overview)
2. [Your Responsibilities](#your-responsibilities)
3. [Code Explanation (Line by Line in Hinglish)](#code-explanation)
4. [Database Models](#database-models)
5. [Key Functions](#key-functions)
6. [Testing Guide](#testing-guide)
7. [Viva Questions](#viva-questions)

---

## 🎯 Project Overview

**Student Tracking System** ek complete academic management platform hai jo Django framework pe bana hai. Is system mein students, teachers, aur admins apne respective dashboards access kar sakte hain.

**Aapki Responsibility**: User authentication, registration, login, OTP verification, aur user profiles ka complete management.

---

## 👨‍💻 Your Responsibilities

### Core Tasks:
1. ✅ User Model aur Profile Models ka implementation
2. ✅ Student, Teacher, aur Admin registration system
3. ✅ Email-based OTP verification (FREE - no SMS cost)
4. ✅ Login/Logout functionality
5. ✅ Password reset with OTP
6. ✅ User profile management

### Files You Own:
```
accounts/
├── models.py              ← User, StudentProfile, TeacherProfile, AdminProfile, EmailOTP
├── views.py               ← Registration, Login, OTP verification views
├── api_views.py           ← API endpoints for mobile/SPA
├── urls.py                ← URL routing
└── migrations/            ← Database migrations
```

---

## 💻 Code Explanation (Line by Line in Hinglish)

### 1. User Model (`accounts/models.py`)

```python
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
import random
from datetime import timedelta
```

**Explanation:**
- `AbstractUser`: Django ka built-in user model hai, isko extend kar rahe hain custom fields add karne ke liye
- `models`: Django ORM ke liye - database tables banane ke liye
- `RegexValidator`: Input validation ke liye (jaise roll number format check karna)
- `timezone`: Django ka timezone-aware datetime ke liye
- `random`: OTP generate karne ke liye random numbers chahiye
- `timedelta`: Time calculations ke liye (jaise OTP 10 minute mein expire ho jaye)

---

```python
class User(AbstractUser):
    """Custom user model extending Django's AbstractUser."""
    USER_TYPE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('admin', 'Admin'),
    ]
```

**Hinglish Explanation:**
- `AbstractUser` ko extend kar rahe hain taaki Django ke default fields (username, password, email) mil jayein
- `USER_TYPE_CHOICES`: Ye ek tuple hai jo define karta hai ki user kis type ka ho sakta hai
- First value ('student') database mein save hoti hai
- Second value ('Student') human-readable form hai (display ke liye)

---

```python
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES)
    phone_number = models.CharField(max_length=15, blank=True, null=True, 
                                   help_text="Phone number for SMS notifications")
    is_verified = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**Hinglish Explanation:**
- `user_type`: CharField hai jo USER_TYPE_CHOICES mein se ek value store karega
- `max_length=10`: Maximum 10 characters store ho sakti hain
- `choices=USER_TYPE_CHOICES`: Dropdown mein sirf ye 3 options dikhenge
- `phone_number`: Optional field hai (`blank=True, null=True` means not required)
- `is_verified`: Boolean field - user verified hai ya nahi (default=True rakha hai)
- `created_at`: Automatically user creation time store karega (`auto_now_add=True`)
- `updated_at`: Har baar update hone pe automatically change hoga (`auto_now=True`)

---

### 2. StudentProfile Model

```python
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
```

**Hinglish Explanation:**
- `StudentProfile`: Separate model hai kyunki har student ke liye extra information store karni hai
- `COURSE_CHOICES`: Available courses ki list - database mein 'B.Tech' save hoga, display mein 'Bachelor of Technology' dikhega
- `YEAR_CHOICES`: Year integer mein store hoga (1,2,3,4) but display mein text mein dikhega

---

```python
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    roll_number = models.CharField(
        max_length=20, 
        unique=True,
        validators=[RegexValidator(
            regex=r'^[A-Z0-9]+$',
            message='Roll number should contain only uppercase letters and numbers.'
        )]
    )
```

**Hinglish Explanation:**
- `OneToOneField`: Ek User ke saath sirf ek StudentProfile ho sakti hai (one-to-one relationship)
- `on_delete=models.CASCADE`: Agar User delete ho jaye to uski StudentProfile bhi delete ho jayegi
- `primary_key=True`: User ka ID hi StudentProfile ka primary key ban jayega
- `roll_number`: Unique honi chahiye, koi duplicate nahi
- `RegexValidator`: Roll number mein sirf CAPITAL LETTERS aur NUMBERS allowed hain
- `regex=r'^[A-Z0-9]+$'`: Regular expression - starting se ending tak sirf A-Z aur 0-9

---

```python
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
```

**Hinglish Explanation:**
- `course`: Dropdown mein COURSE_CHOICES se select karenge
- `year`: Integer field - 1, 2, 3, ya 4 ho sakta hai
- `section`: Sirf capital letters (A, B, C, etc.)
- `unique_together`: Same course, year, section mein same roll number nahi ho sakta
  - Example: B.Tech, Year 2, Section A, Roll ABC123 - ye combination unique hona chahiye

---

### 3. EmailOTP Model (FREE Email Verification)

```python
class EmailOTP(models.Model):
    """Email-based OTP model for verification (FREE alternative to SMS)."""
    PURPOSE_CHOICES = [
        ('password_reset', 'Password Reset'),
        ('email_verification', 'Email Verification'),
        ('login_verification', 'Login Verification'),
        ('registration', 'Registration Verification'),
    ]
```

**Hinglish Explanation:**
- Email-based OTP use kar rahe hain kyunki SMS ka paisa lagta hai, email FREE hai
- `PURPOSE_CHOICES`: OTP kis purpose ke liye hai - registration, password reset, etc.

---

```python
    email = models.EmailField()
    otp_code = models.CharField(max_length=6)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES, default='registration')
    is_used = models.BooleanField(default=False)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
```

**Hinglish Explanation:**
- `email`: EmailField automatically validate karta hai ki proper email format hai ya nahi
- `otp_code`: 6 digit ka OTP code (jaise 123456)
- `purpose`: Kis kaam ke liye OTP hai
- `is_used`: OTP use ho gaya hai ya nahi - ek baar use hone ke baad True ho jayega
- `expires_at`: Kab tak valid hai - uske baad expire ho jayega
- `created_at`: OTP kab generate hua tha

---

```python
    @classmethod
    def generate_otp(cls, email, purpose='registration'):
        """Generate a new OTP for the given email address."""
        # Purane OTPs ko invalidate kar do
        cls.objects.filter(
            email=email,
            purpose=purpose,
            is_used=False
        ).update(is_used=True)
        
        # 6-digit OTP generate karo
        otp_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        
        # Naya OTP create karo with 15-minute expiration
        otp = cls.objects.create(
            email=email,
            otp_code=otp_code,
            purpose=purpose,
            expires_at=timezone.now() + timedelta(minutes=15)
        )
        
        return otp_code
```

**Hinglish Explanation:**
- `@classmethod`: Ye method class level pe call hota hai, instance nahi chahiye
- **Step 1**: Pehle check karo ki koi purana unused OTP hai to usko used mark kar do
  - Same email aur purpose ke saath multiple active OTPs nahi chahiye
- **Step 2**: Random 6-digit OTP generate karo
  - `random.randint(0, 9)` - 0 se 9 tak random number
  - 6 baar loop chalake 6 digits banaye
  - `''.join()` se sabko ek string mein join kar diya
- **Step 3**: Database mein naya OTP entry create karo
  - `expires_at`: Current time + 15 minutes (itne time tak valid rahega)
- **Return**: OTP code return karo taaki email mein bhej sakein

---

```python
    @classmethod
    def verify_otp(cls, email, otp_code, purpose='registration'):
        """Verify OTP for the given email address."""
        try:
            otp = cls.objects.get(
                email=email,
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
```

**Hinglish Explanation:**
- **Input**: Email, OTP code, aur purpose
- **Process**:
  1. Database mein OTP dhundo jo match kare:
     - Same email
     - Same OTP code
     - Same purpose
     - Abhi tak use nahi hua (`is_used=False`)
     - Expire nahi hua (`expires_at__gt=timezone.now()` means expiry time current time se greater hai)
  2. Agar mil gaya:
     - `is_used=True` kar do (taaki dobara use na ho sake)
     - Save kar do
     - Return `True` (OTP correct tha)
  3. Agar nahi mila:
     - Return `False` (OTP wrong/expired tha)

---

### 4. Registration View (`accounts/views.py`)

```python
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db import transaction
from django.utils import timezone
import json

from .models import User, StudentProfile, AdminProfile, TeacherProfile, EmailOTP
from utils.notifications import send_otp_notification
```

**Hinglish Explanation:**
- `render`: HTML template render karne ke liye
- `redirect`: User ko different page pe redirect karne ke liye
- `get_object_or_404`: Object dhundo, nahi mila to 404 error
- `login, authenticate, logout`: Django ke built-in authentication functions
- `login_required`: Decorator - sirf logged-in users access kar sakein
- `messages`: Flash messages show karne ke liye (success/error alerts)
- `JsonResponse`: JSON response return karne ke liye (AJAX requests)
- `transaction`: Database transactions ko atomic banane ke liye
- `send_otp_notification`: Custom utility function email bhejne ke liye
- Models import kiye jo use honge

---

**Real Implementation: Two-Step Registration Process**

```python
def student_register(request):
    """Student registration view with 2-step OTP verification."""
    if request.method == 'POST':
        step = request.POST.get('step', '1')
        
        if step == '1':
            # Step 1: Basic info collect karo aur OTP bhejo
            return handle_student_registration_step1(request)
        elif step == '2':
            # Step 2: OTP verify karo aur registration complete karo
            return handle_student_registration_step2(request)
    
    return render(request, 'accounts/student_register.html')
```

**Hinglish Explanation:**
- **Two-step process kyun?** Security aur better user experience ke liye
- **Step 1**: User details collect karo → OTP bhejo → Wait for verification
- **Step 2**: OTP verify karo → User create karo → Auto-login
- `step` parameter se decide hota hai konsa step execute karna hai

---

### Step 1: Basic Info Collection & OTP Sending

```python
def handle_student_registration_step1(request):
    """Step 1: Collect info and send Email OTP (FREE)."""
    try:
        # Form data extract karo
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip().lower()
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password')
        roll_number = request.POST.get('roll_number', '').strip().upper()
        course = request.POST.get('course')
        year = int(request.POST.get('year'))
        section = request.POST.get('section', '').strip().upper()
```

**Hinglish Explanation:**
- `request.POST.get('field', '')`: Field ki value nikalo, agar nahi hai to empty string
- `.strip()`: Extra spaces remove karo (leading/trailing whitespace)
- `.lower()`: Email ko lowercase mein convert karo (consistency ke liye)
- `.upper()`: Roll number aur section ko uppercase mein (standard format)
- `int()`: Year ko string se integer mein convert karo
- **Error handling**: Try-except block mein wrap kiya hai safety ke liye

---

```python
        # Validation 1: Required fields check
        if not all([first_name, last_name, email, username, password, 
                   roll_number, course, year, section]):
            return JsonResponse({
                'success': False,
                'message': 'All fields are required!'
            })
        
        # Validation 2: Username already exists check
        if User.objects.filter(username=username).exists():
            return JsonResponse({
                'success': False,
                'message': 'Username already taken! Please choose another.'
            })
        
        # Validation 3: Email already registered check
        if User.objects.filter(email=email).exists():
            return JsonResponse({
                'success': False,
                'message': 'Email already registered! Try logging in.'
            })
        
        # Validation 4: Roll number already exists check
        if StudentProfile.objects.filter(roll_number=roll_number).exists():
            return JsonResponse({
                'success': False,
                'message': 'Roll number already exists!'
            })
```

**Hinglish Explanation:**
- **Validation 1**: `all()` function check karta hai ki saare fields filled hain ya nahi
  - Agar koi bhi field empty hai to False return
  - Early return se unnecessary database queries avoid hoti hain
- **Validation 2**: Username uniqueness check
  - `.filter(username=username)` - is username wala user dhundo
  - `.exists()` - agar mil gaya to True, nahi to False (efficient query)
  - Agar mil gaya: JSON response return karo with error
- **Validation 3**: Email duplication check (same logic)
- **Validation 4**: Roll number unique hona chahiye ek course/year/section mein
- **JsonResponse kyun?**: AJAX request hai to JSON response better hai (page reload nahi hoga)

---

```python
        # Generate OTP for email verification
        otp_code = EmailOTP.generate_otp(email, purpose='registration')
        
        # Send OTP via email using utility function
        email_sent = send_otp_notification(
            email=email,
            otp_code=otp_code,
            purpose='registration',
            user_name=first_name
        )
        
        if not email_sent:
            return JsonResponse({
                'success': False,
                'message': 'Failed to send OTP email. Please try again.'
            })
```

**Hinglish Explanation:**
- `EmailOTP.generate_otp()`: Humara custom method - 6 digit OTP generate karega
  - Purane unused OTPs ko invalid kar dega
  - Naya OTP database mein save karega
  - OTP code return karega
- **`send_otp_notification()`**: Custom utility function (utils/notifications.py mein hai)
  - Email formatting handle karta hai
  - HTML template use karta hai (professional look)
  - Error handling include hai
  - True/False return karta hai (success/failure)
- **Error handling**: Agar email send fail ho jaye to user ko inform karo
- **Why separate function?**: Code reusability - same function registration, password reset, etc. mein use hoga

---

```python
        # Store registration data in session (temporary storage)
        request.session['student_registration_data'] = {
            'username': username,
            'email': email,
            'password': password,
            'first_name': first_name,
            'last_name': last_name,
            'roll_number': roll_number,
            'course': course,
            'year': year,
            'section': section,
            'user_type': 'student',
            'timestamp': timezone.now().isoformat()  # Track when data was stored
        }
        
        # Save session immediately
        request.session.modified = True
        
        return JsonResponse({
            'success': True,
            'message': f'OTP sent to {email}. Please check your email.',
            'email': email
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Registration error: {str(e)}'
        })
```

**Hinglish Explanation:**
- **Session Storage**: Form ka saara data session mein temporarily store kiya
  - Kyunki OTP verification ke baad hi user create karenge
  - Session server-side storage hai - secure hai
  - Browser mein sirf session ID cookie ke form mein save hoti hai
- **`timestamp`**: Kab store hua ye track karne ke liye (session timeout check mein useful)
- **`request.session.modified = True`**: Django ko force karo ki session ko save kare
  - Sometimes Django automatically detect nahi karta ki nested dictionary update hui hai
- **JSON Response**: AJAX request ko response bheja
  - Frontend pe JavaScript handle karega next step
- **Exception handling**: Koi bhi unexpected error ko catch karo aur user-friendly message show karo

---

### Step 2: OTP Verification & User Creation

```python
def handle_student_registration_step2(request):
    """Step 2: Verify OTP and create user account."""
    try:
        # Get OTP code from form
        otp_code = request.POST.get('otp_code', '').strip()
        
        # Get registration data from session
        registration_data = request.session.get('student_registration_data')
        
        if not registration_data:
            return JsonResponse({
                'success': False,
                'message': 'Session expired. Please start registration again.'
            })
        
        email = registration_data['email']
        
        # Verify OTP
        if not EmailOTP.verify_otp(email, otp_code, purpose='registration'):
            return JsonResponse({
                'success': False,
                'message': 'Invalid or expired OTP. Please try again.'
            })
```

**Hinglish Explanation:**
- **Step 2 ka purpose**: OTP verify karna aur user account create karna
- Form se user ka entered OTP nikalo
- Session se pehle store kiya hua registration data nikalo
- **Session check**: Agar data nahi mila (session expire ho gaya):
  - Error return karo
  - User ko dobara registration start karna padega
- **OTP Verification**: `EmailOTP.verify_otp()` call karo
  - Ye method database se OTP match karega
  - Check karega ki expired to nahi
  - Check karega ki pehle use to nahi ho gaya
  - True/False return karega

---

```python
        # OTP verified successfully - Create user with transaction
        with transaction.atomic():
            # Create User account
            user = User.objects.create_user(
                username=registration_data['username'],
                email=registration_data['email'],
                password=registration_data['password'],
                first_name=registration_data['first_name'],
                last_name=registration_data['last_name'],
                user_type='student',
                is_verified=True
            )
            
            # Create StudentProfile
            StudentProfile.objects.create(
                user=user,
                roll_number=registration_data['roll_number'],
                course=registration_data['course'],
                year=registration_data['year'],
                section=registration_data['section']
            )
        
        # Auto-login the user
        login(request, user)
        
        # Clear session data (cleanup)
        del request.session['student_registration_data']
        request.session.modified = True
        
        return JsonResponse({
            'success': True,
            'message': 'Registration successful! Redirecting to dashboard...',
            'redirect_url': '/student/dashboard/'
        })
    
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'Registration failed: {str(e)}'
        })
```

**Hinglish Explanation:**
- **`transaction.atomic()`**: Database transaction mein wrap kiya
  - Agar User create ho gaya but StudentProfile create fail ho jaye:
    - Pura transaction rollback ho jayega
    - Database inconsistent state mein nahi rahega
  - **ACID properties** maintain hoti hain
- **User Creation**:
  - `create_user()` method password ko automatically hash kar deta hai
  - `is_verified=True` set kiya kyunki email already verify ho gaya
- **StudentProfile Creation**:
  - user object pass kiya (OneToOne relationship)
  - Student-specific fields bhi add kiye
- **Auto-login**:
  - Django ka `login()` function use karke user ko login kar diya
  - Session create ho gaya
  - User ko manually login karne ki zarurat nahi
- **Session Cleanup**:
  - Registration data delete kar diya
  - Memory aur security ke liye important
- **JSON Response**: Frontend ko success response with redirect URL

---

```python
# GET request handler
def student_register(request):
    """Show blank registration form for GET requests."""
    return render(request, 'accounts/student_register.html')
```

**Hinglish Explanation:**
- Agar POST request nahi hai (matlab page pehli baar load ho raha hai)
- To blank registration form show karo
- User form fill karega aur submit karega (Step 1 trigger hoga)

---

### 5. Complete Registration Flow Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                    REGISTRATION FLOW                             │
└─────────────────────────────────────────────────────────────────┘

USER                    FRONTEND                 BACKEND               DATABASE
 │                         │                        │                    │
 │  1. Opens /register     │                        │                    │
 │─────────────────────────>                        │                    │
 │                         │   GET request          │                    │
 │                         │───────────────────────>│                    │
 │                         │   Blank form HTML      │                    │
 │                         │<───────────────────────│                    │
 │                         │                        │                    │
 │  2. Fills form & submits│                        │                    │
 │─────────────────────────>                        │                    │
 │                         │   POST (step=1)        │                    │
 │                         │───────────────────────>│                    │
 │                         │                        │ Check duplicates   │
 │                         │                        │───────────────────>│
 │                         │                        │ No duplicates      │
 │                         │                        │<───────────────────│
 │                         │                        │                    │
 │                         │                        │ Generate OTP       │
 │                         │                        │───────────────────>│
 │                         │                        │ OTP saved          │
 │                         │                        │<───────────────────│
 │                         │                        │                    │
 │                         │                        │ Send email         │
 │                         │                        │────────────────>   │
 │  3. OTP email received  │                        │                    │
 │<────────────────────────────────────────────────────────────────────  │
 │                         │   JSON success         │                    │
 │                         │<───────────────────────│                    │
 │  4. Shows OTP input     │                        │                    │
 │<─────────────────────────                        │                    │
 │                         │                        │                    │
 │  5. Enters OTP & submits│                        │                    │
 │─────────────────────────>                        │                    │
 │                         │   POST (step=2)        │                    │
 │                         │───────────────────────>│                    │
 │                         │                        │ Verify OTP         │
 │                         │                        │───────────────────>│
 │                         │                        │ OTP valid ✓        │
 │                         │                        │<───────────────────│
 │                         │                        │                    │
 │                         │                        │ Create User        │
 │                         │                        │───────────────────>│
 │                         │                        │ User created       │
 │                         │                        │<───────────────────│
 │                         │                        │                    │
 │                         │                        │ Create Profile     │
 │                         │                        │───────────────────>│
 │                         │                        │ Profile created    │
 │                         │                        │<───────────────────│
 │                         │   Success + redirect   │                    │
 │                         │<───────────────────────│                    │
 │  6. Redirect to dashboard                        │                    │
 │<─────────────────────────                        │                    │
 │                         │                        │                    │
 └─────────────────────────┴────────────────────────┴────────────────────┘
```

**Key Points:**
1. **Two-step process** - Data collection + OTP verification
2. **Session storage** - Temporary data storage between steps
3. **Email-based** - FREE verification (no SMS cost)
4. **Transaction-safe** - Atomic database operations
5. **Auto-login** - Seamless user experience

---

### 6. Login View

```python
def user_login(request):
    """Login view for all user types."""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        # Authenticate user
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            
            # Redirect based on user type
            if user.user_type == 'student':
                return redirect('student_dashboard')
            elif user.user_type == 'teacher':
                return redirect('teacher_dashboard')
            elif user.user_type == 'admin':
                return redirect('admin_dashboard')
        else:
            messages.error(request, 'Invalid username or password!')
            return redirect('login')
    
    return render(request, 'accounts/login.html')
```

**Hinglish Explanation:**
- Form se username aur password nikalo
- **`authenticate()`**: Django ka built-in function
  - Database mein user dhundta hai
  - Password hash ko check karta hai (plain text compare nahi karta)
  - Agar credentials correct hain: User object return karta hai
  - Agar wrong: None return karta hai
- **Agar user mil gaya** (`user is not None`):
  - `login()` function call karo - session create hota hai
  - User type ke basis pe different dashboard pe redirect karo
- **Agar user nahi mila**:
  - Error message show karo
  - Login page pe wapas bhej do

---

## 🗄️ Database Models Summary

### User Model Fields:
| Field | Type | Purpose |
|-------|------|---------|
| id | Integer (PK) | Unique identifier |
| username | String (Unique) | Login username |
| email | Email (Unique) | Email address |
| password | String (Hashed) | Encrypted password |
| user_type | String | student/teacher/admin |
| phone_number | String (Optional) | Contact number |
| is_verified | Boolean | Email verification status |
| created_at | DateTime | Account creation time |
| updated_at | DateTime | Last update time |

### StudentProfile Fields:
| Field | Type | Purpose |
|-------|------|---------|
| user | OneToOne FK | Link to User |
| roll_number | String (Unique) | Student ID |
| course | String | B.Tech, BCA, etc. |
| year | Integer | 1, 2, 3, 4 |
| section | String | A, B, C, etc. |

### EmailOTP Fields:
| Field | Type | Purpose |
|-------|------|---------|
| email | Email | Recipient email |
| otp_code | String (6) | 6-digit OTP |
| purpose | String | registration/password_reset |
| is_used | Boolean | Used or not |
| expires_at | DateTime | Expiration time |
| created_at | DateTime | Generation time |

---

## 🔑 Key Functions You Implemented

### 1. `generate_otp(email, purpose)`
**Purpose**: Email ke liye 6-digit OTP generate karna  
**Returns**: OTP code (string)  
**Logic**: 
1. Purane unused OTPs ko invalid kar do
2. Random 6-digit number generate karo
3. Database mein save karo with 15-minute expiry
4. OTP code return karo

### 2. `verify_otp(email, otp_code, purpose)`
**Purpose**: User ka entered OTP verify karna  
**Returns**: True (correct) ya False (wrong/expired)  
**Logic**:
1. Database mein matching OTP dhundo
2. Check karo: not used, not expired
3. Agar mil gaya: mark as used, return True
4. Agar nahi mila: return False

### 3. `student_register(request)`
**Purpose**: Student registration handle karna  
**Process**:
1. Form data validate karo
2. Duplicate check karo
3. OTP generate karo
4. Email bhejo
5. Session mein data store karo
6. OTP verification page pe redirect karo

### 4. `verify_otp(request)` (View)
**Purpose**: OTP verification aur user creation  
**Process**:
1. Session se data nikalo
2. User ka OTP verify karo
3. User aur Profile create karo
4. Auto-login karo
5. Dashboard pe redirect karo

### 5. `user_login(request)`
**Purpose**: Login authentication  
**Process**:
1. Credentials validate karo
2. User authenticate karo
3. User type ke basis pe redirect karo

---

## 🧪 Testing Guide

### Test Case 1: Student Registration
**Steps**:
1. `/register/student/` pe jao
2. Form fill karo with valid data
3. "Register" button click karo
4. Check email for OTP
5. OTP enter karo
6. Verify: Student dashboard dikhna chahiye

**Expected Result**: User successfully register ho jaye aur dashboard pe redirect ho jaye

---

### Test Case 2: Duplicate Registration
**Steps**:
1. Existing username/email se register karne ki koshish karo
2. Submit karo

**Expected Result**: Error message show hona chahiye: "Username/Email already taken"

---

### Test Case 3: Invalid OTP
**Steps**:
1. Registration ke baad wrong OTP enter karo
2. Submit karo

**Expected Result**: Error message: "Invalid or expired OTP"

---

### Test Case 4: Expired OTP
**Steps**:
1. Registration karo
2. 15 minutes wait karo
3. OTP enter karo

**Expected Result**: Error message: "Invalid or expired OTP"

---

### Test Case 5: Login Success
**Steps**:
1. `/login/` pe jao
2. Correct username aur password enter karo
3. Login click karo

**Expected Result**: User type ke according dashboard dikhna chahiye

---

### Test Case 6: Login Failure
**Steps**:
1. Wrong username/password enter karo
2. Login click karo

**Expected Result**: Error message: "Invalid username or password"

---

## 📝 Viva Questions & Answers

### Basic Questions:

**Q1: Django mein AbstractUser kya hai aur aapne isko kyun extend kiya?**  
**Ans**: AbstractUser Django ka built-in user model hai jo basic authentication fields provide karta hai (username, password, email, etc.). Humne isko extend kiya kyunki humein extra fields chahiye the jaise user_type, phone_number, is_verified. Agar hum AbstractUser extend nahi karte to in sabko manually banana padta jo bahut time-consuming aur error-prone hota.

---

**Q2: OneToOneField aur ForeignKey mein kya difference hai?**  
**Ans**: 
- **OneToOneField**: Ek record ka dusre table ke ek hi record ke saath relation hota hai. Example: Ek User ki sirf ek StudentProfile ho sakti hai.
- **ForeignKey**: Ek record ke multiple relations ho sakte hain. Example: Ek Teacher ke multiple TimetableEntry ho sakte hain.

OneToOneField internally ForeignKey hai but with unique=True constraint.

---

**Q3: OTP ko database mein store karna safe hai ya nahi?**  
**Ans**: Haan, safe hai kyunki:
1. OTP plain text mein store hai but wo temporary hai (15 minutes)
2. Ek baar use hone ke baad `is_used=True` ho jata hai
3. Expired OTPs automatically invalid ho jate hain
4. OTP ko password ki tarah hash karne ki zarurat nahi kyunki wo short-lived hai

Lekin production mein expired OTPs ko periodically clean karna chahiye (celery task se).

---

**Q4: `auto_now_add=True` aur `auto_now=True` mein kya difference hai?**  
**Ans**:
- **`auto_now_add=True`**: Sirf ek baar set hota hai jab record pehli baar create hota hai. Useful for created_at field.
- **`auto_now=True`**: Har baar update hota hai jab record save hota hai. Useful for updated_at field.

Example:
```python
created_at = models.DateTimeField(auto_now_add=True)  # Sirf ek baar set
updated_at = models.DateTimeField(auto_now=True)      # Har save pe update
```

---

**Q5: Session storage kya hai aur aapne registration data session mein kyun store kiya?**  
**Ans**: Session ek server-side storage hai jo user-specific data temporarily store karta hai. Django automatically ek session ID generate karta hai jo user ke browser mein cookie ke form mein save hoti hai.

Registration data session mein isliye store kiya kyunki:
1. OTP verification alag page pe hota hai
2. Verification successful hone ke baad hi user create karna hai
3. Session mein data secure rahta hai (cookie mein sirf session ID hoti hai)
4. Temporary storage hai - verification ke baad delete kar dete hain

---

### Intermediate Questions:

**Q6: RegexValidator ka use kyun kiya roll_number mein?**  
**Ans**: RegexValidator se hum input format ko control kar sakte hain:
```python
regex=r'^[A-Z0-9]+$'
```
- `^` = String ka start
- `[A-Z0-9]` = Sirf capital letters aur numbers allowed
- `+` = Ek ya zyada characters
- `$` = String ka end

Isse invalid roll numbers database mein save nahi honge (jaise lowercase letters, special characters). Ye data integrity maintain karta hai.

---

**Q7: `create_user()` method ko `create()` ke jagah kyun use kiya?**  
**Ans**: `create_user()` Django ka special method hai jo password ko automatically hash kar deta hai using PBKDF2 algorithm with salt. 

Agar hum `User.objects.create()` use karein to password plain text mein save hoga jo major security issue hai.

```python
# WRONG - Password plain text mein save hoga
User.objects.create(username='test', password='password123')

# CORRECT - Password hash hoke save hoga
User.objects.create_user(username='test', password='password123')
```

---

**Q8: `unique_together` constraint ka kya use hai StudentProfile mein?**  
**Ans**: `unique_together` ensure karta hai ki multiple fields ka combination unique ho:
```python
unique_together = ['course', 'year', 'section', 'roll_number']
```

Matlab same course, year, aur section mein same roll number nahi ho sakta:
- ✅ Allowed: B.Tech, Year 2, Section A, Roll ABC123
- ✅ Allowed: B.Tech, Year 2, Section B, Roll ABC123 (Section different hai)
- ❌ Not Allowed: B.Tech, Year 2, Section A, Roll ABC123 (Duplicate)

Ye ensure karta hai ki ek class mein koi duplicate roll number na ho.

---

**Q9: authenticate() aur login() mein kya difference hai?**  
**Ans**:
- **`authenticate()`**: 
  - Username aur password ko verify karta hai
  - Database query karta hai
  - Password hash match karta hai
  - User object return karta hai (ya None agar wrong credentials)
  - Session create NAHI karta

- **`login()`**:
  - User object ko as authenticated mark karta hai
  - Session create karta hai
  - Cookie browser mein save karta hai
  - Future requests mein user authenticated rahega

Dono ek saath use hote hain:
```python
user = authenticate(username='test', password='pass')  # Verify
if user:
    login(request, user)  # Create session
```

---

**Q10: EmailOTP model mein `@classmethod` ka use kyun kiya?**  
**Ans**: `@classmethod` use kiya kyunki:
1. Method ko class level pe call karna hai (instance ki zarurat nahi)
2. OTP generate karne ke liye existing OTP object ki zarurat nahi hai
3. Method mein `cls` parameter milta hai jo class ko represent karta hai

```python
# Class method - No instance needed
otp = EmailOTP.generate_otp('test@email.com')

# Instance method - Instance chahiye hota
otp_object = EmailOTP.objects.get(id=1)
result = otp_object.is_expired()
```

---

### Advanced Questions:

**Q11: Agar multiple users ek hi time pe same email se OTP generate karein to kya hoga?**  
**Ans**: Race condition handle karne ke liye humne logic likha hai:
1. Pehle sabhi unused OTPs ko `is_used=True` kar dete hain
2. Phir naya OTP generate karte hain
3. Latest OTP hi valid rahega

Lekin agar bilkul same time pe 2 requests aayein to:
- Database level pe transaction isolation se handle hota hai
- Django's atomic transactions ensure karte hain ki data corrupt na ho
- Latest generated OTP ko hi valid mana jayega

Better approach: Celery task queue use karein OTP generation ke liye.

---

**Q12: Password reset functionality implement kaise karenge?**  
**Ans**: Same EmailOTP model use karenge with different purpose:
```python
# Step 1: Generate OTP
otp = EmailOTP.generate_otp(email, purpose='password_reset')

# Step 2: Send email
send_mail(subject, message, from_email, [email])

# Step 3: Verify OTP
if EmailOTP.verify_otp(email, otp_code, purpose='password_reset'):
    # Step 4: Allow password change
    user.set_password(new_password)
    user.save()
```

`purpose='password_reset'` ensure karega ki registration OTP password reset mein use na ho sake.

---

**Q13: `on_delete=models.CASCADE` ka kya effect hai?**  
**Ans**: Jab parent record delete hota hai to child record bhi delete ho jayega:

```python
user = models.OneToOneField(User, on_delete=models.CASCADE)
```

Example:
- User delete kiya → StudentProfile bhi automatically delete hoga

Other options:
- **`CASCADE`**: Child bhi delete (Default for OneToOne)
- **`SET_NULL`**: Child ka foreign key NULL set ho jayega
- **`PROTECT`**: Parent delete nahi hoga agar child exist karti hai
- **`SET_DEFAULT`**: Child mein default value set hogi

---

**Q14: Session security ke liye kya precautions lene chahiye?**  
**Ans**: Session security important hai kyunki sensitive data store hota hai:

**Best Practices**:
1. **HTTPS use karo**: Session cookies ko secure flag ke saath send karo
2. **SESSION_COOKIE_HTTPONLY = True**: JavaScript se cookie access na ho
3. **SESSION_COOKIE_SECURE = True**: Sirf HTTPS pe cookie send ho
4. **SESSION_EXPIRE_AT_BROWSER_CLOSE = True**: Browser close hone pe session expire
5. **Sensitive data encrypt karo**: Password kabhi session mein mat store karo
6. **Session timeout**: Inactive users ko automatic logout karo

```python
# settings.py
SESSION_COOKIE_SECURE = True  # HTTPS only
SESSION_COOKIE_HTTPONLY = True  # No JavaScript access
SESSION_COOKIE_SAMESITE = 'Strict'  # CSRF protection
SESSION_COOKIE_AGE = 3600  # 1 hour timeout
```

---

**Q15: Email sending fail ho jaye to kya hoga? Error handling kaise karein?**  
**Ans**: Currently `fail_silently=False` hai, matlab error throw hoga. Production ke liye better error handling:

```python
from django.core.mail import send_mail
from django.db import transaction
import logging

logger = logging.getLogger(__name__)

def send_otp_email(email, otp_code):
    try:
        send_mail(
            subject='Your OTP',
            message=f'Your OTP is: {otp_code}',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        logger.error(f'Email failed for {email}: {str(e)}')
        # Retry logic ya alternative notification
        return False

# View mein
with transaction.atomic():
    otp_code = EmailOTP.generate_otp(email)
    if not send_otp_email(email, otp_code):
        messages.error(request, 'Failed to send OTP. Please try again.')
        return redirect('register')
```

**Better approach**:
- Celery task queue use karo (asynchronous email sending)
- Retry mechanism implement karo
- Backup notification method (SMS fallback)

---

**Q16: Database indexing ka kya role hai aur aapke models mein kahan apply karni chahiye?**  
**Ans**: Index database query ko fast banata hai (like book index). Django automatically index create karta hai:
1. Primary keys pe
2. Foreign keys pe
3. Unique fields pe

**Additional indexes needed**:
```python
class User(AbstractUser):
    email = models.EmailField(db_index=True)  # Login queries fast hongi
    user_type = models.CharField(db_index=True)  # Filter by type fast
    
class StudentProfile(models.Model):
    roll_number = models.CharField(unique=True)  # Already indexed
    
    class Meta:
        indexes = [
            models.Index(fields=['course', 'year', 'section']),  # Composite index
        ]
```

**Trade-off**:
- ✅ SELECT queries fast (90% faster)
- ❌ INSERT/UPDATE slow (10% slower)
- ❌ Extra storage space

Rule: Frequently queried fields pe index lagao.

---

**Q17: Production environment mein kaise ensure karein ki duplicate users create na ho (race condition)?**  
**Ans**: Race condition tab hoti hai jab 2 requests ek saath process ho:

**Problem**:
```
Time T1: Request A checks - Username 'john' doesn't exist ✅
Time T2: Request B checks - Username 'john' doesn't exist ✅
Time T3: Request A creates user 'john' ✅
Time T4: Request B creates user 'john' ✅ DUPLICATE!
```

**Solutions**:

1. **Database constraints** (Best):
```python
username = models.CharField(unique=True)  # Database level constraint
```
Django automatically constraint create karta hai. Agar duplicate insert ho to `IntegrityError` raise hoga.

2. **Transaction atomicity**:
```python
from django.db import transaction

with transaction.atomic():
    if not User.objects.filter(username=username).exists():
        User.objects.create_user(...)
```

3. **Database-level locks**:
```python
from django.db import transaction

with transaction.atomic():
    User.objects.select_for_update().filter(username=username)
    # Create user
```

**Best practice**: Database constraints + try-except:
```python
try:
    user = User.objects.create_user(username=username, ...)
except IntegrityError:
    messages.error(request, 'Username already exists!')
```

---

**Q18: `messages` framework kaise kaam karta hai Django mein?**  
**Ans**: Django messages ek temporary storage hai jo flash messages show karta hai:

**Backend**:
```python
from django.contrib import messages

# View mein message add karo
messages.success(request, 'Registration successful!')
messages.error(request, 'Invalid OTP!')
messages.warning(request, 'OTP expiring soon!')
messages.info(request, 'Check your email.')
```

**Frontend** (Template):
```html
{% if messages %}
    {% for message in messages %}
        <div class="alert alert-{{ message.tags }}">
            {{ message }}
        </div>
    {% endfor %}
{% endif %}
```

**Working**:
1. Messages session ya cookie mein store hote hain
2. Ek baar display hone ke baad automatically delete ho jate hain
3. Redirect ke baad bhi work karte hain (persist across requests)

**Storage backends**:
- `session` (default) - Session mein store
- `cookie` - Cookie mein store
- `fallback` - Cookie try, phir session

---

**Q19: CSRF protection kya hai aur Django mein kaise implement hota hai?**  
**Ans**: **CSRF (Cross-Site Request Forgery)** ek attack hai jahan malicious website tumhare logged-in session ko use karke unauthorized actions perform karta hai.

**Example attack**:
```html
<!-- Malicious site -->
<form action="https://bank.com/transfer" method="POST">
    <input name="amount" value="10000">
    <input name="to" value="hacker">
</form>
<script>document.forms[0].submit();</script>
```
Agar tum bank.com pe logged in ho, ye form automatically submit hoga!

**Django's protection**:
1. **Backend** - Middleware check:
```python
# settings.py
MIDDLEWARE = [
    'django.middleware.csrf.CsrfViewMiddleware',  # CSRF protection
]
```

2. **Template** - Token add:
```html
<form method="POST">
    {% csrf_token %}  <!-- Secret token generate hota hai -->
    <input type="text" name="username">
    <button>Submit</button>
</form>
```

3. **Process**:
   - Django unique token generate karta hai
   - Token cookie + form hidden field mein add hota hai
   - POST request pe dono tokens match hone chahiye
   - Match nahi to 403 Forbidden error

**Exceptions**:
```python
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt  # CSRF check skip (APIs ke liye)
def api_view(request):
    pass
```

---

**Q20: Production deployment ke time kya environment variables set karne honge?**  
**Ans**: Security ke liye sensitive information environment variables mein store karo:

```python
# settings.py
import os

# Security
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
DEBUG = os.environ.get('DEBUG', 'False') == 'True'
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# Email configuration
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}
```

**.env file** (development):
```
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DB_NAME=student_tracking
DB_USER=postgres
DB_PASSWORD=password
```

**Production** (Render/Heroku):
- Environment variables dashboard mein set karo
- `.env` file commit mat karo (add to `.gitignore`)

---

## 🎓 Important Concepts to Remember

### 1. Authentication vs Authorization
- **Authentication**: Tum kaun ho? (Login, identity verification)
- **Authorization**: Tumhe kya karne ki permission hai? (Permissions, roles)

### 2. Password Hashing
- Plain text passwords KABHI store mat karo
- Django PBKDF2 algorithm use karta hai with SHA256
- Salt automatically add hota hai (every password ka unique hash)

### 3. Session Management
- Server-side storage for user data
- Session ID cookie mein store hoti hai
- Session expiry set karo security ke liye

### 4. OTP Best Practices
- Short expiration time (10-15 minutes)
- One-time use only
- Rate limiting (prevent brute force)
- Secure transmission (HTTPS, email encryption)

### 5. Database Relationships
- **OneToOne**: One user = One profile
- **ForeignKey**: One teacher = Many classes
- **ManyToMany**: Many teachers = Many subjects

---

## 📚 Additional Resources

1. **Django Official Docs**: https://docs.djangoproject.com/
2. **Django Authentication**: https://docs.djangoproject.com/en/4.2/topics/auth/
3. **Django Email**: https://docs.djangoproject.com/en/4.2/topics/email/
4. **Django Sessions**: https://docs.djangoproject.com/en/4.2/topics/http/sessions/

---

## ✅ Checklist Before Viva

- [ ] User model aur fields samajh liye
- [ ] Registration process step-by-step explain kar sakta hoon
- [ ] OTP generation aur verification logic samajh liya
- [ ] Session management ka concept clear hai
- [ ] Email sending process samajh liya
- [ ] Database relationships clear hain
- [ ] Security best practices pata hain
- [ ] Error handling samajh liya
- [ ] All test cases successfully run kar liye

---

**Good Luck! 🎉**

**Remember**: Confidence ke saath explain karo, code ki har line ka logic samjho, aur practical examples deke samjhao!

