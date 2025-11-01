# 🎓 Student Tracking System

**AI-powered student tracking and management platform for educational institutions.**

[![Deploy on Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/)
[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![Django](https://img.shields.io/badge/django-4.2+-green.svg)](https://djangoproject.com)

## 🚀 Live Demo

- **Production**: https://smart-time-table-management-system-1.onrender.com
- **Admin Login**: admin/admin123 (demo)

## ✨ Features

### 🎯 For Students
- **AI-powered personalized dashboard**
- **Smart study recommendations** 
- **Interactive AI chatbot assistant**
- **Real-time timetable updates**
- **Email OTP registration** (FREE!)
- **Attendance tracking**

### 👨‍🏫 For Teachers  
- **Class management dashboard**
- **Attendance marking system**
- **Student progress tracking**
- **Announcement system**
- **Material management**

### 🛡️ For Administrators
- **Comprehensive course management**
- **AI-assisted timetable generation** 
- **Teacher and student management**
- **Advanced analytics dashboard**
- **Automated conflict resolution**
- **Performance insights**

### 🤖 AI-Powered Intelligence
- **Automatic timetable optimization**
- **Performance prediction analytics**
- **Smart notification system**
- **Attendance trend analysis**
- **Resource optimization suggestions**

## 🛠️ Technology Stack

- **Backend**: Django 4.2+ (Python)
- **Frontend**: Bootstrap 5, JavaScript
- **Database**: PostgreSQL (Production), SQLite (Development)
- **Email**: Gmail SMTP (FREE OTP verification)
- **AI**: OpenAI GPT, Offline fallback
- **Deployment**: Render.com
- **Authentication**: Email OTP verification

## 📧 Email OTP System (FREE!)

✅ **100% FREE** email verification (no SMS costs)  
✅ **Professional HTML email templates**  
✅ **6-digit OTP codes** with 10-minute expiration  
✅ **All user types** (Student, Teacher, Admin)  
✅ **Phone numbers optional**  
✅ **Gmail SMTP integration**  

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/AdityaPandey-DEV/Smart-Time-Table-Management-System.git
cd student-tracking-system
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Environment Setup
Create `.env` file:
```env
DEBUG=True
SECRET_KEY=your-secret-key-here

# Email Configuration (Gmail SMTP)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-16-character-app-password

# Database
DATABASE_URL=sqlite:///db.sqlite3
```

### 4. Database Setup
```bash
python manage.py migrate
python manage.py collectstatic
```

### 5. Create Superuser (Optional)
```bash
python manage.py createsuperuser
```

### 6. Run Development Server
```bash
python manage.py runserver
```

Visit: http://127.0.0.1:8000

## 📧 Gmail SMTP Setup (5 minutes)

### Step 1: Enable 2-Factor Authentication
1. Go to: https://myaccount.google.com/security
2. Enable "2-Step Verification"
3. Complete phone verification

### Step 2: Generate App Password  
1. Go to: https://myaccount.google.com/apppasswords
2. Select "Mail" → "Other (Custom name)"
3. Enter: "Student Tracking System"
4. Copy the 16-character password (e.g., `abcdefghijklmnop`)

### Step 3: Update .env File
```env
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=abcdefghijklmnop
```

### Step 4: Test Email
```bash
python test_email.py
```

## 🚀 Production Deployment (Render)

### ⚠️ Important: Email Setup for Render Free Tier

**Gmail SMTP is blocked on Render free tier!** Use **SendGrid** instead (100 emails/day free).

**Quick Setup:**
1. Create account: https://signup.sendgrid.com/
2. Generate API key: https://app.sendgrid.com/settings/api_keys
3. Verify sender email
4. Add environment variables (see below)

📖 **Full guide:** See [docs/RENDER_EMAIL_SETUP.md](docs/RENDER_EMAIL_SETUP.md)

### Environment Variables Required:
```env
# Basic Settings
DEBUG=False
SECRET_KEY=your-production-secret-key
ALLOWED_HOSTS=your-domain.onrender.com,*.onrender.com

# Email Configuration (SendGrid - Recommended for Render)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_PROVIDER=sendgrid
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
SENDGRID_API_KEY=SG.your-sendgrid-api-key-here
DEFAULT_FROM_EMAIL=your-verified-email@example.com

# Alternative: Gmail SMTP (works locally, blocked on Render free tier)
# EMAIL_HOST=smtp.gmail.com
# EMAIL_HOST_USER=your-email@gmail.com
# EMAIL_HOST_PASSWORD=your-gmail-app-password

# Security
CSRF_TRUSTED_ORIGINS=https://your-domain.onrender.com

# Database (PostgreSQL)
DATABASE_URL=postgresql://user:password@host:port/database
```

### Critical Production Settings:
- ⚠️ **EMAIL_HOST_PASSWORD**: Must have **NO SPACES**
- ⚠️ **DEBUG**: Must be `False` in production
- ⚠️ **CSRF_TRUSTED_ORIGINS**: Required for form submissions

## 🎯 User Registration Process

### Students
1. Go to `/register/student/`
2. Fill personal information
3. **Email required**, phone optional
4. Receive OTP via email (FREE!)
5. Enter 6-digit code to verify
6. Account created successfully

### Teachers  
1. Go to `/register/teacher/`
2. Fill professional details
3. Email OTP verification
4. Account approved by admin

### Administrators
1. Go to `/register/admin/`
2. Fill administrative information  
3. Email OTP verification
4. Full system access

## 🔧 Development Tools

### Test Email Configuration
```bash
python test_email.py
```

### Run System Health Check
```bash
python system_health_check.py
```

### Setup Demo Environment
```bash
python setup_demo.py
```

### Debug Production Issues
```bash
python debug_production.py
```

## 🏗️ Project Structure

```
enhanced_timetable_system/
├── accounts/              # User management & authentication
├── timetable/            # Core timetable functionality  
├── ai_features/          # AI-powered features
├── utils/                # Utilities (email, AI services)
├── templates/            # HTML templates
├── static/               # CSS, JS, images
├── enhanced_timetable_system/  # Django settings
└── requirements.txt      # Python dependencies
```

## 🤖 AI Features

### Timetable Optimization
- **Conflict detection** and resolution
- **Resource optimization**
- **Schedule balancing**
- **Automated suggestions**

### Performance Analytics
- **Student performance prediction**
- **Attendance pattern analysis**
- **Grade trend forecasting**
- **Personalized recommendations**

### Intelligent Notifications
- **Smart reminder system**
- **Proactive conflict alerts**
- **Performance insights**
- **Custom notification preferences**

## 🔒 Security Features

### Authentication
- **Email OTP verification**
- **Role-based access control**
- **Session management**
- **CSRF protection**

### Data Protection
- **Input validation**
- **SQL injection prevention**
- **XSS protection**
- **Secure password hashing**

## 🐛 Troubleshooting

### Registration Issues

**Problem**: "An error occurred. Please try again"
- **Solution**: Check Render logs for specific error
- **Common fix**: Verify EMAIL_HOST_PASSWORD has no spaces

**Problem**: Form stuck at Stage 1
- **Solution**: Check CSRF_TRUSTED_ORIGINS in production
- **Alternative**: Try incognito mode, different browser

**Problem**: No OTP email received
- **Solution**: Check spam folder, verify Gmail App Password
- **Test**: Run `python test_email.py` locally

### Email Configuration Issues

**Problem**: `535 Username and Password not accepted`
- **Solution**: Regenerate Gmail App Password
- **Check**: 2-Factor Authentication enabled
- **Verify**: 16-character password, no spaces

**Problem**: `Connection refused` or timeout
- **Solution**: Check internet connection, firewall
- **Alternative**: Try different SMTP settings

### Production Deployment Issues

**Problem**: 500 Internal Server Error
- **Solution**: Check DEBUG=False, proper SECRET_KEY
- **Verify**: All environment variables set correctly

**Problem**: CSRF verification failed  
- **Solution**: Add CSRF_TRUSTED_ORIGINS environment variable
- **Format**: `https://your-domain.onrender.com`

## 🧪 Testing

### Run Tests
```bash
python manage.py test
```

### Email System Test
```bash
python test_email.py
```

### Complete System Test
```bash
python system_health_check.py
```

## 📊 System Status

### ✅ Working Features
- User registration (all types) with email OTP
- Gmail SMTP email sending  
- Professional HTML email templates
- AI-powered timetable generation
- Comprehensive admin dashboard
- Student/Teacher portals
- Attendance management
- Course management system

### 🔧 Configuration Verified
- Email OTP system (FREE verification)
- Phone numbers optional across all user types
- Professional error handling
- Production-ready security settings
- Offline AI fallback system

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Support

- **GitHub Issues**: https://github.com/AdityaPandey-DEV/Smart-Time-Table-Management-System/issues
- **Email**: adityapandey.dev.in@gmail.com
- **Live Demo**: https://smart-time-table-management-system-1.onrender.com

## 🎉 Acknowledgments

- Django framework and community
- Bootstrap for responsive UI
- OpenAI for AI capabilities  
- Gmail SMTP for free email service
- Render.com for hosting platform

---

## 🚀 Ready to Transform Your Academic Experience?

**Join thousands of students and educators using our AI-powered platform!**

[**🌟 Get Started Today**](https://smart-time-table-management-system-1.onrender.com) | [**📚 Learn More**](https://github.com/AdityaPandey-DEV/Smart-Time-Table-Management-System)

---

*Student Tracking System - Making education management easier! 🎓*
