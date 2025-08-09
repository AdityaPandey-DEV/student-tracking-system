# 🎓 Enhanced Smart Timetable Management System

A comprehensive Django-based web application for managing academic timetables, student enrollment, teacher assignments, and AI-powered analytics for educational institutions.

## 🚀 Features

### 👨‍💼 Admin Features
- **Dashboard Overview**: Complete administrative control panel
- **User Management**: Register and manage students, teachers, and admin accounts
- **Course Management**: Create and manage academic courses and subjects
- **Teacher Management**: Assign teachers to subjects and manage faculty
- **Student Management**: Enroll students, manage sections, and track attendance
- **Timetable Management**: Create, modify, and optimize class schedules
- **AI Analytics**: Smart insights and performance analytics
- **Announcements**: Broadcast important updates to targeted audiences

### 👩‍🎓 Student Features
- **Personal Dashboard**: Overview of classes, subjects, and announcements
- **Interactive Timetable**: Weekly schedule view with current class highlighting
- **Subject Management**: View enrolled subjects with attendance tracking
- **AI Chat Assistant**: 24/7 academic support and query resolution
- **Attendance Tracking**: Real-time attendance monitoring with progress bars
- **Study Resources**: Access to materials and assignments

### 👨‍🏫 Teacher Features
- **Teaching Dashboard**: Overview of assigned classes and schedules
- **Attendance Management**: Mark and track student attendance
- **Subject Management**: Manage assigned subjects and student enrollments
- **Resource Sharing**: Upload study materials and assignments
- **Student Performance**: View analytics and generate reports

### 🤖 AI-Powered Features
- **Smart Scheduling**: AI-optimized timetable generation
- **Performance Analytics**: Intelligent insights and trend analysis
- **Study Recommendations**: Personalized learning suggestions
- **Attendance Predictions**: Early warning systems for at-risk students
- **Resource Optimization**: Efficient room and teacher allocation

## 🛠️ Technology Stack

- **Backend**: Django 4.2.7 (Python)
- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript
- **Database**: SQLite (development) / MySQL (production)
- **AI Integration**: OpenAI API for intelligent features
- **Authentication**: Django's built-in user system with custom profiles
- **UI Framework**: Bootstrap 5 with custom styling
- **Icons**: Font Awesome
- **Forms**: Django Crispy Forms with Bootstrap5 template pack

## 📦 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)
- Git

### Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/AdityaPandey-DEV/Smart-Time-Table-Management-System.git
   cd Smart-Time-Table-Management-System
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   # Copy the example env file
   cp .env.example .env
   
   # Edit .env with your settings
   SECRET_KEY=your-secret-key-here
   DEBUG=True
   OPENAI_API_KEY=your-openai-api-key (optional)
   ```

5. **Run migrations**
   ```bash
   python manage.py migrate
   ```

6. **Create superuser** (optional)
   ```bash
   python manage.py createsuperuser
   ```

7. **Start the development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   - Open your browser and navigate to `http://127.0.0.1:8000`
   - Register as an admin to access full features

## 📁 Project Structure

```
enhanced_timetable_system/
├── accounts/              # User management and authentication
│   ├── models.py         # User, Student, Teacher, Admin profiles
│   ├── views.py          # Authentication views
│   ├── admin_views.py    # Admin dashboard and management
│   └── urls.py           # URL routing
├── timetable/            # Core timetable functionality
│   ├── models.py         # Course, Subject, TimetableEntry, etc.
│   ├── views.py          # Timetable management views
│   └── utils.py          # Helper functions
├── ai_features/          # AI-powered features
│   ├── models.py         # AI chat, analytics, recommendations
│   ├── views.py          # AI functionality views
│   └── services.py       # AI service integrations
├── templates/            # HTML templates
│   ├── admin/            # Admin interface templates
│   ├── student/          # Student interface templates
│   ├── teacher/          # Teacher interface templates
│   └── base.html         # Base template
├── static/               # Static files (CSS, JS, images)
├── media/                # User uploaded files
└── requirements.txt      # Python dependencies
```

## 🎯 Usage Guide

### Getting Started
1. **Admin Registration**: Start by registering an admin account
2. **Course Setup**: Create courses (B.Tech, BCA, etc.) and subjects
3. **Teacher Management**: Add teachers and assign them to subjects
4. **Student Enrollment**: Register students and enroll them in subjects
5. **Timetable Creation**: Generate or manually create timetables
6. **AI Features**: Enable AI analytics and chat features

### User Roles

**Admin Users:**
- Full system access
- User and content management
- Analytics and reporting
- System configuration

**Teacher Users:**
- Subject and class management
- Attendance marking
- Student performance tracking
- Resource sharing

**Student Users:**
- Personal timetable access
- Subject enrollment viewing
- AI chat assistance
- Attendance monitoring

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the root directory:

```env
SECRET_KEY=your-django-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (Optional - defaults to SQLite)
DB_NAME=timetable_db
DB_USER=root
DB_PASSWORD=
DB_HOST=localhost
DB_PORT=3306

# AI Features (Optional)
OPENAI_API_KEY=your-openai-api-key

# Email Configuration (Optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

### Database Configuration

**SQLite (Default - Development):**
- No additional setup required
- Database file created automatically

**MySQL (Production):**
```bash
pip install mysqlclient
```
Update settings.py to use MySQL configuration.

## 🔒 Security Features

- **CSRF Protection**: All forms protected against CSRF attacks
- **User Authentication**: Secure login/logout functionality
- **Permission System**: Role-based access control
- **Data Validation**: Comprehensive form and model validation
- **SQL Injection Protection**: Django ORM provides built-in protection

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```
3. **Make your changes**
4. **Write tests** (if applicable)
5. **Commit your changes**
   ```bash
   git commit -m "Add your feature description"
   ```
6. **Push to your branch**
   ```bash
   git push origin feature/your-feature-name
   ```
7. **Create a Pull Request**

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter any issues or have questions:

1. **Check the Issues**: Look for existing solutions
2. **Create an Issue**: Describe your problem clearly
3. **Contact**: Reach out to the maintainers

## 🎉 Acknowledgments

- **Django Community**: For the amazing web framework
- **Bootstrap Team**: For the responsive UI framework  
- **OpenAI**: For AI integration capabilities
- **Font Awesome**: For the beautiful icons
- **All Contributors**: Thanks for making this project better!

## 📊 Project Status

- ✅ **Core Features**: Complete
- ✅ **User Management**: Complete  
- ✅ **Timetable System**: Complete
- ✅ **AI Integration**: Complete
- ✅ **Responsive Design**: Complete
- 🚧 **Advanced Analytics**: In Development
- 🚧 **Mobile App**: Planned
- 🚧 **API Endpoints**: Planned

---

**Made with ❤️ by [Aditya Pandey](https://github.com/AdityaPandey-DEV)**

*For educational institutions looking to modernize their timetable management with AI-powered features.*
