# Database Schema Documentation

## MongoDB Collections

### 1. Users Collection
```javascript
{
  "_id": ObjectId("..."),
  "username": "parent001",
  "email": "parent@email.com",
  "password_hash": "$2b$12$...", // bcrypt hashed
  "role": "parent", // Enum: admin, faculty, parent, student
  "is_active": true,
  "is_verified": true,
  "profile": {
    "first_name": "John",
    "last_name": "Parent",
    "phone": "9876543210",
    "address": "123 Main St, City",
    "profile_image": "url_to_image"
  },
  "role_specific": {
    // For parent
    "student_reg_no": "STU001",
    "relationship": "Father",
    
    // For faculty
    "employee_id": "FAC001",
    "department": "CSE",
    "designation": "Assistant Professor",
    "subjects": ["DBMS", "Operating Systems"],
    
    // For student (linked to students collection)
    "student_id": ObjectId("..."),
    
    // For admin
    "admin_level": "super", // super, standard
    "permissions": ["all"]
  },
  "last_login": ISODate("2025-03-14T10:30:00Z"),
  "created_at": ISODate("2025-01-01T00:00:00Z"),
  "updated_at": ISODate("2025-03-14T10:30:00Z"),
  "otp": {
    "code": "123456",
    "expiry": ISODate("2025-03-14T10:35:00Z"),
    "attempts": 0
  }
}
```

**Indexes:**
- `username`: Unique
- `email`: Unique
- `role`: For role-based queries
- `role_specific.student_reg_no`: For parent lookups

---

### 2. Students Collection
```javascript
{
  "_id": ObjectId("..."),
  "reg_no": "STU001",
  "roll_no": "22CS101",
  "personal_info": {
    "first_name": "Arjun",
    "last_name": "Mehta",
    "date_of_birth": ISODate("2003-05-15T00:00:00Z"),
    "gender": "Male",
    "blood_group": "B+",
    "category": "General",
    "aadhar_number": "XXXX-XXXX-1234"
  },
  "contact": {
    "email": "arjun@student.college.edu",
    "phone": "9876543210",
    "address": {
      "street": "456 College Road",
      "city": "Hyderabad",
      "state": "Telangana",
      "pincode": "500001"
    }
  },
  "academic": {
    "branch": "CSE",
    "year": 3,
    "semester": 6,
    "section": "A",
    "batch": "2022-2026",
    "cgpa": 8.2,
    "backlogs": 1,
    "course_status": "Active" // Active, Completed, Discontinued, At Risk
  },
  "admission": {
    "year": 2022,
    "type": "Regular", // Regular, Lateral Entry
    "category": "Convener",
    "rank": 1250
  },
  "family": {
    "father_name": "Suresh Mehta",
    "mother_name": "Lata Mehta",
    "parent_phone": "9876543211",
    "parent_email": "parent@email.com",
    "annual_income": 500000
  },
  "advisor": {
    "faculty_id": ObjectId("..."),
    "name": "Dr. R. Sharma",
    "email": "r.sharma@college.edu",
    "phone": "9001111111"
  },
  "documents": {
    "photo": "url",
    "id_proof": "url",
    "marksheets": ["url1", "url2"],
    "caste_certificate": "url",
    "income_certificate": "url"
  },
  "created_at": ISODate("2022-07-01T00:00:00Z"),
  "updated_at": ISODate("2025-03-14T10:30:00Z")
}
```

**Indexes:**
- `reg_no`: Unique
- `academic.branch`: For branch-wise queries
- `academic.year`: For year-wise queries
- `advisor.faculty_id`: For advisor lookups

---

### 3. Attendance Collection
```javascript
{
  "_id": ObjectId("..."),
  "student_reg_no": "STU001",
  "subject_code": "CS301",
  "subject_name": "Database Management Systems",
  "semester": 6,
  "academic_year": "2024-2025",
  "records": [
    {
      "date": ISODate("2025-03-01T00:00:00Z"),
      "status": "present", // present, absent, late, on_duty
      "period": 1,
      "marked_by": ObjectId("..."),
      "marked_at": ISODate("2025-03-01T09:30:00Z")
    },
    {
      "date": ISODate("2025-03-02T00:00:00Z"),
      "status": "absent",
      "period": 1,
      "marked_by": ObjectId("..."),
      "marked_at": ISODate("2025-03-02T09:30:00Z"),
      "reason": "Medical leave"
    }
  ],
  "summary": {
    "total_classes": 45,
    "attended": 40,
    "absent": 3,
    "late": 2,
    "percentage": 88.9,
    "status": "good" // good, warning, critical
  },
  "created_at": ISODate("2025-01-01T00:00:00Z"),
  "updated_at": ISODate("2025-03-14T10:30:00Z")
}
```

**Indexes:**
- `student_reg_no`: For student lookups
- `subject_code`: For subject lookups
- `semester`: For semester queries
- Compound: `{student_reg_no, subject_code, semester}`: Unique

---

### 4. Marks Collection
```javascript
{
  "_id": ObjectId("..."),
  "student_reg_no": "STU001",
  "subject_code": "CS301",
  "subject_name": "Database Management Systems",
  "semester": 6,
  "academic_year": "2024-2025",
  "exam_type": "regular", // regular, supplementary, revaluation
  "components": {
    "internal": {
      "mid1": {
        "marks": 18,
        "max_marks": 20,
        "percentage": 90
      },
      "mid2": {
        "marks": 17,
        "max_marks": 20,
        "percentage": 85
      },
      "assignments": {
        "marks": 10,
        "max_marks": 10,
        "percentage": 100
      },
      "total": {
        "marks": 45,
        "max_marks": 50,
        "percentage": 90
      }
    },
    "external": {
      "marks": 42,
      "max_marks": 50,
      "percentage": 84
    }
  },
  "total": {
    "marks": 87,
    "max_marks": 100,
    "percentage": 87,
    "grade": "A",
    "grade_point": 8,
    "result": "pass" // pass, fail, absent
  },
  "backlog_status": false,
  "previous_attempts": [
    {
      "semester": 5,
      "marks": 35,
      "result": "fail"
    }
  ],
  "uploaded_by": ObjectId("..."),
  "uploaded_at": ISODate("2025-03-10T10:30:00Z"),
  "created_at": ISODate("2025-03-10T10:30:00Z"),
  "updated_at": ISODate("2025-03-10T10:30:00Z")
}
```

**Indexes:**
- `student_reg_no`: For student lookups
- `subject_code`: For subject lookups
- `semester`: For semester queries
- `backlog_status`: For backlog queries
- Compound: `{student_reg_no, subject_code, semester, exam_type}`: Unique

---

### 5. CGPA Records Collection
```javascript
{
  "_id": ObjectId("..."),
  "student_reg_no": "STU001",
  "semester": 6,
  "academic_year": "2024-2025",
  "sgpa": 8.5,
  "credits_earned": 24,
  "total_credits": 24,
  "subjects": [
    {
      "subject_code": "CS301",
      "subject_name": "DBMS",
      "credits": 4,
      "grade": "A",
      "grade_point": 8,
      "credit_points": 32
    },
    {
      "subject_code": "CS302",
      "subject_name": "Operating Systems",
      "credits": 4,
      "grade": "B",
      "grade_point": 7,
      "credit_points": 28
    }
  ],
  "cumulative": {
    "cgpa": 8.2,
    "total_credits_earned": 120,
    "total_credits": 120,
    "total_grade_points": 984
  },
  "backlogs": {
    "count": 1,
    "subjects": ["PH101"]
  },
  "class_rank": 15,
  "section_rank": 3,
  "result_status": "pass", // pass, fail, promoted_with_backlog
  "published": true,
  "published_at": ISODate("2025-01-15T10:00:00Z"),
  "created_at": ISODate("2025-01-15T10:00:00Z"),
  "updated_at": ISODate("2025-01-15T10:00:00Z")
}
```

**Indexes:**
- `student_reg_no`: For student lookups
- `semester`: For semester queries
- Compound: `{student_reg_no, semester}`: Unique

---

### 6. Fees Collection
```javascript
{
  "_id": ObjectId("..."),
  "student_reg_no": "STU001",
  "semester": 6,
  "academic_year": "2024-2025",
  "fee_structure": {
    "tuition_fee": 20000,
    "exam_fee": 2000,
    "library_fee": 1000,
    "lab_fee": 1500,
    "sports_fee": 500,
    "total": 25000
  },
  "payments": [
    {
      "receipt_no": "RCP2025001",
      "amount": 15000,
      "mode": "online", // online, cash, cheque, dd
      "transaction_id": "TXN123456",
      "bank": "SBI",
      "date": ISODate("2025-01-10T10:30:00Z"),
      "status": "completed",
      "verified_by": ObjectId("..."),
      "verified_at": ISODate("2025-01-10T11:00:00Z")
    },
    {
      "receipt_no": "RCP2025002",
      "amount": 10000,
      "mode": "cash",
      "date": ISODate("2025-02-15T14:30:00Z"),
      "status": "completed",
      "verified_by": ObjectId("..."),
      "verified_at": ISODate("2025-02-15T15:00:00Z")
    }
  ],
  "summary": {
    "total_due": 25000,
    "total_paid": 25000,
    "pending": 0,
    "status": "paid", // paid, partial, pending, overdue
    "due_date": ISODate("2025-01-31T00:00:00Z")
  },
  "scholarship": {
    "eligible": true,
    "type": "merit",
    "amount": 5000,
    "applied": true,
    "approved": true,
    "disbursed": true,
    "disbursed_at": ISODate("2025-02-01T00:00:00Z")
  },
  "concession": {
    "type": "staff_ward",
    "percentage": 25,
    "amount": 6250
  },
  "created_at": ISODate("2025-01-01T00:00:00Z"),
  "updated_at": ISODate("2025-02-15T15:00:00Z")
}
```

**Indexes:**
- `student_reg_no`: For student lookups
- `semester`: For semester queries
- `summary.status`: For status queries
- Compound: `{student_reg_no, semester}`: Unique

---

### 7. Faculty Collection
```javascript
{
  "_id": ObjectId("..."),
  "employee_id": "FAC001",
  "personal_info": {
    "first_name": "Dr. R.",
    "last_name": "Sharma",
    "gender": "Male",
    "date_of_birth": ISODate("1975-03-15T00:00:00Z"),
    "qualification": "Ph.D. in Computer Science",
    "experience_years": 15
  },
  "contact": {
    "email": "r.sharma@college.edu",
    "phone": "9001111111",
    "cabin": "Block A, Room 101",
    "office_hours": "Mon-Fri 2PM-4PM"
  },
  "department": "CSE",
  "designation": "Professor & HOD",
  "subjects": [
    {
      "code": "CS301",
      "name": "DBMS",
      "semester": [5, 6]
    },
    {
      "code": "CS401",
      "name": "Advanced DBMS",
      "semester": [7]
    }
  ],
  "assigned_sections": [
    {
      "year": 3,
      "section": "A",
      "subjects": ["CS301"]
    },
    {
      "year": 4,
      "section": "B",
      "subjects": ["CS401"]
    }
  ],
  "is_advisor": true,
  "advisor_sections": [
    {
      "year": 3,
      "section": "A",
      "batch": "2022-2026"
    }
  ],
  "research": {
    "areas": ["Database Systems", "Big Data"],
    "publications": 25,
    "projects": [
      {
        "title": "Intelligent Database System",
        "funding": "AICTE",
        "amount": 500000,
        "status": "ongoing"
      }
    ]
  },
  "joining_date": ISODate("2010-07-01T00:00:00Z"),
  "is_active": true,
  "created_at": ISODate("2010-07-01T00:00:00Z"),
  "updated_at": ISODate("2025-03-14T10:30:00Z")
}
```

**Indexes:**
- `employee_id`: Unique
- `department`: For department queries
- `is_advisor`: For advisor lookups

---

### 8. Notifications Collection
```javascript
{
  "_id": ObjectId("..."),
  "title": "Mid-Semester Examination Schedule",
  "message": "Mid-semester exams will commence from March 15, 2025. Hall tickets will be available from March 12.",
  "category": "exam", // exam, academic, fee, general, urgent
  "priority": "high", // low, medium, high, urgent
  "target": {
    "type": "all", // all, specific, role, batch
    "roles": ["student", "parent"],
    "branches": ["CSE", "ECE"],
    "years": [3, 4],
    "specific_users": ["STU001", "STU002"]
  },
  "attachments": [
    {
      "name": "Exam_Schedule.pdf",
      "url": "url_to_file",
      "type": "pdf"
    }
  ],
  "posted_by": {
    "user_id": ObjectId("..."),
    "name": "Examination Cell",
    "role": "admin"
  },
  "schedule": {
    "publish_at": ISODate("2025-03-10T09:00:00Z"),
    "expiry_at": ISODate("2025-03-20T23:59:59Z")
  },
  "acknowledgment_required": true,
  "acknowledgments": [
    {
      "user_id": ObjectId("..."),
      "role": "student",
      "acknowledged_at": ISODate("2025-03-10T10:30:00Z")
    }
  ],
  "status": "active", // draft, scheduled, active, expired, archived
  "created_at": ISODate("2025-03-09T15:30:00Z"),
  "updated_at": ISODate("2025-03-10T09:00:00Z")
}
```

**Indexes:**
- `category`: For category queries
- `priority`: For priority queries
- `status`: For status queries
- `schedule.publish_at`: For scheduled notifications

---

### 9. Subjects Collection
```javascript
{
  "_id": ObjectId("..."),
  "code": "CS301",
  "name": "Database Management Systems",
  "short_name": "DBMS",
  "department": "CSE",
  "semester": 5,
  "credits": 4,
  "type": "theory", // theory, practical, elective, project
  "hours_per_week": 4,
  "syllabus": {
    "units": [
      {
        "unit_no": 1,
        "title": "Introduction to DBMS",
        "topics": ["Data vs Information", "DBMS Architecture"]
      }
    ],
    "textbooks": [
      {
        "title": "Database System Concepts",
        "author": "Silberschatz, Korth",
        "edition": "7th"
      }
    ]
  },
  "assessment": {
    "internal_weightage": 50,
    "external_weightage": 50,
    "passing_marks_internal": 20,
    "passing_marks_external": 20,
    "passing_marks_total": 40
  },
  "is_active": true,
  "created_at": ISODate("2020-01-01T00:00:00Z"),
  "updated_at": ISODate("2024-01-01T00:00:00Z")
}
```

**Indexes:**
- `code`: Unique
- `department`: For department queries
- `semester`: For semester queries

---

### 10. Academic Calendar Collection
```javascript
{
  "_id": ObjectId("..."),
  "academic_year": "2024-2025",
  "semester": 6,
  "events": [
    {
      "title": "Semester Start",
      "start_date": ISODate("2025-01-01T00:00:00Z"),
      "end_date": ISODate("2025-01-01T00:00:00Z"),
      "type": "academic",
      "description": "Classes begin for Even Semester"
    },
    {
      "title": "Mid-Semester Exams",
      "start_date": ISODate("2025-03-15T00:00:00Z"),
      "end_date": ISODate("2025-03-22T00:00:00Z"),
      "type": "exam",
      "description": "Mid-semester examination schedule"
    },
    {
      "title": "Fee Payment Deadline",
      "start_date": ISODate("2025-01-31T00:00:00Z"),
      "end_date": ISODate("2025-01-31T23:59:59Z"),
      "type": "fee",
      "description": "Last date for fee payment without fine"
    }
  ],
  "holidays": [
    {
      "date": ISODate("2025-01-26T00:00:00Z"),
      "name": "Republic Day",
      "type": "national"
    }
  ],
  "created_at": ISODate("2024-12-01T00:00:00Z"),
  "updated_at": ISODate("2025-01-01T00:00:00Z")
}
```

**Indexes:**
- `academic_year`: For year queries
- `semester`: For semester queries

---

## Data Relationships

```
Users (1) ────────> (1) Students (for student role)
   │
   │ (1) ─────────> (1) Parents (for parent role, linked to student)
   │
   │ (1) ─────────> (1) Faculty (for faculty role)

Students (1) ──────> (N) Attendance
Students (1) ──────> (N) Marks
Students (1) ──────> (N) CGPA Records
Students (1) ──────> (N) Fees
Students (1) ──────> (N) Notifications (received)

Faculty (1) ───────> (N) Attendance (marked by)
Faculty (1) ───────> (N) Marks (uploaded by)
Faculty (1) ───────> (N) Students (as advisor)

Subjects (1) ──────> (N) Attendance
Subjects (1) ──────> (N) Marks
```

## Collection Statistics

| Collection | Expected Size | Growth Rate |
|------------|--------------|-------------|
| Users | 2,000 | +500/year |
| Students | 2,000 | +500/year |
| Attendance | 500,000 records/month | +500K/month |
| Marks | 20,000 records/semester | +20K/semester |
| CGPA Records | 12,000 | +3K/year |
| Fees | 12,000 | +3K/year |
| Faculty | 100 | +10/year |
| Notifications | 1,000 | +200/year |
| Subjects | 200 | +20/year |

## Backup Strategy

- **Daily**: Incremental backup at 2 AM
- **Weekly**: Full backup on Sundays at 3 AM
- **Monthly**: Archive backup on 1st of month
- **Retention**: 30 days for daily, 12 weeks for weekly, 12 months for monthly

## Security Measures

1. **Encryption at Rest**: MongoDB encrypted storage
2. **Access Control**: Role-based access control (RBAC)
3. **Audit Logging**: All write operations logged
4. **Data Masking**: Sensitive fields masked in logs
5. **Field Level Encryption**: Aadhar, phone numbers encrypted
