# Entity-Relationship Diagram (ERD)
## Student Tracking System Database Schema

## Database Overview
- **Current Database**: SQLite3 (Development) / PostgreSQL (Production)
- **Total Entities**: 25
- **Relationship Types**: OneToOne, OneToMany, ManyToMany

---

## Entity Descriptions

### 1. USER (Core Authentication Entity)
**Primary Key**: `id` (inherited from AbstractUser)  
**Description**: Central user authentication entity extending Django's AbstractUser

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| id | Integer | PK, Auto | Unique identifier |
| username | String(150) | UNIQUE, NOT NULL | Login username |
| email | String(254) | UNIQUE, NOT NULL | Email address |
| password | String | NOT NULL, Hashed | Encrypted password |
| first_name | String(150) | | User's first name |
| last_name | String(150) | | User's last name |
| user_type | Char(10) | NOT NULL, CHECK | 'student', 'teacher', 'admin' |
| phone_number | String(15) | NULL | Optional phone number |
| is_verified | Boolean | DEFAULT=True | Email verification status |
| is_staff | Boolean | DEFAULT=False | Staff access flag |
| is_superuser | Boolean | DEFAULT=False | Superuser flag |
| created_at | DateTime | AUTO | Account creation timestamp |
| updated_at | DateTime | AUTO | Last update timestamp |

**Relationships**:
- 1:1 → StudentProfile (via user field)
- 1:1 → AdminProfile (via user field)
- 1:1 → TeacherProfile (via user field)
- 1:N → AIChat (creator)
- 1:N → Announcement (posted_by)
- 1:N → Attendance (marked_by)
- 1:N → EmailOTP (associated emails)
- 1:N → AlgorithmicTimetableSuggestion (generated_by, reviewed_by)
- 1:N → TimetableConfiguration (created_by)
- 1:N → AIAnalyticsReport (generated_by)
- 1:N → SmartNotification (recipient)

---

### 2. STUDENT_PROFILE
**Primary Key**: `user_id` (Foreign Key to User)  
**Description**: Extended profile information for students

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| user_id | Integer | PK, FK→User | One-to-one with User |
| roll_number | String(20) | UNIQUE, NOT NULL | Unique roll number |
| course | Char(50) | NOT NULL, CHECK | 'B.Tech', 'BCA', 'B.Sc', 'MCA', 'M.Tech', 'MBA' |
| year | Integer | NOT NULL, CHECK | 1-4 (First to Fourth Year) |
| section | String(5) | NOT NULL | Section identifier (A, B, C, etc.) |

**Unique Constraint**: `(course, year, section, roll_number)`

**Relationships**:
- N:1 → User (user_id)
- 1:N → Enrollment (student)
- 1:N → Attendance (student)
- 1:N → StudyRecommendation (student)
- 1:N → PerformanceInsight (student)

---

### 3. TEACHER_PROFILE
**Primary Key**: `user_id` (Foreign Key to User)  
**Description**: Extended profile information for teachers

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| user_id | Integer | PK, FK→User | One-to-one with User |
| teacher_id | Integer | FK→Teacher, NULL | Link to Teacher entity |
| employee_id | String(20) | UNIQUE, NULL | Employee identification |
| department | String(100) | | Department name |
| designation | String(100) | NULL | Job title/position |
| specialization | Text | | Area of expertise |
| is_active | Boolean | DEFAULT=True | Active status flag |

**Relationships**:
- N:1 → User (user_id)
- 1:1 → Teacher (teacher_id)
- 1:N → StudyMaterial (uploaded_by, via User)

---

### 4. ADMIN_PROFILE
**Primary Key**: `user_id` (Foreign Key to User)  
**Description**: Extended profile information for administrators

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| user_id | Integer | PK, FK→User | One-to-one with User |
| admin_id | String(20) | UNIQUE, NOT NULL | Admin identification |
| department | String(100) | NOT NULL | Department name |
| designation | String(100) | NULL | Job title/position |

**Relationships**:
- N:1 → User (user_id)

---

### 5. COURSE
**Primary Key**: `id`  
**Description**: Academic programs offered by the institution

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| id | Integer | PK, Auto | Unique identifier |
| name | String(100) | UNIQUE, NOT NULL | Course code (e.g., 'B.Tech') |
| full_name | String(200) | NOT NULL | Full course name |
| duration_years | Integer | DEFAULT=4, CHECK(1-6) | Course duration |
| description | Text | | Course description |
| is_active | Boolean | DEFAULT=True | Active status |
| created_at | DateTime | AUTO | Creation timestamp |
| updated_at | DateTime | AUTO | Update timestamp |

**Relationships**:
- 1:N → Subject (course)

---

### 6. SUBJECT
**Primary Key**: `id`  
**Description**: Academic subjects within courses

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| id | Integer | PK, Auto | Unique identifier |
| code | String(10) | UNIQUE, NOT NULL | Subject code (e.g., 'CS101') |
| name | String(100) | NOT NULL | Subject name |
| course_id | Integer | FK→Course, NOT NULL | Belongs to Course |
| year | Integer | NOT NULL, CHECK(1-4) | Year of study |
| semester | Integer | NOT NULL, CHECK(1-8) | Semester number |
| credits | Integer | DEFAULT=3, CHECK(1-6) | Credit hours |
| description | Text | | Subject description |
| is_active | Boolean | DEFAULT=True | Active status |
| created_at | DateTime | AUTO | Creation timestamp |
| updated_at | DateTime | AUTO | Update timestamp |

**Unique Constraint**: `(code, course_id)`

**Relationships**:
- N:1 → Course (course_id)
- N:M → Teacher (through TeacherSubject)
- 1:N → TimetableEntry (subject)
- 1:N → Enrollment (subject)
- 1:N → StudyMaterial (subject)
- 1:N → Assignment (subject)
- N:M → StudyRecommendation (subjects)

---

### 7. TEACHER
**Primary Key**: `id`  
**Description**: Faculty member information

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| id | Integer | PK, Auto | Unique identifier |
| employee_id | String(20) | UNIQUE, NOT NULL | Employee ID |
| name | String(100) | NOT NULL | Teacher's full name |
| email | String(254) | UNIQUE, NOT NULL | Email address |
| phone_number | String(15) | NULL | Phone number |
| department | String(100) | NOT NULL | Department |
| designation | String(100) | | Job title |
| specialization | String(200) | | Areas of expertise |
| is_active | Boolean | DEFAULT=True | Active status |
| created_at | DateTime | AUTO | Creation timestamp |
| updated_at | DateTime | AUTO | Update timestamp |

**Relationships**:
- 1:1 → TeacherProfile (via employee_id)
- N:M → Subject (through TeacherSubject)
- 1:N → TimetableEntry (teacher)

---

### 8. TEACHER_SUBJECT (Junction Table)
**Primary Key**: `id`  
**Description**: Many-to-many relationship between Teachers and Subjects

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| id | Integer | PK, Auto | Unique identifier |
| teacher_id | Integer | FK→Teacher, NOT NULL | Teacher reference |
| subject_id | Integer | FK→Subject, NOT NULL | Subject reference |
| assigned_at | DateTime | AUTO | Assignment timestamp |
| is_active | Boolean | DEFAULT=True | Active status |

**Unique Constraint**: `(teacher_id, subject_id)`

**Relationships**:
- N:1 → Teacher (teacher_id)
- N:1 → Subject (subject_id)

---

### 9. TIME_SLOT
**Primary Key**: `id`  
**Description**: Time periods for class scheduling

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| id | Integer | PK, Auto | Unique identifier |
| period_number | Integer | NOT NULL, UNIQUE, CHECK(1-10) | Period sequence |
| start_time | Time | NOT NULL | Period start time |
| end_time | Time | NOT NULL | Period end time |
| is_break | Boolean | DEFAULT=False | Break period flag |
| break_duration | Integer | DEFAULT=0 | Break duration (minutes) |
| is_active | Boolean | DEFAULT=True | Active status |

**Relationships**:
- 1:N → TimetableEntry (time_slot)

---

### 10. ROOM
**Primary Key**: `id`  
**Description**: Physical locations (classrooms, labs, etc.)

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| id | Integer | PK, Auto | Unique identifier |
| room_number | String(20) | UNIQUE, NOT NULL | Room identifier |
| room_name | String(100) | | Room name/description |
| room_type | Char(20) | NOT NULL, CHECK | 'classroom', 'lab', 'auditorium', 'seminar' |
| capacity | Integer | NOT NULL, CHECK(>0) | Maximum capacity |
| floor | String(10) | | Floor number |
| building | String(50) | | Building name |
| facilities | Text | | Available facilities |
| is_active | Boolean | DEFAULT=True | Active status |

**Relationships**:
- 1:N → TimetableEntry (room)

---

### 11. TIMETABLE_ENTRY
**Primary Key**: `id`  
**Description**: Individual class schedule entries

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| id | Integer | PK, Auto | Unique identifier |
| subject_id | Integer | FK→Subject, NOT NULL | Subject reference |
| teacher_id | Integer | FK→Teacher, NOT NULL | Teacher reference |
| course | String(50) | NOT NULL | Course name (denormalized) |
| year | Integer | NOT NULL, CHECK(1-4) | Year of study |
| section | String(5) | NOT NULL | Section identifier |
| day_of_week | Integer | NOT NULL, CHECK(0-5) | 0=Monday, 5=Saturday |
| time_slot_id | Integer | FK→TimeSlot, NOT NULL | Time period |
| room_id | Integer | FK→Room, NOT NULL | Room assignment |
| academic_year | String(10) | NOT NULL | Academic year (e.g., '2023-24') |
| semester | Integer | NOT NULL, CHECK(1-8) | Semester number |
| is_active | Boolean | DEFAULT=True | Active status |
| created_at | DateTime | AUTO | Creation timestamp |
| updated_at | DateTime | AUTO | Update timestamp |

**Unique Constraints**:
- `(day_of_week, time_slot_id, room_id, academic_year, semester)` - No room conflicts
- `(day_of_week, time_slot_id, teacher_id, academic_year, semester)` - No teacher conflicts
- `(day_of_week, time_slot_id, course, year, section, academic_year, semester)` - No class conflicts

**Relationships**:
- N:1 → Subject (subject_id)
- N:1 → Teacher (teacher_id)
- N:1 → TimeSlot (time_slot_id)
- N:1 → Room (room_id)
- 1:N → Attendance (timetable_entry)

---

### 12. ENROLLMENT
**Primary Key**: `id`  
**Description**: Student enrollment in subjects

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| id | Integer | PK, Auto | Unique identifier |
| student_id | Integer | FK→StudentProfile, NOT NULL | Student reference |
| subject_id | Integer | FK→Subject, NOT NULL | Subject reference |
| academic_year | String(10) | NOT NULL | Academic year |
| semester | Integer | NOT NULL, CHECK(1-8) | Semester number |
| enrolled_at | DateTime | AUTO | Enrollment timestamp |
| is_active | Boolean | DEFAULT=True | Active status |

**Unique Constraint**: `(student_id, subject_id, academic_year, semester)`

**Relationships**:
- N:1 → StudentProfile (student_id)
- N:1 → Subject (subject_id)

---

### 13. ATTENDANCE
**Primary Key**: `id`  
**Description**: Student attendance records

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| id | Integer | PK, Auto | Unique identifier |
| student_id | Integer | FK→StudentProfile, NOT NULL | Student reference |
| timetable_entry_id | Integer | FK→TimetableEntry, NOT NULL | Class reference |
| date | Date | NOT NULL | Attendance date |
| status | Char(10) | NOT NULL, CHECK | 'present', 'absent', 'late', 'excused' |
| marked_at | DateTime | AUTO | Marking timestamp |
| marked_by_id | Integer | FK→User, NULL | Who marked attendance |
| notes | Text | | Additional notes |

**Unique Constraint**: `(student_id, timetable_entry_id, date)`

**Relationships**:
- N:1 → StudentProfile (student_id)
- N:1 → TimetableEntry (timetable_entry_id)
- N:1 → User (marked_by_id)

---

### 14. ANNOUNCEMENT
**Primary Key**: `id`  
**Description**: Announcements posted by admins

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| id | Integer | PK, Auto | Unique identifier |
| title | String(200) | NOT NULL | Announcement title |
| content | Text | NOT NULL | Announcement content |
| posted_by_id | Integer | FK→User, NOT NULL | Creator reference |
| target_audience | Char(20) | DEFAULT='all', CHECK | 'all', 'course', 'year', 'section' |
| target_course | String(50) | | Course filter |
| target_year | Integer | NULL, CHECK(1-4) | Year filter |
| target_section | String(5) | | Section filter |
| is_active | Boolean | DEFAULT=True | Active status |
| is_urgent | Boolean | DEFAULT=False | Urgency flag |
| created_at | DateTime | AUTO | Creation timestamp |
| updated_at | DateTime | AUTO | Update timestamp |

**Relationships**:
- N:1 → User (posted_by_id)

---

### 15. EMAIL_OTP
**Primary Key**: `id`  
**Description**: Email-based OTP for verification (FREE alternative to SMS)

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| id | Integer | PK, Auto | Unique identifier |
| email | String(254) | NOT NULL | Email address |
| otp_code | String(6) | NOT NULL | 6-digit OTP code |
| purpose | Char(20) | NOT NULL, CHECK | 'password_reset', 'email_verification', 'login_verification', 'registration' |
| is_used | Boolean | DEFAULT=False | Usage status |
| expires_at | DateTime | NOT NULL | Expiration timestamp |
| created_at | DateTime | AUTO | Creation timestamp |

**Relationships**:
- N:1 → User (via email)

---

### 16. OTP (Legacy)
**Primary Key**: `id`  
**Description**: Phone-based OTP (legacy, EmailOTP preferred)

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| id | Integer | PK, Auto | Unique identifier |
| phone_number | String(15) | NOT NULL | Phone number |
| otp_code | String(6) | NOT NULL | 6-digit OTP |
| purpose | Char(20) | NOT NULL | Purpose of OTP |
| is_used | Boolean | DEFAULT=False | Usage status |
| expires_at | DateTime | NOT NULL | Expiration timestamp |
| created_at | DateTime | AUTO | Creation timestamp |

---

### 17. AI_CHAT
**Primary Key**: `id`  
**Description**: AI chat conversation sessions

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| id | Integer | PK, Auto | Unique identifier |
| user_id | Integer | FK→User, NOT NULL | User reference |
| chat_type | Char(30) | DEFAULT='general_query', CHECK | Type of chat |
| session_id | String(100) | NOT NULL | Unique session identifier |
| created_at | DateTime | AUTO | Creation timestamp |
| updated_at | DateTime | AUTO | Update timestamp |

**Relationships**:
- N:1 → User (user_id)
- 1:N → ChatMessage (chat)

---

### 18. CHAT_MESSAGE
**Primary Key**: `id`  
**Description**: Individual messages in AI chat conversations

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| id | Integer | PK, Auto | Unique identifier |
| chat_id | Integer | FK→AIChat, NOT NULL | Chat session reference |
| sender | Char(10) | NOT NULL, CHECK | 'user' or 'ai' |
| message | Text | NOT NULL | Message content |
| context_data | JSON | DEFAULT={} | Additional context |
| timestamp | DateTime | AUTO | Message timestamp |

**Relationships**:
- N:1 → AIChat (chat_id)

---

### 19. ALGORITHMIC_TIMETABLE_SUGGESTION
**Primary Key**: `id`  
**Description**: Algorithm-generated timetable suggestions using DSA/DBMS principles

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| id | Integer | PK, Auto | Unique identifier |
| generated_by_id | Integer | FK→User, NOT NULL | Creator reference |
| course | String(50) | NOT NULL | Course name |
| year | Integer | NOT NULL | Year |
| section | String(5) | NOT NULL | Section |
| academic_year | String(10) | NOT NULL | Academic year |
| semester | Integer | NOT NULL | Semester |
| algorithm_type | Char(25) | DEFAULT='constraint_satisfaction', CHECK | Algorithm used |
| suggestion_data | JSON | NOT NULL | Generated timetable data |
| optimization_score | Float | DEFAULT=0.0 | Score (0-100) |
| conflicts_resolved | Integer | DEFAULT=0 | Number of conflicts resolved |
| constraint_violations | Integer | DEFAULT=0 | Number of violations |
| status | Char(20) | DEFAULT='generated', CHECK | Status |
| reviewed_by_id | Integer | FK→User, NULL | Reviewer reference |
| notes | Text | | Additional notes |
| created_at | DateTime | AUTO | Creation timestamp |
| updated_at | DateTime | AUTO | Update timestamp |

**Relationships**:
- N:1 → User (generated_by_id, reviewed_by_id)

---

### 20. TIMETABLE_CONFIGURATION
**Primary Key**: `id`  
**Description**: Configuration for timetable generation algorithms

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| id | Integer | PK, Auto | Unique identifier |
| name | String(100) | UNIQUE, NOT NULL | Configuration name |
| description | Text | | Description |
| days_per_week | Integer | DEFAULT=5 | Working days |
| periods_per_day | Integer | DEFAULT=8 | Periods per day |
| period_duration | Integer | DEFAULT=50 | Duration (minutes) |
| break_periods | JSON | DEFAULT=[] | Break period numbers |
| break_duration | Integer | DEFAULT=15 | Break duration (minutes) |
| algorithm_type | Char(25) | NOT NULL | Algorithm type |
| is_active | Boolean | DEFAULT=True | Active status |
| created_by_id | Integer | FK→User, NOT NULL | Creator reference |
| created_at | DateTime | AUTO | Creation timestamp |
| updated_at | DateTime | AUTO | Update timestamp |

**Relationships**:
- N:1 → User (created_by_id)

---

### 21. STUDY_RECOMMENDATION
**Primary Key**: `id`  
**Description**: AI-generated study recommendations for students

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| id | Integer | PK, Auto | Unique identifier |
| student_id | Integer | FK→StudentProfile, NOT NULL | Student reference |
| recommendation_type | Char(25) | NOT NULL, CHECK | Type of recommendation |
| title | String(200) | NOT NULL | Recommendation title |
| description | Text | NOT NULL | Detailed description |
| priority | Char(10) | DEFAULT='medium', CHECK | Priority level |
| confidence_score | Float | DEFAULT=0.0 | AI confidence (0-100) |
| is_read | Boolean | DEFAULT=False | Read status |
| is_implemented | Boolean | DEFAULT=False | Implementation status |
| generated_data | JSON | DEFAULT={} | AI analysis data |
| expires_at | DateTime | NULL | Expiration timestamp |
| created_at | DateTime | AUTO | Creation timestamp |

**Relationships**:
- N:1 → StudentProfile (student_id)
- N:M → Subject (subjects)

---

### 22. PERFORMANCE_INSIGHT
**Primary Key**: `id`  
**Description**: AI-generated performance insights and trends

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| id | Integer | PK, Auto | Unique identifier |
| student_id | Integer | FK→StudentProfile, NULL | Student reference (if individual) |
| title | String(200) | NOT NULL | Insight title |
| insight_type | Char(25) | NOT NULL, CHECK | Type of insight |
| scope | Char(15) | NOT NULL, CHECK | Scope level |
| description | Text | NOT NULL | Detailed description |
| course | String(50) | | Course filter |
| year | Integer | NULL | Year filter |
| section | String(5) | | Section filter |
| insight_data | JSON | NOT NULL | Analysis data |
| confidence_score | Float | NOT NULL | AI confidence (0-100) |
| impact_score | Float | DEFAULT=0.0 | Impact score (0-100) |
| recommendations | Text | | AI recommendations |
| generated_by_id | Integer | FK→User, NULL | Generator reference |
| is_actionable | Boolean | DEFAULT=True | Actionable flag |
| is_viewed | Boolean | DEFAULT=False | View status |
| created_at | DateTime | AUTO | Creation timestamp |
| updated_at | DateTime | AUTO | Update timestamp |

**Relationships**:
- N:1 → StudentProfile (student_id)
- N:1 → User (generated_by_id)

---

### 23. AI_ANALYTICS_REPORT
**Primary Key**: `id`  
**Description**: Comprehensive AI-generated analytics reports

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| id | Integer | PK, Auto | Unique identifier |
| report_type | Char(25) | NOT NULL, CHECK | Type of report |
| title | String(200) | NOT NULL | Report title |
| period | Char(10) | NOT NULL, CHECK | Time period |
| start_date | Date | NOT NULL | Start date |
| end_date | Date | NOT NULL | End date |
| course_filter | String(50) | | Course filter |
| year_filter | Integer | NULL | Year filter |
| section_filter | String(5) | | Section filter |
| report_data | JSON | NOT NULL | Complete analytics data |
| summary | Text | NOT NULL | Summary |
| key_insights | JSON | DEFAULT=[] | Key insights |
| recommendations | Text | | Recommendations |
| generated_by_id | Integer | FK→User, NOT NULL | Generator reference |
| is_published | Boolean | DEFAULT=False | Published status |
| views_count | Integer | DEFAULT=0 | View counter |
| created_at | DateTime | AUTO | Creation timestamp |
| updated_at | DateTime | AUTO | Update timestamp |

**Relationships**:
- N:1 → User (generated_by_id)

---

### 24. SMART_NOTIFICATION
**Primary Key**: `id`  
**Description**: AI-generated smart notifications

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| id | Integer | PK, Auto | Unique identifier |
| recipient_id | Integer | FK→User, NOT NULL | Recipient reference |
| notification_type | Char(25) | NOT NULL, CHECK | Type of notification |
| title | String(200) | NOT NULL | Notification title |
| message | Text | NOT NULL | Notification message |
| priority | Char(10) | DEFAULT='medium', CHECK | Priority level |
| ai_context | JSON | DEFAULT={} | AI decision context |
| confidence_score | Float | DEFAULT=0.0 | Relevance score (0-100) |
| is_read | Boolean | DEFAULT=False | Read status |
| is_dismissed | Boolean | DEFAULT=False | Dismissed status |
| read_at | DateTime | NULL | Read timestamp |
| scheduled_for | DateTime | NULL | Scheduled delivery time |
| expires_at | DateTime | NULL | Expiration timestamp |
| created_at | DateTime | AUTO | Creation timestamp |

**Relationships**:
- N:1 → User (recipient_id)

---

### 25. STUDY_MATERIAL
**Primary Key**: `id`  
**Description**: Study materials uploaded by teachers

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| id | Integer | PK, Auto | Unique identifier |
| title | String(200) | NOT NULL | Material title |
| description | Text | | Description |
| subject_id | Integer | FK→Subject, NOT NULL | Subject reference |
| course | String(50) | NOT NULL | Course name |
| year | Integer | NOT NULL | Year |
| section | String(10) | | Section |
| material_type | Char(20) | DEFAULT='document', CHECK | Type of material |
| content | Text | | Text content |
| file_url | String(200) | | File/link URL |
| uploaded_by_id | Integer | FK→User, NOT NULL | Uploader reference |
| is_published | Boolean | DEFAULT=True | Published status |
| created_at | DateTime | AUTO | Creation timestamp |
| updated_at | DateTime | AUTO | Update timestamp |

**Relationships**:
- N:1 → Subject (subject_id)
- N:1 → User (uploaded_by_id)

---

### 26. ASSIGNMENT
**Primary Key**: `id`  
**Description**: Assignments created by teachers

| Attribute | Type | Constraints | Description |
|-----------|------|-------------|-------------|
| id | Integer | PK, Auto | Unique identifier |
| title | String(200) | NOT NULL | Assignment title |
| description | Text | NOT NULL | Assignment description |
| subject_id | Integer | FK→Subject, NOT NULL | Subject reference |
| course | String(50) | NOT NULL | Course name |
| year | Integer | NOT NULL | Year |
| section | String(10) | | Section |
| due_date | DateTime | NOT NULL | Due date and time |
| max_marks | Integer | DEFAULT=100 | Maximum marks |
| instructions | Text | | Instructions |
| created_by_id | Integer | FK→User, NOT NULL | Creator reference |
| is_published | Boolean | DEFAULT=False | Published status |
| status | Char(20) | DEFAULT='draft', CHECK | Status |
| created_at | DateTime | AUTO | Creation timestamp |
| updated_at | DateTime | AUTO | Update timestamp |

**Relationships**:
- N:1 → Subject (subject_id)
- N:1 → User (created_by_id)

---

## Relationship Summary

### One-to-One (1:1) Relationships:
1. **User ↔ StudentProfile** (via user_id)
2. **User ↔ AdminProfile** (via user_id)
3. **User ↔ TeacherProfile** (via user_id)
4. **TeacherProfile ↔ Teacher** (via employee_id)

### One-to-Many (1:N) Relationships:
1. **Course → Subject** (1 course has many subjects)
2. **Subject → TimetableEntry** (1 subject has many timetable entries)
3. **Subject → Enrollment** (1 subject has many enrollments)
4. **Subject → StudyMaterial** (1 subject has many materials)
5. **Subject → Assignment** (1 subject has many assignments)
6. **Teacher → TimetableEntry** (1 teacher has many timetable entries)
7. **TimeSlot → TimetableEntry** (1 time slot has many entries)
8. **Room → TimetableEntry** (1 room has many entries)
9. **TimetableEntry → Attendance** (1 entry has many attendance records)
10. **StudentProfile → Enrollment** (1 student has many enrollments)
11. **StudentProfile → Attendance** (1 student has many attendance records)
12. **StudentProfile → StudyRecommendation** (1 student has many recommendations)
13. **StudentProfile → PerformanceInsight** (1 student has many insights)
14. **User → AIChat** (1 user has many chats)
15. **User → Announcement** (1 user posts many announcements)
16. **AIChat → ChatMessage** (1 chat has many messages)

### Many-to-Many (N:M) Relationships:
1. **Teacher ↔ Subject** (via TeacherSubject junction table)
   - Teachers can teach multiple subjects
   - Subjects can be taught by multiple teachers
2. **Subject ↔ StudyRecommendation** (via ManyToManyField)
   - Recommendations can target multiple subjects
   - Subjects can appear in multiple recommendations

---

## Key Constraints and Business Rules

1. **User Type Constraint**: Each user must be exactly one type (student, teacher, or admin)
2. **Unique Roll Numbers**: Student roll numbers must be unique across all courses
3. **Timetable Conflict Prevention**: 
   - No room can have two classes at the same time
   - No teacher can teach two classes at the same time
   - No student section can have two classes at the same time
4. **Email Uniqueness**: Email addresses must be unique across all users
5. **OTP Expiration**: OTPs expire after 15 minutes
6. **Attendance Uniqueness**: One attendance record per student per class per date
7. **Enrollment Uniqueness**: One enrollment per student per subject per semester

---

## Database Indexes (Recommended)

### Primary Indexes (Automatic):
- All primary keys are automatically indexed

### Foreign Key Indexes (Automatic):
- All foreign keys are automatically indexed

### Additional Recommended Indexes:
1. `User.email` - For fast login lookups
2. `User.user_type` - For filtering by user type
3. `StudentProfile.roll_number` - For student lookups
4. `TimetableEntry(day_of_week, time_slot_id)` - For timetable queries
5. `Attendance(student_id, date)` - For attendance reports
6. `EmailOTP(email, is_used, expires_at)` - For OTP verification
7. `Announcement(is_active, is_urgent, created_at)` - For announcement queries

---

## Database Normalization

### Normal Form Compliance:
- **1NF**: All tables comply (atomic values, no repeating groups)
- **2NF**: All tables comply (no partial dependencies)
- **3NF**: Most tables comply (minor denormalization in TimetableEntry for performance)
  - `TimetableEntry.course` is denormalized from StudentProfile for quick queries

### Denormalization Decisions:
1. **TimetableEntry.course**: Stored directly to avoid joins when querying timetables
2. **TimetableEntry.academic_year**: Stored for historical data separation

---

## Data Integrity

### Referential Integrity:
- CASCADE deletes for most relationships
- SET NULL for optional relationships (marked_by, reviewed_by)
- RESTRICT would prevent deletion if referenced (handled by Django)

### Check Constraints:
- User type values limited to ('student', 'teacher', 'admin')
- Year values limited to 1-4
- Semester values limited to 1-8
- Status fields have predefined choices
- Period numbers limited to 1-10

---

## ER Diagram Legend

```
Entity (Rectangle)
├── Primary Key (Underlined, Bold)
├── Attributes (Normal)
└── Foreign Key (FK→EntityName)

Relationships:
├── 1:1 (One-to-One) ──┐
├── 1:N (One-to-Many) ─┼─►
└── N:M (Many-to-Many) ─┘
```

---

**Generated**: 2025-01-31  
**Database**: SQLite3/PostgreSQL  
**ORM**: Django 4.2  
**Total Entities**: 26  
**Total Relationships**: 30+

