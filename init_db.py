import random
from datetime import datetime, timedelta
from pymongo import MongoClient
from flask_bcrypt import Bcrypt
import os

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.environ.get("DB_NAME", "school_chatbot")

bcrypt = Bcrypt()

def init_db():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]

    # Drop existing collections
    db.faculty.drop()
    db.students.drop()
    db.parents.drop()
    db.academic_data.drop()
    db.fees.drop()
    db.notifications.drop()
    db.users.drop()  # Also drop users collection

    # --- USERS (for authentication) ---
    # Generate proper bcrypt hashes
    admin_hash = bcrypt.generate_password_hash('admin123').decode('utf-8')
    faculty_hash = bcrypt.generate_password_hash('faculty123').decode('utf-8')
    student_hash = bcrypt.generate_password_hash('student123').decode('utf-8')
    parent_hash = bcrypt.generate_password_hash('parent123').decode('utf-8')
    
    users = [
        {
            "username": "admin",
            "email": "admin@college.edu",
            "password_hash": admin_hash,
            "role": "admin",
            "is_active": True,
            "is_verified": True,
            "profile": {
                "first_name": "System",
                "last_name": "Administrator",
                "phone": "9000000000"
            },
            "created_at": datetime.utcnow()
        },
        {
            "username": "faculty001",
            "email": "faculty@college.edu",
            "password_hash": faculty_hash,
            "role": "faculty",
            "is_active": True,
            "is_verified": True,
            "profile": {
                "first_name": "Dr. kumar",
                "last_name": "devagopu",
                "phone": "9876789690"
            },
            "role_specific": {
                "employee_id": "FAC001",
                "department": "CSE",
                "designation": "Professor"
            },
            "created_at": datetime.utcnow()
        },
        {
            "username": "student001",
            "email": "student@college.edu",
            "password_hash": student_hash,
            "role": "student",
            "is_active": True,
            "is_verified": True,
            "profile": {
                "first_name": "Arjun",
                "last_name": "Mehta",
                "phone": "9876543210"
            },
            "role_specific": {
                "student_reg_no": "STU001"
            },
            "created_at": datetime.utcnow()
        },
        {
            "username": "parent001",
            "email": "parent@email.com",
            "password_hash": parent_hash,
            "role": "parent",
            "is_active": True,
            "is_verified": True,
            "profile": {
                "first_name": "Suresh",
                "last_name": "Mehta",
                "phone": "9876543211"
            },
            "role_specific": {
                "student_reg_no": "STU001",
                "relationship": "Father"
            },
            "created_at": datetime.utcnow()
        }
    ]
    db.users.insert_many(users)

    # --- FACULTY ---
    faculty = [
        {"name": "Dr. R. Sharma", "subject": "Mathematics", "email": "r.sharma@college.edu", "phone": "9001111111", "cabin": "Block A, Room 101"},
        {"name": "Prof. S. Kumar", "subject": "Physics", "email": "s.kumar@college.edu", "phone": "9001111112", "cabin": "Block A, Room 102"},
        {"name": "Dr. P. Reddy", "subject": "Data Structures", "email": "p.reddy@college.edu", "phone": "9001111113", "cabin": "Block B, Room 201"},
        {"name": "Prof. M. Rao", "subject": "DBMS", "email": "m.rao@college.edu", "phone": "9001111114", "cabin": "Block B, Room 202"},
        {"name": "Dr. A. Singh", "subject": "Operating Systems", "email": "a.singh@college.edu", "phone": "9001111115", "cabin": "Block C, Room 301"},
        {"name": "Prof. L. Nair", "subject": "Computer Networks", "email": "l.nair@college.edu", "phone": "9001111116", "cabin": "Block C, Room 302"},
        {"name": "Dr. K. Patel", "subject": "Web Technologies", "email": "k.patel@college.edu", "phone": "9001111117", "cabin": "Block D, Room 401"},
    ]
    db.faculty.insert_many(faculty)

    # --- STUDENTS ---
    students = [
        {
            "reg_no": "STU001", 
            "name": "Arjun Mehta", 
            "phone": "9876543210", 
            "parent_phone": "9876543211", 
            "cgpa": 8.2, 
            "backlogs": 0, 
            "attendance_pct": 85.5, 
            "course_status": "Active", 
            "year": 3, 
            "branch": "CSE", 
            "class_advisor": "Dr. R. Sharma", 
            "advisor_phone": "9001111111",
            "personal_info": {
                "first_name": "Arjun",
                "last_name": "Mehta",
                "email": "arjun.mehta@college.edu",
                "phone": "9876543210"
            },
            "academic": {
                "branch": "CSE",
                "year": 3,
                "semester": 6,
                "section": "A",
                "cgpa": 8.2,
                "backlogs": 0,
                "course_status": "Active"
            }
        },
        {
            "reg_no": "STU002", 
            "name": "Priya Sharma", 
            "phone": "9823456789", 
            "parent_phone": "9823456780", 
            "cgpa": 7.5, 
            "backlogs": 1, 
            "attendance_pct": 72.3, 
            "course_status": "Active", 
            "year": 2, 
            "branch": "ECE", 
            "class_advisor": "Prof. S. Kumar", 
            "advisor_phone": "9001111112",
            "personal_info": {
                "first_name": "Priya",
                "last_name": "Sharma",
                "email": "priya.sharma@college.edu",
                "phone": "9823456789"
            },
            "academic": {
                "branch": "ECE",
                "year": 2,
                "semester": 4,
                "section": "A",
                "cgpa": 7.5,
                "backlogs": 1,
                "course_status": "Active"
            }
        },
        {
            "reg_no": "STU003", 
            "name": "Rahul Verma", 
            "phone": "9812345678", 
            "parent_phone": "9812345670", 
            "cgpa": 6.8, 
            "backlogs": 2, 
            "attendance_pct": 68.0, 
            "course_status": "Active", 
            "year": 3, 
            "branch": "MECH", 
            "class_advisor": "Dr. P. Reddy", 
            "advisor_phone": "9001111113",
            "personal_info": {
                "first_name": "Rahul",
                "last_name": "Verma",
                "email": "rahul.verma@college.edu",
                "phone": "9812345678"
            },
            "academic": {
                "branch": "MECH",
                "year": 3,
                "semester": 6,
                "section": "B",
                "cgpa": 6.8,
                "backlogs": 2,
                "course_status": "Active"
            }
        },
        {
            "reg_no": "STU004", 
            "name": "Sneha Patel", 
            "phone": "9898765432", 
            "parent_phone": "9898765430", 
            "cgpa": 9.1, 
            "backlogs": 0, 
            "attendance_pct": 92.0, 
            "course_status": "Active", 
            "year": 4, 
            "branch": "CSE", 
            "class_advisor": "Prof. M. Rao", 
            "advisor_phone": "9001111114",
            "personal_info": {
                "first_name": "Sneha",
                "last_name": "Patel",
                "email": "sneha.patel@college.edu",
                "phone": "9898765432"
            },
            "academic": {
                "branch": "CSE",
                "year": 4,
                "semester": 8,
                "section": "A",
                "cgpa": 9.1,
                "backlogs": 0,
                "course_status": "Active"
            }
        },
        {
            "reg_no": "STU005", 
            "name": "Vikram Nair", 
            "phone": "9945678901", 
            "parent_phone": "9945678900", 
            "cgpa": 5.9, 
            "backlogs": 3, 
            "attendance_pct": 60.5, 
            "course_status": "At Risk", 
            "year": 2, 
            "branch": "IT", 
            "class_advisor": "Dr. A. Singh", 
            "advisor_phone": "9001111115",
            "personal_info": {
                "first_name": "Vikram",
                "last_name": "Nair",
                "email": "vikram.nair@college.edu",
                "phone": "9945678901"
            },
            "academic": {
                "branch": "IT",
                "year": 2,
                "semester": 4,
                "section": "A",
                "cgpa": 5.9,
                "backlogs": 3,
                "course_status": "At Risk"
            }
        },
    ]
    db.students.insert_many(students)

    # --- PARENTS ---
    parents = [
        {"student_reg_no": "STU001", "name": "Suresh Mehta", "phone": "9876543211", "is_verified": True},
        {"student_reg_no": "STU002", "name": "Ravi Sharma", "phone": "9823456780", "is_verified": True},
        {"student_reg_no": "STU003", "name": "Anil Verma", "phone": "9812345670", "is_verified": True},
        {"student_reg_no": "STU004", "name": "Hitesh Patel", "phone": "9898765430", "is_verified": True},
        {"student_reg_no": "STU005", "name": "Mohan Nair", "phone": "9945678900", "is_verified": True},
    ]
    db.parents.insert_many(parents)

    # --- ACADEMIC DATA ---
    subjects_by_sem = {
        1: [("Engineering Mathematics I", 78, 88), ("Engineering Physics", 65, 75), ("C Programming", 82, 90), ("Engineering Graphics", 70, 80)],
        2: [("Engineering Mathematics II", 80, 85), ("Engineering Chemistry", 72, 78), ("Data Structures", 88, 92), ("Digital Electronics", 75, 82)],
        3: [("DBMS", 85, 90), ("Operating Systems", 79, 85), ("Computer Networks", 81, 87), ("Web Technologies", 90, 95)],
    }

    academic_records = []
    for student in students:
        reg_no = student["reg_no"]
        year = student["year"]
        sems = list(range(1, min(year * 2, 5)))
        for sem in sems:
            sem_subjects = subjects_by_sem.get(sem, subjects_by_sem[3])
            for subj, base_marks, base_att in sem_subjects:
                var_m = random.randint(-15, 10)
                var_a = random.uniform(-10, 8)
                marks = max(30, min(100, base_marks + var_m))
                att = max(50, min(100, base_att + var_a))
                backlog = 1 if marks < 40 else 0
                grade = "O" if marks >= 90 else "A+" if marks >= 80 else "A" if marks >= 70 else "B" if marks >= 60 else "C" if marks >= 50 else "F"
                academic_records.append({
                    "student_reg_no": reg_no,
                    "semester": sem,
                    "subject": subj,
                    "marks": marks,
                    "max_marks": 100,
                    "attendance_pct": round(att, 1),
                    "backlog_status": backlog,
                    "grade": grade
                })
    db.academic_data.insert_many(academic_records)

    # --- FEES ---
    fee_data = [
        ("STU001", [(1, 25000, 25000, "Paid", "2022-07-15"), (2, 25000, 25000, "Paid", "2023-01-10"), (3, 25000, 20000, "Partial", None)]),
        ("STU002", [(1, 25000, 25000, "Paid", "2022-07-12"), (2, 25000, 5000, "Partial", None)]),
        ("STU003", [(1, 25000, 25000, "Paid", "2022-07-20"), (2, 25000, 25000, "Paid", "2023-01-15"), (3, 25000, 0, "Pending", None)]),
        ("STU004", [(1, 25000, 25000, "Paid", "2022-07-10"), (2, 25000, 25000, "Paid", "2023-01-08"), (3, 25000, 25000, "Paid", "2023-07-11"), (4, 25000, 0, "Pending", None)]),
        ("STU005", [(1, 25000, 25000, "Paid", "2022-07-18"), (2, 25000, 10000, "Partial", None)]),
    ]
    fee_records = []
    for reg_no, sem_fees in fee_data:
        for sem, due, paid, status, date in sem_fees:
            schol = 5000 if reg_no == "STU004" else 0
            fee_records.append({
                "student_reg_no": reg_no,
                "semester": sem,
                "amount_due": due,
                "amount_paid": paid,
                "status": status,
                "payment_date": date,
                "scholarship_amount": schol
            })
    db.fees.insert_many(fee_records)

    # --- NOTIFICATIONS ---
    notifs = [
        {"student_reg_no": "STU001", "title": "Mid-Sem Exam", "message": "Mid-semester exams start from 15th March 2025.", "date": "2025-03-01", "category": "Exam", "is_read": False},
        {"student_reg_no": "STU001", "title": "Fee Reminder", "message": "Semester 3 fee balance of ₹5000 is due by 31st March.", "date": "2025-02-15", "category": "Finance", "is_read": False},
        {"student_reg_no": "STU001", "title": "Assignment Due", "message": "DBMS Lab Assignment due on 10th March.", "date": "2025-03-05", "category": "Academic", "is_read": False},
        {"student_reg_no": "STU002", "title": "Low Attendance Alert", "message": "Your attendance in Physics is below 75%. Please attend classes.", "date": "2025-03-02", "category": "Attendance", "is_read": False},
        {"student_reg_no": "STU002", "title": "Fee Reminder", "message": "Semester 2 fee balance pending. Contact accounts office.", "date": "2025-02-20", "category": "Finance", "is_read": False},
        {"student_reg_no": "STU003", "title": "Backlog Notice", "message": "You have 2 backlogs. Please apply for supplementary exams.", "date": "2025-03-01", "category": "Academic", "is_read": False},
        {"student_reg_no": "STU003", "title": "Fee Due", "message": "Semester 3 fee of ₹25000 is due immediately.", "date": "2025-02-28", "category": "Finance", "is_read": False},
        {"student_reg_no": "STU004", "title": "Scholarship Credited", "message": "Merit scholarship of ₹5000 credited for Sem 4.", "date": "2025-03-10", "category": "Finance", "is_read": False},
        {"student_reg_no": "STU004", "title": "Academic Excellence", "message": "Congratulations! Ranked 1st in department this semester.", "date": "2025-03-08", "category": "Academic", "is_read": False},
        {"student_reg_no": "STU005", "title": "Academic Warning", "message": "GPA below 6.0. Please meet your class advisor immediately.", "date": "2025-03-05", "category": "Academic", "is_read": False},
        {"student_reg_no": "STU005", "title": "Attendance Critical", "message": "Overall attendance 60.5% — risk of detainment.", "date": "2025-03-01", "category": "Attendance", "is_read": False},
    ]
    db.notifications.insert_many(notifs)

    client.close()
    print("✅ MongoDB initialized with sample data!")

if __name__ == "__main__":
    init_db()
