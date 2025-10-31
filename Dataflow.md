# Data Flow Documentation
## Student Tracking System - Complete Data Flow Analysis

## Overview
This document describes the complete data flow through the Student Tracking System, from user registration to AI-powered analytics and reporting.

---

## 1. User Registration & Authentication Flow

### 1.1 Student Registration Flow

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │
       │ 1. POST /register/student/
       │    (Form Data: name, email, roll_number, course, year, section, password)
       ▼
┌─────────────────────────────────┐
│  Student Registration View      │
│  (accounts/views.py)            │
└──────┬──────────────────────────┘
       │
       │ 2. Validate Input Data
       │    - Check required fields
       │    - Validate email format
       │    - Validate roll_number uniqueness
       │    - Validate course, year, section
       │
       ▼
┌─────────────────────────────────┐
│  EmailOTP.generate_otp()        │
│  (accounts/models.py)           │
│  - Generate 6-digit OTP         │
│  - Store in EmailOTP table      │
│  - Set expiration (15 min)      │
│  - Invalidate previous OTPs     │
└──────┬──────────────────────────┘
       │
       │ 3. Send OTP Email
       │
       ▼
┌─────────────────────────────────┐
│  send_otp_notification()        │
│  (utils/notifications.py)       │
│  - Generate HTML email          │
│  - Send via SMTP/Console        │
└──────┬──────────────────────────┘
       │
       │ 4. Store Registration Data in Session
       │    (reg_data: encrypted session storage)
       │
       ▼
┌─────────────────────────────────┐
│  Display OTP Verification Form  │
│  (Step 2)                       │
└──────┬──────────────────────────┘
       │
       │ 5. POST /register/student/verify/
       │    (OTP Code)
       │
       ▼
┌─────────────────────────────────┐
│  EmailOTP.verify_otp()          │
│  - Check OTP code               │
│  - Verify expiration            │
│  - Mark as used                 │
└──────┬──────────────────────────┘
       │
       │ 6. Create User Account (Transaction)
       │
       ▼
┌─────────────────────────────────┐
│  Database Transaction           │
│  ├── User.objects.create_user() │
│  │   └── INSERT INTO User       │
│  │       (username, email,      │
│  │        password, user_type)  │
│  └── StudentProfile.objects.    │
│      create()                   │
│      └── INSERT INTO            │
│          StudentProfile         │
│          (user_id, roll_number, │
│           course, year, section)│
└──────┬──────────────────────────┘
       │
       │ 7. Clear Session Data
       │
       ▼
┌─────────────────────────────────┐
│  Redirect to Login Page         │
│  Success Message Displayed      │
└─────────────────────────────────┘
```

**Database Operations**:
- `INSERT INTO User` (username, email, password_hash, user_type='student')
- `INSERT INTO StudentProfile` (user_id, roll_number, course, year, section)
- `INSERT INTO EmailOTP` (email, otp_code, purpose='registration', expires_at)
- `UPDATE EmailOTP SET is_used=True` (after verification)

---

### 1.2 Teacher/Admin Registration Flow
Similar to student registration, but creates:
- `TeacherProfile` or `AdminProfile` instead of `StudentProfile`
- Links to `Teacher` entity for teachers

---

### 1.3 Login Flow

```
┌─────────────┐
│   Browser   │
└──────┬──────┘
       │
       │ 1. POST /login/
       │    (username, password)
       │
       ▼
┌─────────────────────────────────┐
│  Django Authentication          │
│  (accounts/views.py)            │
│  - authenticate()               │
│  - login()                      │
└──────┬──────────────────────────┘
       │
       │ 2. Create Session
       │    - Store user_id
       │    - Set session cookie
       │
       ▼
┌─────────────────────────────────┐
│  Role-Based Redirect            │
│  ├── student → /student/        │
│  ├── teacher → /teacher/        │
│  └── admin → /admin/            │
└─────────────────────────────────┘
```

**Database Operations**:
- `SELECT FROM User WHERE username=?` (authentication lookup)
- `SELECT FROM StudentProfile/TeacherProfile/AdminProfile WHERE user_id=?` (profile lookup)

---

## 2. Timetable Management Flow

### 2.1 Creating Timetable Entry

```
┌─────────────┐
│  Admin      │
│  Dashboard  │
└──────┬──────┘
       │
       │ 1. POST /admin/timetable/create/
       │    (subject, teacher, course, year, section,
       │     day, time_slot, room, academic_year, semester)
       │
       ▼
┌─────────────────────────────────┐
│  TimetableEntry Creation        │
│  (timetable/views.py)           │
│  - Validate inputs              │
│  - Check conflicts              │
└──────┬──────────────────────────┘
       │
       │ 2. Conflict Detection
       │
       ▼
┌─────────────────────────────────┐
│  Conflict Checks                │
│  ├── Room Conflict:             │
│  │   SELECT FROM TimetableEntry │
│  │   WHERE day_of_week=?        │
│  │   AND time_slot_id=?         │
│  │   AND room_id=?              │
│  │   AND academic_year=?        │
│  │   AND semester=?             │
│  ├── Teacher Conflict:          │
│  │   SELECT FROM TimetableEntry │
│  │   WHERE day_of_week=?        │
│  │   AND time_slot_id=?         │
│  │   AND teacher_id=?           │
│  └── Class Conflict:            │
│      SELECT FROM TimetableEntry │
│      WHERE day_of_week=?        │
│      AND time_slot_id=?         │
│      AND course=? AND year=?    │
│      AND section=?              │
└──────┬──────────────────────────┘
       │
       │ 3. If No Conflicts → Create Entry
       │
       ▼
┌─────────────────────────────────┐
│  INSERT INTO TimetableEntry     │
│  (subject_id, teacher_id,       │
│   course, year, section,        │
│   day_of_week, time_slot_id,    │
│   room_id, academic_year,       │
│   semester, is_active)          │
└──────┬──────────────────────────┘
       │
       │ 4. Return Success/Error
       │
       ▼
┌─────────────────────────────────┐
│  Update Timetable Grid Display  │
│  (AJAX Response)                │
└─────────────────────────────────┘
```

**Database Operations**:
- Multiple `SELECT` queries for conflict checking
- `INSERT INTO TimetableEntry` (if no conflicts)

---

### 2.2 Viewing Timetable

```
┌─────────────┐
│  Student/   │
│  Teacher    │
└──────┬──────┘
       │
       │ 1. GET /student/timetable/ or /teacher/timetable/
       │
       ▼
┌─────────────────────────────────┐
│  Timetable Query                │
│  (timetable/views.py)           │
│  - Get user profile             │
│  - Determine filters            │
└──────┬──────────────────────────┘
       │
       │ 2. For Students:
       │    SELECT FROM TimetableEntry
       │    WHERE course = student.course
       │    AND year = student.year
       │    AND section = student.section
       │    AND academic_year = current_year
       │    AND semester = current_semester
       │
       │ 3. For Teachers:
       │    SELECT FROM TimetableEntry
       │    WHERE teacher_id = teacher.id
       │    AND academic_year = current_year
       │    AND semester = current_semester
       │
       ▼
┌─────────────────────────────────┐
│  Join Related Data              │
│  ├── JOIN Subject               │
│  ├── JOIN Teacher               │
│  ├── JOIN Room                  │
│  └── JOIN TimeSlot              │
└──────┬──────────────────────────┘
       │
       │ 4. Organize by Day & Time
       │
       ▼
┌─────────────────────────────────┐
│  Render Timetable Template      │
│  (Grid Layout)                  │
└─────────────────────────────────┘
```

**Database Operations**:
- `SELECT FROM TimetableEntry` with JOINs to Subject, Teacher, Room, TimeSlot
- `SELECT FROM StudentProfile` (for student context)

---

## 3. Attendance Management Flow

### 3.1 Marking Attendance

```
┌─────────────┐
│  Teacher    │
│  Dashboard  │
└──────┬──────┘
       │
       │ 1. GET /teacher/mark-attendance/
       │    ?class_id=X&date=YYYY-MM-DD
       │
       ▼
┌─────────────────────────────────┐
│  Load Class Students            │
│  (timetable/views.py)           │
│  - Get TimetableEntry           │
│  - Get enrolled students        │
└──────┬──────────────────────────┘
       │
       │ 2. SELECT FROM StudentProfile
       │    WHERE course = entry.course
       │    AND year = entry.year
       │    AND section = entry.section
       │
       │ 3. SELECT FROM Enrollment
       │    WHERE student_id IN (...)
       │    AND subject_id = entry.subject_id
       │
       │ 4. SELECT FROM Attendance
       │    WHERE timetable_entry_id = entry.id
       │    AND date = selected_date
       │    (Load existing attendance)
       │
       ▼
┌─────────────────────────────────┐
│  Display Attendance Form        │
│  (Checkboxes: Present/Absent/   │
│   Late/Excused)                 │
└──────┬──────────────────────────┘
       │
       │ 5. POST /teacher/save-attendance/
       │    (student_id[], status[], notes[])
       │
       ▼
┌─────────────────────────────────┐
│  Save Attendance (Bulk)         │
│  (accounts/teacher_api_views.py)│
│  - Loop through students        │
│  - Upsert attendance records    │
└──────┬──────────────────────────┘
       │
       │ 6. For each student:
       │    INSERT INTO Attendance
       │    (student_id, timetable_entry_id,
       │     date, status, marked_by_id, notes)
       │    ON CONFLICT UPDATE
       │    (student_id, timetable_entry_id, date)
       │
       ▼
┌─────────────────────────────────┐
│  Return Success Response        │
│  (JSON)                         │
└─────────────────────────────────┘
```

**Database Operations**:
- `SELECT FROM StudentProfile` (get class students)
- `SELECT FROM Enrollment` (verify subject enrollment)
- `SELECT FROM Attendance` (load existing records)
- `INSERT INTO Attendance` or `UPDATE Attendance` (bulk upsert)

---

### 3.2 Viewing Attendance Reports

```
┌─────────────┐
│  Student/   │
│  Teacher    │
└──────┬──────┘
       │
       │ 1. GET /student/attendance/ or /teacher/attendance-reports/
       │    ?subject_id=X&start_date=...&end_date=...
       │
       ▼
┌─────────────────────────────────┐
│  Query Attendance Records       │
│  (accounts/views.py)            │
│  - Apply filters                │
│  - Calculate statistics         │
└──────┬──────────────────────────┘
       │
       │ 2. SELECT FROM Attendance
       │    WHERE student_id = ? (if student)
       │    AND timetable_entry_id IN (
       │        SELECT id FROM TimetableEntry
       │        WHERE subject_id = ?
       │    )
       │    AND date BETWEEN ? AND ?
       │
       │ 3. Calculate:
       │    - Total classes
       │    - Present count
       │    - Absent count
       │    - Attendance percentage
       │    - Trend analysis
       │
       ▼
┌─────────────────────────────────┐
│  Generate Attendance Report     │
│  (Table + Charts)               │
└─────────────────────────────────┘
```

**Database Operations**:
- `SELECT FROM Attendance` with JOINs
- `SELECT FROM TimetableEntry` (for filtering)
- Aggregate queries: `COUNT`, `GROUP BY`

---

## 4. AI Features Data Flow

### 4.1 AI Chat Flow

```
┌─────────────┐
│  Student    │
│  Chat UI    │
└──────┬──────┘
       │
       │ 1. POST /student/ai-chat/
       │    (message, session_id)
       │
       ▼
┌─────────────────────────────────┐
│  Create/Get Chat Session        │
│  (ai_features/views.py)         │
│  - Get or create AIChat         │
└──────┬──────────────────────────┘
       │
       │ 2. SELECT FROM AIChat
       │    WHERE session_id = ?
       │    OR INSERT INTO AIChat
       │    (user_id, session_id, chat_type)
       │
       │ 3. INSERT INTO ChatMessage
       │    (chat_id, sender='user', message)
       │
       ▼
┌─────────────────────────────────┐
│  AI Service Processing          │
│  (utils/ai_service.py)          │
│  - Get chat history             │
│  - Fetch student context        │
│  - Call AI API                  │
└──────┬──────────────────────────┘
       │
       │ 4. SELECT FROM ChatMessage
       │    WHERE chat_id = ?
       │    ORDER BY timestamp
       │
       │ 5. SELECT FROM StudentProfile
       │    WHERE user_id = ?
       │
       │ 6. SELECT FROM Enrollment, Attendance
       │    (for context)
       │
       │ 7. Call OpenAI/Groq API
       │    (with context)
       │
       ▼
┌─────────────────────────────────┐
│  Save AI Response               │
│  - INSERT INTO ChatMessage      │
│    (chat_id, sender='ai',       │
│     message, context_data)      │
└──────┬──────────────────────────┘
       │
       │ 8. Return Response to UI
       │
       ▼
┌─────────────────────────────────┐
│  Display Chat Message           │
│  (Real-time update)             │
└─────────────────────────────────┘
```

**Database Operations**:
- `SELECT/INSERT INTO AIChat`
- `INSERT INTO ChatMessage` (user message)
- Multiple `SELECT` queries for context gathering
- `INSERT INTO ChatMessage` (AI response)

---

### 4.2 Study Recommendation Generation

```
┌─────────────┐
│  AI         │
│  Background │
│  Process    │
└──────┬──────┘
       │
       │ 1. Trigger: Daily/Scheduled
       │
       ▼
┌─────────────────────────────────┐
│  Analyze Student Data           │
│  (ai_features/views.py)         │
│  - Get attendance records       │
│  - Get enrollment data          │
│  - Calculate performance        │
└──────┬──────────────────────────┘
       │
       │ 2. SELECT FROM Attendance
       │    WHERE student_id = ?
       │    AND date > (current_date - 30 days)
       │
       │ 3. SELECT FROM Enrollment
       │    WHERE student_id = ?
       │
       │ 4. SELECT FROM TimetableEntry
       │    (for class schedule)
       │
       │ 5. Calculate:
       │    - Attendance percentage
       │    - Weak subjects
       │    - Study patterns
       │
       ▼
┌─────────────────────────────────┐
│  AI Analysis                    │
│  (utils/ai_service.py)          │
│  - Send data to AI              │
│  - Get recommendations          │
└──────┬──────────────────────────┘
       │
       │ 6. Call AI API with analysis data
       │
       ▼
┌─────────────────────────────────┐
│  Generate Recommendations       │
│  - INSERT INTO StudyRecommendation
│    (student_id, type, title,    │
│     description, priority,      │
│     confidence_score,           │
│     generated_data)             │
│  - Link to subjects (ManyToMany)│
└──────┬──────────────────────────┘
       │
       │ 7. Create Notification
       │
       ▼
┌─────────────────────────────────┐
│  INSERT INTO SmartNotification  │
│  (recipient_id, type, title,    │
│   message, priority)            │
└─────────────────────────────────┘
```

**Database Operations**:
- Multiple `SELECT` queries for data analysis
- `INSERT INTO StudyRecommendation`
- `INSERT INTO SmartNotification`

---

### 4.3 Timetable Optimization Flow

```
┌─────────────┐
│  Admin      │
│  Dashboard  │
└──────┬──────┘
       │
       │ 1. POST /admin/generate-timetable/
       │    (course, year, section, constraints)
       │
       ▼
┌─────────────────────────────────┐
│  Algorithm Selection            │
│  (ai_features/views.py)         │
│  - Constraint Satisfaction      │
│  - Genetic Algorithm            │
│  - Greedy Algorithm             │
└──────┬──────────────────────────┘
       │
       │ 2. Load Configuration
       │    SELECT FROM TimetableConfiguration
       │
       │ 3. Load Constraints
       │    SELECT FROM Subject, Teacher,
       │           TeacherSubject, Room, TimeSlot
       │
       │ 4. Run Algorithm
       │    (utils/algorithmic_timetable.py)
       │    - Generate timetable
       │    - Check conflicts
       │    - Optimize score
       │
       ▼
┌─────────────────────────────────┐
│  Save Suggestion                │
│  - INSERT INTO                  │
│    AlgorithmicTimetableSuggestion
│    (generated_by_id, course,    │
│     year, section,              │
│     algorithm_type,             │
│     suggestion_data,            │
│     optimization_score,         │
│     conflicts_resolved,         │
│     status='generated')         │
└──────┬──────────────────────────┘
       │
       │ 5. Display Suggestion
       │
       ▼
┌─────────────────────────────────┐
│  Admin Review                   │
│  - View timetable grid          │
│  - Approve/Reject               │
└──────┬──────────────────────────┘
       │
       │ 6. If Approved:
       │    UPDATE AlgorithmicTimetableSuggestion
       │    SET status='approved',
       │        reviewed_by_id=?
       │
       │ 7. Apply to Timetable:
       │    INSERT INTO TimetableEntry
       │    (for each entry in suggestion_data)
       │
       ▼
┌─────────────────────────────────┐
│  UPDATE status='implemented'    │
└─────────────────────────────────┘
```

**Database Operations**:
- `SELECT FROM TimetableConfiguration`
- Multiple `SELECT` queries for constraints
- `INSERT INTO AlgorithmicTimetableSuggestion`
- `UPDATE AlgorithmicTimetableSuggestion` (approval)
- Bulk `INSERT INTO TimetableEntry` (implementation)

---

## 5. Enrollment Flow

```
┌─────────────┐
│  Admin/     │
│  Student    │
└──────┬──────┘
       │
       │ 1. POST /enroll/
       │    (student_id, subject_id, academic_year, semester)
       │
       ▼
┌─────────────────────────────────┐
│  Validate Enrollment            │
│  - Check student eligibility    │
│  - Check subject availability   │
│  - Check prerequisites          │
└──────┬──────────────────────────┘
       │
       │ 2. SELECT FROM StudentProfile
       │    WHERE user_id = ?
       │
       │ 3. SELECT FROM Subject
       │    WHERE id = ?
       │    AND course = student.course
       │    AND year = student.year
       │
       │ 4. SELECT FROM Enrollment
       │    WHERE student_id = ?
       │    AND subject_id = ?
       │    AND academic_year = ?
       │    AND semester = ?
       │    (Check for duplicates)
       │
       ▼
┌─────────────────────────────────┐
│  Create Enrollment              │
│  INSERT INTO Enrollment         │
│  (student_id, subject_id,       │
│   academic_year, semester,      │
│   enrolled_at, is_active)       │
└─────────────────────────────────┘
```

**Database Operations**:
- `SELECT FROM StudentProfile`
- `SELECT FROM Subject`
- `SELECT FROM Enrollment` (duplicate check)
- `INSERT INTO Enrollment`

---

## 6. Announcement Flow

```
┌─────────────┐
│  Admin      │
│  Dashboard  │
└──────┬──────┘
       │
       │ 1. POST /admin/announcement/create/
       │    (title, content, target_audience,
       │     target_course, target_year, target_section)
       │
       ▼
┌─────────────────────────────────┐
│  Create Announcement            │
│  INSERT INTO Announcement       │
│  (title, content, posted_by_id, │
│   target_audience,              │
│   target_course, target_year,   │
│   target_section, is_urgent)    │
└──────┬──────────────────────────┘
       │
       │ 2. Display on Dashboard
       │
       ▼
┌─────────────────────────────────┐
│  For Students/Teachers:         │
│  GET /dashboard/                │
│  - Query relevant announcements │
└──────┬──────────────────────────┘
       │
       │ 3. SELECT FROM Announcement
       │    WHERE is_active = True
       │    AND (
       │        target_audience = 'all'
       │        OR (target_course = student.course
       │            AND target_year = student.year
       │            AND target_section = student.section)
       │    )
       │    ORDER BY is_urgent DESC, created_at DESC
       │
       ▼
┌─────────────────────────────────┐
│  Display Announcements          │
│  (Dashboard Feed)               │
└─────────────────────────────────┘
```

**Database Operations**:
- `INSERT INTO Announcement`
- `SELECT FROM Announcement` (filtered by audience)

---

## 7. Data Flow Summary

### Read Operations (SELECT):
1. **User Authentication**: User, Profile lookups
2. **Timetable Viewing**: TimetableEntry with JOINs
3. **Attendance Queries**: Attendance with filters
4. **AI Context**: Student, Enrollment, Attendance data
5. **Analytics**: Aggregate queries on Attendance, Enrollment

### Write Operations (INSERT/UPDATE):
1. **Registration**: User, Profile creation
2. **Timetable Creation**: TimetableEntry insertion
3. **Attendance Marking**: Attendance bulk upsert
4. **Enrollment**: Enrollment insertion
5. **AI Features**: AIChat, ChatMessage, Recommendations
6. **Announcements**: Announcement creation

### Transaction Patterns:
1. **Registration**: Single transaction (User + Profile)
2. **Attendance**: Bulk transaction (multiple Attendance records)
3. **Timetable Creation**: Single transaction with conflict checks

### Caching Opportunities:
1. **Timetable Data**: Cache by (course, year, section, semester)
2. **Student Profiles**: Cache by user_id
3. **Announcements**: Cache active announcements
4. **AI Chat History**: Cache recent messages

---

## 8. Data Integrity Checks

### Before INSERT:
1. **Uniqueness Checks**: Roll numbers, email addresses
2. **Foreign Key Validation**: All FK references must exist
3. **Conflict Detection**: TimetableEntry conflicts
4. **Constraint Validation**: Year, semester ranges

### After INSERT:
1. **Audit Logging**: Timestamp tracking
2. **Notification Triggers**: Smart notifications
3. **Cache Invalidation**: Clear relevant caches

---

## 9. Error Handling Flow

```
┌─────────────────────────────────┐
│  Operation Attempt              │
└──────┬──────────────────────────┘
       │
       │ Try Operation
       │
       ▼
┌─────────────────────────────────┐
│  Exception Occurs?              │
│  ├── IntegrityError             │
│  ├── ValidationError            │
│  ├── DoesNotExist               │
│  └── DatabaseError              │
└──────┬──────────────────────────┘
       │
       │ Yes → Catch Exception
       │
       ▼
┌─────────────────────────────────┐
│  Rollback Transaction           │
│  - If in transaction            │
│  - Restore previous state       │
└──────┬──────────────────────────┘
       │
       │ Log Error
       │
       ▼
┌─────────────────────────────────┐
│  Return Error Response          │
│  - User-friendly message        │
│  - Error code                   │
│  - Suggested actions            │
└─────────────────────────────────┘
```

---

## 10. Performance Considerations

### Query Optimization:
1. **Use SELECT_related()** for ForeignKey joins
2. **Use PREFETCH_related()** for ManyToMany/Reverse FK
3. **Index frequently queried fields**
4. **Limit query result sets** with pagination

### Database Indexes:
- Primary keys (automatic)
- Foreign keys (automatic)
- User.email, User.user_type
- TimetableEntry(day_of_week, time_slot_id)
- Attendance(student_id, date)
- EmailOTP(email, is_used, expires_at)

### Bulk Operations:
- Attendance marking (bulk upsert)
- TimetableEntry creation (bulk insert)
- Notification creation (bulk insert)

---

**Generated**: 2025-01-31  
**System**: Student Tracking System  
**Database**: SQLite3/PostgreSQL  
**ORM**: Django 4.2

