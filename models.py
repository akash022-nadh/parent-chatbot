from datetime import datetime
from pymongo import MongoClient
import os

# MongoDB Connection String
# Use environment variable or default to local MongoDB
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.environ.get("DB_NAME", "school_chatbot")

# MongoDB Client
def get_db():
    client = MongoClient(MONGO_URI)
    return client[DB_NAME]

def get_student(reg_no):
    db = get_db()
    student = db.students.find_one({"reg_no": reg_no.upper()})
    return student

def get_parent(reg_no, phone):
    db = get_db()
    
    # First check parents collection (legacy/init_db parents)
    parent = db.parents.find_one({
        "student_reg_no": reg_no.upper(),
        "phone": phone
    })
    if parent:
        return parent
    
    # Also check users collection for registered parents
    user_parent = db.users.find_one({
        "role": "parent",
        "role_specific.student_reg_no": reg_no.upper(),
        "profile.phone": phone
    })
    if user_parent:
        # Return in expected format for login
        return {
            "student_reg_no": reg_no.upper(),
            "phone": phone,
            "name": f"{user_parent.get('profile', {}).get('first_name', '')} {user_parent.get('profile', {}).get('last_name', '')}".strip(),
            "relationship": user_parent.get('role_specific', {}).get('relationship', 'Parent'),
            "from_users": True
        }
    
    return None

def save_otp(phone, otp, expiry):
    db = get_db()
    # Try to save in parents collection first
    result = db.parents.update_one(
        {"phone": phone},
        {"$set": {"otp": otp, "otp_expiry": expiry}}
    )
    # If not found in parents, try users collection (registered parents)
    if result.matched_count == 0:
        db.users.update_one(
            {"profile.phone": phone, "role": "parent"},
            {"$set": {"otp": otp, "otp_expiry": expiry}}
        )

def verify_otp(phone, otp):
    db = get_db()
    # Check parents collection first
    parent = db.parents.find_one({"phone": phone})
    if parent:
        stored_otp = parent.get("otp")
        expiry_str = parent.get("otp_expiry")
        if stored_otp != otp:
            return False
        if expiry_str and datetime.fromisoformat(expiry_str) < datetime.now():
            return False
        return True
    
    # Check users collection for registered parents
    user = db.users.find_one({"profile.phone": phone, "role": "parent"})
    if user:
        stored_otp = user.get("otp")
        expiry_str = user.get("otp_expiry")
        if stored_otp != otp:
            return False
        if expiry_str and datetime.fromisoformat(expiry_str) < datetime.now():
            return False
        return True
    
    return False

def get_attendance(reg_no):
    db = get_db()
    rows = list(db.academic_data.find(
        {"student_reg_no": reg_no.upper()},
        {"semester": 1, "subject": 1, "attendance_pct": 1, "_id": 0}
    ).sort([("semester", 1), ("subject", 1)]))
    student = db.students.find_one(
        {"reg_no": reg_no.upper()},
        {"attendance_pct": 1, "_id": 0}
    )
    return rows, student if student else {}

def get_marks(reg_no):
    db = get_db()
    rows = list(db.academic_data.find(
        {"student_reg_no": reg_no.upper()},
        {"semester": 1, "subject": 1, "marks": 1, "max_marks": 1, "grade": 1, "backlog_status": 1, "_id": 0}
    ).sort([("semester", 1), ("subject", 1)]))
    return rows

def get_backlogs(reg_no):
    db = get_db()
    rows = list(db.academic_data.find(
        {"student_reg_no": reg_no.upper(), "backlog_status": 1},
        {"semester": 1, "subject": 1, "marks": 1, "grade": 1, "_id": 0}
    ))
    return rows

def get_cgpa_history(reg_no):
    db = get_db()
    pipeline = [
        {"$match": {"student_reg_no": reg_no.upper()}},
        {"$group": {
            "_id": "$semester",
            "sem_gpa": {"$avg": {"$divide": [{"$toDouble": "$marks"}, 10]}}
        }},
        {"$sort": {"_id": 1}},
        {"$project": {"semester": "$_id", "sem_gpa": 1, "_id": 0}}
    ]
    rows = list(db.academic_data.aggregate(pipeline))
    student = db.students.find_one(
        {"reg_no": reg_no.upper()},
        {"cgpa": 1, "_id": 0}
    )
    return rows, student if student else {}

def get_fees(reg_no):
    db = get_db()
    rows = list(db.fees.find(
        {"student_reg_no": reg_no.upper()},
        {"semester": 1, "amount_due": 1, "amount_paid": 1, "status": 1, 
         "payment_date": 1, "scholarship_amount": 1, "_id": 0}
    ).sort("semester", 1))
    return rows

def get_notifications(reg_no):
    db = get_db()
    rows = list(db.notifications.find(
        {"student_reg_no": reg_no.upper()},
        {"title": 1, "message": 1, "date": 1, "category": 1, "is_read": 1, "_id": 0}
    ).sort("date", -1))
    return rows

def get_faculty_contacts():
    db = get_db()
    rows = list(db.faculty.find(
        {},
        {"name": 1, "subject": 1, "email": 1, "phone": 1, "cabin": 1, "_id": 0}
    ))
    return rows

def get_student_full(reg_no):
    db = get_db()
    student = db.students.find_one({"reg_no": reg_no.upper()})
    return student

def get_current_semester(reg_no):
    db = get_db()
    result = db.academic_data.find_one(
        {"student_reg_no": reg_no.upper()},
        sort=[("semester", -1)]
    )
    return result.get("semester", 1) if result else 1
