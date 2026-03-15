# Student Academic Monitoring System (SAMS)

A comprehensive web application for monitoring student academic progress with parent verification chatbot.

## 📁 Project Structure

```
parent_chatbot/
├── app/
│   ├── __init__.py              # Flask app factory
│   ├── config.py                # Configuration settings
│   ├── models/                  # Database models
│   │   ├── __init__.py
│   │   ├── user.py              # User model with roles
│   │   ├── student.py           # Student model
│   │   ├── attendance.py        # Attendance model
│   │   ├── marks.py             # Marks/CGPA model
│   │   ├── fees.py              # Fees model
│   │   ├── notifications.py     # Notifications model
│   │   └── faculty.py           # Faculty model
│   ├── routes/                  # API Routes
│   │   ├── __init__.py
│   │   ├── auth.py              # Authentication routes
│   │   ├── admin.py             # Admin dashboard routes
│   │   ├── faculty.py           # Faculty routes
│   │   ├── parent.py            # Parent routes
│   │   ├── student.py           # Student routes
│   │   ├── api.py               # REST API endpoints
│   │   └── chatbot.py           # Chatbot API
│   ├── services/                # Business logic
│   │   ├── __init__.py
│   │   ├── auth_service.py      # Authentication service
│   │   ├── attendance_service.py
│   │   ├── marks_service.py
│   │   ├── fees_service.py
│   │   └── notification_service.py
│   ├── utils/                   # Utilities
│   │   ├── __init__.py
│   │   ├── decorators.py        # Role-based decorators
│   │   ├── validators.py        # Input validators
│   │   └── helpers.py           # Helper functions
│   └── templates/               # HTML Templates
│       ├── base.html
│       ├── auth/
│       │   ├── login.html
│       │   ├── register.html
│       │   └── forgot_password.html
│       ├── admin/
│       │   ├── dashboard.html
│       │   ├── students.html
│       │   ├── faculty.html
│       │   └── settings.html
│       ├── faculty/
│       │   ├── dashboard.html
│       │   ├── attendance.html
│       │   ├── marks.html
│       │   └── students.html
│       ├── parent/
│       │   ├── dashboard.html
│       │   ├── reports.html
│       │   ├── chatbot.html
│       │   └── notifications.html
│       └── student/
│           ├── dashboard.html
│           ├── profile.html
│           └── results.html
├── static/
│   ├── css/
│   │   ├── main.css
│   │   ├── dashboard.css
│   │   ├── reports.css
│   │   └── chatbot.css
│   ├── js/
│   │   ├── main.js
│   │   ├── dashboard.js
│   │   ├── reports.js
│   │   ├── chatbot.js
│   │   └── charts.js
│   └── images/
├── tests/
│   ├── __init__.py
│   ├── test_auth.py
│   ├── test_api.py
│   └── test_models.py
├── docs/
│   ├── API.md                   # API Documentation
│   ├── DATABASE.md              # Database Schema
│   └── SETUP.md                 # Setup Instructions
├── migrations/                  # Database migrations
├── requirements.txt
├── config.py
├── run.py
└── README.md
```

## 🚀 Features

### Academic Monitoring
- Overall attendance percentage
- Subject-wise attendance
- Semester-wise attendance reports
- Low attendance alerts

### Academic Status
- Number of backlogs
- Repeated subjects
- Incomplete subjects
- Course completion status

### Academic Performance
- Current CGPA
- Year-wise CGPA
- Semester-wise CGPA
- Subject-wise marks

### Academic Notifications
- Upcoming exams
- Assignment deadlines
- Academic calendar updates

### Financial Information
- Fee payment status
- Pending fees
- Payment history
- Scholarship status

### Communication Support
- Faculty contact information
- Class advisor details
- Academic office contacts

### Performance Insights
- Strong subjects
- Weak subjects
- Academic improvement suggestions

### System Utilities
- Notifications and announcements
- Logout / secure session termination

## 👥 User Roles

1. **Admin**: Full system access, manage users, configure settings
2. **Faculty**: Manage attendance, marks, view student reports
3. **Parent**: View child's academic progress, chatbot access
4. **Student**: View own profile, attendance, marks, notifications

## 🔧 Technology Stack

- **Backend**: Flask (Python)
- **Database**: MongoDB
- **Frontend**: HTML5, CSS3, JavaScript
- **Authentication**: JWT + Session-based
- **Real-time**: WebSocket for notifications

## 📋 Setup Instructions

1. Install dependencies: `pip install -r requirements.txt`
2. Configure MongoDB connection in `config.py`
3. Run migrations: `python run.py db migrate`
4. Start server: `python run.py`

## 📡 API Endpoints

See `docs/API.md` for complete API documentation.

## 📊 Database Schema

See `docs/DATABASE.md` for complete database schema.
