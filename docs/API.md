# API Documentation

## Authentication Endpoints

### POST /api/auth/login
Login for all user roles.

**Request:**
```json
{
  "username": "parent001",
  "password": "password123",
  "role": "parent"
}
```

**Response:**
```json
{
  "success": true,
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "id": "user_id",
    "name": "John Parent",
    "role": "parent",
    "student_reg_no": "STU001"
  }
}
```

### POST /api/auth/logout
Logout user.

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

## Admin Endpoints

### GET /api/admin/dashboard
Get admin dashboard statistics.

**Response:**
```json
{
  "total_students": 500,
  "total_faculty": 45,
  "total_parents": 480,
  "pending_approvals": 12,
  "recent_activities": [...]
}
```

### GET /api/admin/students
List all students with pagination.

**Query Parameters:**
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 20)
- `branch`: Filter by branch
- `year`: Filter by year

**Response:**
```json
{
  "students": [...],
  "total": 500,
  "page": 1,
  "pages": 25
}
```

### POST /api/admin/students
Add new student.

**Request:**
```json
{
  "reg_no": "STU006",
  "name": "New Student",
  "email": "student@college.edu",
  "phone": "9876543210",
  "branch": "CSE",
  "year": 1,
  "parent_phone": "9876543211"
}
```

### GET /api/admin/faculty
List all faculty members.

### POST /api/admin/faculty
Add new faculty member.

### GET /api/admin/reports
Generate system reports.

## Faculty Endpoints

### GET /api/faculty/dashboard
Faculty dashboard data.

### GET /api/faculty/students
List students assigned to faculty.

### POST /api/faculty/attendance
Mark attendance.

**Request:**
```json
{
  "subject": "DBMS",
  "date": "2025-03-14",
  "attendance": [
    {"reg_no": "STU001", "status": "present"},
    {"reg_no": "STU002", "status": "absent"}
  ]
}
```

### POST /api/faculty/marks
Upload marks.

**Request:**
```json
{
  "subject": "DBMS",
  "exam_type": "mid_sem",
  "marks": [
    {"reg_no": "STU001", "marks": 85, "max_marks": 100},
    {"reg_no": "STU002", "marks": 72, "max_marks": 100}
  ]
}
```

### GET /api/faculty/reports/student/:reg_no
Get student performance report.

## Parent Endpoints

### GET /api/parent/dashboard
Parent dashboard with child's summary.

**Response:**
```json
{
  "student": {
    "name": "Arjun Mehta",
    "reg_no": "STU001",
    "branch": "CSE",
    "year": 3,
    "cgpa": 8.2
  },
  "attendance_summary": {
    "overall": 85.5,
    "status": "good"
  },
  "alerts": [
    {"type": "attendance", "message": "Low attendance in Physics"},
    {"type": "fee", "message": "Pending fee for Semester 3"}
  ],
  "recent_marks": [...],
  "upcoming_events": [...]
}
```

### GET /api/parent/attendance/:reg_no
Get detailed attendance report.

**Response:**
```json
{
  "overall_percentage": 85.5,
  "subjects": [
    {"name": "DBMS", "attendance": 92, "classes_attended": 23, "total_classes": 25},
    {"name": "Operating Systems", "attendance": 78, "classes_attended": 18, "total_classes": 23}
  ],
  "monthly_trend": [...],
  "low_attendance_alerts": [...]
}
```

### GET /api/parent/marks/:reg_no
Get marks report.

**Response:**
```json
{
  "current_cgpa": 8.2,
  "semester_wise": [
    {"semester": 1, "sgpa": 7.8},
    {"semester": 2, "sgpa": 8.0},
    {"semester": 3, "sgpa": 8.5}
  ],
  "subject_wise": [
    {"subject": "DBMS", "internal": 85, "external": 88, "total": 86.5, "grade": "A"},
    {"subject": "Operating Systems", "internal": 78, "external": 82, "total": 80, "grade": "A"}
  ],
  "backlogs": [],
  "strong_subjects": ["DBMS", "Computer Networks"],
  "weak_subjects": ["Operating Systems"]
}
```

### GET /api/parent/fees/:reg_no
Get fee details.

**Response:**
```json
{
  "total_paid": 75000,
  "total_pending": 25000,
  "semester_wise": [
    {
      "semester": 1,
      "amount_due": 25000,
      "amount_paid": 25000,
      "status": "paid",
      "payment_date": "2022-07-15"
    },
    {
      "semester": 3,
      "amount_due": 25000,
      "amount_paid": 20000,
      "status": "partial",
      "pending": 5000
    }
  ],
  "scholarship": {
    "eligible": true,
    "amount": 5000,
    "status": "active"
  }
}
```

### GET /api/parent/backlogs/:reg_no
Get backlog information.

**Response:**
```json
{
  "total_backlogs": 1,
  "backlogs": [
    {
      "subject": "Engineering Physics",
      "semester": 1,
      "marks": 35,
      "attempts": 1,
      "status": "pending"
    }
  ],
  "repeated_subjects": [],
  "incomplete_subjects": []
}
```

### GET /api/parent/notifications/:reg_no
Get notifications.

### POST /api/parent/chatbot
Chatbot query endpoint.

**Request:**
```json
{
  "message": "What is my child's CGPA?"
}
```

**Response:**
```json
{
  "intent": "cgpa",
  "response": "Your child's current CGPA is 8.2",
  "data": {...}
}
```

## Student Endpoints

### GET /api/student/dashboard
Student dashboard.

### GET /api/student/profile
Student profile.

### GET /api/student/attendance
Own attendance.

### GET /api/student/marks
Own marks.

### GET /api/student/fees
Own fee status.

### GET /api/student/notifications
Notifications for student.

## Chatbot API

### POST /api/chatbot/message
Send message to chatbot.

**Request:**
```json
{
  "reg_no": "STU001",
  "message": "Show attendance report"
}
```

**Response:**
```json
{
  "success": true,
  "intent": "attendance",
  "message": "Overall attendance: 85.5%",
  "html": "<table>...</table>",
  "data": {...}
}
```

### POST /api/chatbot/quick-reply
Quick reply action.

**Request:**
```json
{
  "reg_no": "STU001",
  "action": "show_cgpa"
}
```

## Common Endpoints

### GET /api/calendar
Academic calendar.

### GET /api/faculty-contacts
Faculty contact list.

### GET /api/academic-office
Academic office contacts.

### GET /api/exams
Upcoming exams schedule.

### GET /api/assignments
Assignment deadlines.

## Response Codes

- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden (insufficient permissions)
- `404`: Not Found
- `500`: Server Error

## Authentication

All API endpoints (except login) require JWT token in header:
```
Authorization: Bearer <jwt_token>
```

## Role-Based Access

| Endpoint | Admin | Faculty | Parent | Student |
|----------|-------|---------|--------|---------|
| /api/admin/* | ✓ | ✗ | ✗ | ✗ |
| /api/faculty/* | ✓ | ✓ | ✗ | ✗ |
| /api/parent/* | ✓ | ✗ | ✓ | ✗ |
| /api/student/* | ✓ | ✓ | ✗ | ✓ |
