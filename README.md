# Student Tracking System

**AI-powered student management platform — smart timetable generation, attendance analytics, and role-based dashboards.**

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat-square&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-4.2+-092E20?style=flat-square&logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=flat-square&logo=postgresql&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-412991?style=flat-square&logo=openai&logoColor=white)

---

## What It Does

A comprehensive platform for educational institutions to manage students, teachers, and resources using AI.

**Key Features:**
- **Smart Timetables** — AI-assisted generation with automated conflict resolution
- **Role-based Panels** — dedicated views for students, teachers, and admins
- **AI Chatbot** — interactive assistant (OpenAI + offline fallback)
- **Analytics** — performance prediction and attendance trends
- **Auth** — free email OTP verification via Gmail SMTP

## Architecture

```
Student/Teacher/Admin Views (Django Templates) ↔ Django Views & URLs
                                                      ├── Timetable Engine
                                                      ├── OpenAI Chatbot
                                                      ├── Gmail SMTP (Auth)
                                                      └── PostgreSQL DB
```

## Tech Stack

| Component | Technology |
|---|---|
| Backend | Django 4.2+ (Python) |
| Database | PostgreSQL |
| AI | OpenAI GPT |
| Auth | Email OTP |

## My Role

I designed the role-based access system, planned the timetable generation algorithm with constraint satisfaction, and architected the email OTP flow. Code generation was accelerated using AI tools; timetable conflict resolution and PostgreSQL migration on Render are mine.

## Quick Start

```bash
git clone https://github.com/AdityaPandey-DEV/student-tracking-system.git && cd student-tracking-system
pip install -r requirements.txt
# Configure .env (Django Secret, DB URL, Email Credentials)
python manage.py migrate && python manage.py runserver
```

---

<div align="center">

*Architected & built by [Aditya Pandey](https://github.com/AdityaPandey-DEV) — AI-augmented development*

</div>
