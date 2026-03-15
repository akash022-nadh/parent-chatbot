# 🎓 EduParent — Parent Verification & Student Information Chatbot System

A secure, production-ready parent chatbot system built with **Python + Flask + SQLite**.

---

## 🚀 Quick Start

```bash
# 1. Install dependencies
pip install flask

# 2. Initialize database
python init_db.py

# 3. Run the app
python app.py

# 4. Open in browser
http://localhost:5000
```

---

## 🔑 Demo Credentials

| Reg No | Student | Parent Phone | Backlogs | Status |
|--------|---------|--------------|----------|--------|
| STU001 | Arjun Mehta | **9876543211** | 0 | Active |
| STU002 | Priya Sharma | **9823456780** | 1 | Active |
| STU003 | Rahul Verma | **9812345670** | 2 | Active |
| STU004 | Sneha Patel | **9898765430** | 0 | Active (Scholar) |
| STU005 | Vikram Nair | **9945678900** | 3 | At Risk |

**Login steps:**
1. Enter Registration Number (e.g., `STU001`)
2. Enter Parent Phone (e.g., `9876543211`)
3. OTP is auto-filled in demo mode — click Verify

---

## 💬 Supported Chat Commands

| Query | What it shows |
|-------|--------------|
| `show attendance` | Overall + subject-wise + semester-wise |
| `low attendance alert` | Subjects below 75% |
| `show marks` | Subject-wise marks with grades |
| `cgpa` | Current + semester-wise GPA |
| `backlogs` | Active backlog subjects |
| `course status` | Year, branch, completion status |
| `fee status` | Paid / pending / history |
| `scholarship` | Scholarship eligibility & amount |
| `notifications` | Upcoming exams, alerts |
| `faculty contacts` | All faculty details |
| `performance insights` | Strong/weak subjects + suggestions |
| `academic calendar` | Exam & event schedule |
| `logout` | Secure session termination |

---

## 📁 Project Structure

```
parent_chatbot/
├── app.py          # Flask routes & session management
├── models.py       # SQLite database access functions
├── chatbot.py      # Intent detection & response generation
├── init_db.py      # Database schema + sample data
├── requirements.txt
├── school.db       # Auto-generated SQLite database
└── templates/
    ├── index.html  # Login/auth flow (3-step)
    └── chat.html   # Chatbot interface
```

---

## 🛡️ Security Features

- 3-step OTP authentication
- Server-side session management
- SQL injection prevention (parameterized queries)
- Session expiry on logout
- Input sanitization
- Phone number masking in UI

---

## 🗄️ Database Tables

- **students** — reg_no, name, cgpa, backlogs, attendance, branch, advisor
- **parents** — linked to student, phone, OTP storage
- **academic_data** — per-subject marks, attendance, grades per semester
- **fees** — semester-wise fee tracking with scholarship
- **notifications** — alerts, exam notices, announcements
- **faculty** — contact info, cabin details
