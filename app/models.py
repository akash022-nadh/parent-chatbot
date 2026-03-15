"""
Database Models for Student Academic Monitoring System
MongoDB collections using PyMongo
"""

from bson import ObjectId
from datetime import datetime
from pymongo import MongoClient, ASCENDING, DESCENDING
from flask import current_app
import os

class Database:
    """MongoDB Database connection singleton"""
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance.client = None
            cls._instance.db = None
        return cls._instance
    
    def connect(self):
        """Connect to MongoDB"""
        if self.client is None:
            mongo_uri = os.getenv('MONGO_URI', 'mongodb://localhost:27017/')
            db_name = os.getenv('DB_NAME', 'school_chatbot')
            
            self.client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
            self.db = self.client[db_name]
            
            # Create indexes
            self._create_indexes()
        
        return self.db
    
    def _create_indexes(self):
        """Create database indexes for optimal performance"""
        # Users collection indexes
        self.db.users.create_index("username", unique=True)
        self.db.users.create_index("email", unique=True)
        self.db.users.create_index("role")
        self.db.users.create_index("role_specific.student_reg_no")
        
        # Students collection indexes
        self.db.students.create_index("reg_no", unique=True)
        self.db.students.create_index("academic.branch")
        self.db.students.create_index("academic.year")
        self.db.students.create_index("advisor.faculty_id")
        
        # Attendance collection indexes
        self.db.attendance.create_index([("student_reg_no", ASCENDING), 
                                          ("subject_code", ASCENDING), 
                                          ("semester", ASCENDING)], unique=True)
        self.db.attendance.create_index("summary.status")
        
        # Marks collection indexes
        self.db.marks.create_index([("student_reg_no", ASCENDING), 
                                     ("subject_code", ASCENDING), 
                                     ("semester", ASCENDING), 
                                     ("exam_type", ASCENDING)], unique=True)
        self.db.marks.create_index("backlog_status")
        
        # CGPA records indexes
        self.db.cgpa_records.create_index([("student_reg_no", ASCENDING), 
                                            ("semester", ASCENDING)], unique=True)
        
        # Fees collection indexes
        self.db.fees.create_index([("student_reg_no", ASCENDING), 
                                    ("semester", ASCENDING)], unique=True)
        self.db.fees.create_index("summary.status")
        
        # Faculty collection indexes
        self.db.faculty.create_index("employee_id", unique=True)
        self.db.faculty.create_index("department")
        self.db.faculty.create_index("is_advisor")
        
        # Notifications collection indexes
        self.db.notifications.create_index("category")
        self.db.notifications.create_index("priority")
        self.db.notifications.create_index("status")
        self.db.notifications.create_index("schedule.publish_at")
        
        # Subjects collection indexes
        self.db.subjects.create_index("code", unique=True)
        self.db.subjects.create_index("department")
        self.db.subjects.create_index("semester")
    
    def close(self):
        """Close database connection"""
        if self.client:
            self.client.close()
            self.client = None
            self.db = None


# Database instance
db = Database()


def get_db():
    """Get database instance"""
    return db.connect()


# Model Classes for type hints and validation

class UserModel:
    """User model operations"""
    
    @staticmethod
    def create_user(user_data):
        """Create new user"""
        user_data['created_at'] = datetime.utcnow()
        user_data['updated_at'] = datetime.utcnow()
        user_data['is_active'] = True
        user_data['is_verified'] = False
        
        result = get_db().users.insert_one(user_data)
        return str(result.inserted_id)
    
    @staticmethod
    def find_by_username(username):
        """Find user by username"""
        return get_db().users.find_one({"username": username})
    
    @staticmethod
    def find_by_email(email):
        """Find user by email"""
        return get_db().users.find_one({"email": email})
    
    @staticmethod
    def find_by_id(user_id):
        """Find user by ID"""
        return get_db().users.find_one({"_id": ObjectId(user_id)})
    
    @staticmethod
    def find_by_role(role, skip=0, limit=20):
        """Find users by role"""
        return list(get_db().users.find(
            {"role": role, "is_active": True}
        ).skip(skip).limit(limit))
    
    @staticmethod
    def update_user(user_id, update_data):
        """Update user"""
        update_data['updated_at'] = datetime.utcnow()
        return get_db().users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )
    
    @staticmethod
    def delete_user(user_id):
        """Soft delete user"""
        return get_db().users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
        )
    
    @staticmethod
    def update_last_login(user_id):
        """Update last login timestamp"""
        return get_db().users.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"last_login": datetime.utcnow(), "updated_at": datetime.utcnow()}}
        )
    
    @staticmethod
    def store_otp(username, otp_code, expiry_minutes=5):
        """Store OTP for user"""
        from datetime import timedelta
        expiry = datetime.utcnow() + timedelta(minutes=expiry_minutes)
        
        return get_db().users.update_one(
            {"username": username},
            {"$set": {
                "otp": {
                    "code": otp_code,
                    "expiry": expiry,
                    "attempts": 0
                },
                "updated_at": datetime.utcnow()
            }}
        )
    
    @staticmethod
    def verify_otp(username, otp_code):
        """Verify OTP for user"""
        user = get_db().users.find_one({"username": username})
        
        if not user or 'otp' not in user:
            return False, "OTP not found"
        
        otp_data = user['otp']
        
        # Check expiry
        if datetime.utcnow() > otp_data['expiry']:
            return False, "OTP expired"
        
        # Check attempts
        if otp_data.get('attempts', 0) >= 3:
            return False, "Too many attempts"
        
        # Verify code
        if otp_data['code'] != otp_code:
            # Increment attempts
            get_db().users.update_one(
                {"username": username},
                {"$inc": {"otp.attempts": 1}}
            )
            return False, "Invalid OTP"
        
        # Clear OTP after successful verification
        get_db().users.update_one(
            {"username": username},
            {"$unset": {"otp": 1}, "$set": {"is_verified": True}}
        )
        
        return True, "OTP verified"


class StudentModel:
    """Student model operations"""
    
    @staticmethod
    def create_student(student_data):
        """Create new student"""
        student_data['created_at'] = datetime.utcnow()
        student_data['updated_at'] = datetime.utcnow()
        student_data['academic']['course_status'] = 'Active'
        
        result = get_db().students.insert_one(student_data)
        return str(result.inserted_id)
    
    @staticmethod
    def find_by_reg_no(reg_no):
        """Find student by registration number"""
        return get_db().students.find_one({"reg_no": reg_no})
    
    @staticmethod
    def find_by_id(student_id):
        """Find student by ID"""
        return get_db().students.find_one({"_id": ObjectId(student_id)})
    
    @staticmethod
    def get_all_students(filters=None, skip=0, limit=20, sort_by='reg_no'):
        """Get all students with filters"""
        query = filters or {}
        
        return list(get_db().students.find(query).skip(skip).limit(limit).sort(sort_by, ASCENDING))
    
    @staticmethod
    def count_students(filters=None):
        """Count students with filters"""
        query = filters or {}
        return get_db().students.count_documents(query)
    
    @staticmethod
    def update_student(reg_no, update_data):
        """Update student"""
        update_data['updated_at'] = datetime.utcnow()
        return get_db().students.update_one(
            {"reg_no": reg_no},
            {"$set": update_data}
        )
    
    @staticmethod
    def update_cgpa(reg_no, cgpa):
        """Update student CGPA"""
        return get_db().students.update_one(
            {"reg_no": reg_no},
            {"$set": {"academic.cgpa": cgpa, "updated_at": datetime.utcnow()}}
        )
    
    @staticmethod
    def update_backlogs(reg_no, backlog_count):
        """Update student backlogs"""
        return get_db().students.update_one(
            {"reg_no": reg_no},
            {"$set": {"academic.backlogs": backlog_count, "updated_at": datetime.utcnow()}}
        )
    
    @staticmethod
    def get_students_by_advisor(faculty_id):
        """Get students assigned to advisor"""
        return list(get_db().students.find({"advisor.faculty_id": ObjectId(faculty_id)}))
    
    @staticmethod
    def get_students_by_branch_year(branch, year):
        """Get students by branch and year"""
        return list(get_db().students.find(
            {"academic.branch": branch, "academic.year": year}
        ))


class AttendanceModel:
    """Attendance model operations"""
    
    @staticmethod
    def get_attendance(student_reg_no, subject_code=None, semester=None):
        """Get attendance records"""
        query = {"student_reg_no": student_reg_no}
        
        if subject_code:
            query["subject_code"] = subject_code
        if semester:
            query["semester"] = semester
            
        if subject_code and semester:
            return get_db().attendance.find_one(query)
        else:
            return list(get_db().attendance.find(query))
    
    @staticmethod
    def mark_attendance(attendance_data):
        """Mark attendance for a student"""
        # Update or create attendance record
        result = get_db().attendance.update_one(
            {
                "student_reg_no": attendance_data['student_reg_no'],
                "subject_code": attendance_data['subject_code'],
                "semester": attendance_data['semester']
            },
            {
                "$push": {"records": attendance_data['record']},
                "$set": {
                    "updated_at": datetime.utcnow(),
                    "summary": attendance_data.get('summary', {})
                }
            },
            upsert=True
        )
        return result
    
    @staticmethod
    def get_low_attendance(threshold=75.0):
        """Get students with low attendance"""
        return list(get_db().attendance.find(
            {"summary.percentage": {"$lt": threshold}}
        ))
    
    @staticmethod
    def get_attendance_summary(student_reg_no, semester=None):
        """Get attendance summary"""
        query = {"student_reg_no": student_reg_no}
        if semester:
            query["semester"] = semester
            
        pipeline = [
            {"$match": query},
            {
                "$group": {
                    "_id": "$student_reg_no",
                    "overall_attendance": {"$avg": "$summary.percentage"},
                    "subjects": {
                        "$push": {
                            "subject": "$subject_name",
                            "percentage": "$summary.percentage",
                            "status": "$summary.status"
                        }
                    }
                }
            }
        ]
        
        result = list(get_db().attendance.aggregate(pipeline))
        return result[0] if result else None


class MarksModel:
    """Marks model operations"""
    
    @staticmethod
    def get_marks(student_reg_no, subject_code=None, semester=None):
        """Get marks records"""
        query = {"student_reg_no": student_reg_no}
        
        if subject_code:
            query["subject_code"] = subject_code
        if semester:
            query["semester"] = semester
            
        if subject_code and semester:
            return get_db().marks.find_one(query)
        else:
            return list(get_db().marks.find(query))
    
    @staticmethod
    def upload_marks(marks_data):
        """Upload marks for students"""
        marks_data['uploaded_at'] = datetime.utcnow()
        marks_data['created_at'] = datetime.utcnow()
        marks_data['updated_at'] = datetime.utcnow()
        
        result = get_db().marks.update_one(
            {
                "student_reg_no": marks_data['student_reg_no'],
                "subject_code": marks_data['subject_code'],
                "semester": marks_data['semester'],
                "exam_type": marks_data['exam_type']
            },
            {"$set": marks_data},
            upsert=True
        )
        return result
    
    @staticmethod
    def get_backlogs(student_reg_no):
        """Get backlog subjects"""
        return list(get_db().marks.find({
            "student_reg_no": student_reg_no,
            "backlog_status": True
        }))
    
    @staticmethod
    def get_top_performers(subject_code=None, limit=10):
        """Get top performing students"""
        query = {"total.result": "pass"}
        if subject_code:
            query["subject_code"] = subject_code
            
        return list(get_db().marks.find(query)
                   .sort("total.percentage", DESCENDING)
                   .limit(limit))


class CGPAModel:
    """CGPA model operations"""
    
    @staticmethod
    def get_cgpa_records(student_reg_no):
        """Get CGPA records for student"""
        return list(get_db().cgpa_records.find(
            {"student_reg_no": student_reg_no}
        ).sort("semester", ASCENDING))
    
    @staticmethod
    def get_current_cgpa(student_reg_no):
        """Get current CGPA"""
        record = get_db().cgpa_records.find_one(
            {"student_reg_no": student_reg_no},
            sort=[("semester", DESCENDING)]
        )
        return record['cumulative']['cgpa'] if record else 0.0
    
    @staticmethod
    def save_semester_result(result_data):
        """Save semester result"""
        result_data['created_at'] = datetime.utcnow()
        result_data['updated_at'] = datetime.utcnow()
        
        result = get_db().cgpa_records.update_one(
            {
                "student_reg_no": result_data['student_reg_no'],
                "semester": result_data['semester']
            },
            {"$set": result_data},
            upsert=True
        )
        
        # Update student CGPA
        StudentModel.update_cgpa(
            result_data['student_reg_no'],
            result_data['cumulative']['cgpa']
        )
        
        return result
    
    @staticmethod
    def get_class_toppers(semester, branch=None, limit=10):
        """Get class toppers"""
        query = {"semester": semester}
        if branch:
            # Need to join with students collection
            pipeline = [
                {"$match": query},
                {
                    "$lookup": {
                        "from": "students",
                        "localField": "student_reg_no",
                        "foreignField": "reg_no",
                        "as": "student"
                    }
                },
                {"$match": {"student.academic.branch": branch}},
                {"$sort": {"cumulative.cgpa": -1}},
                {"$limit": limit}
            ]
            return list(get_db().cgpa_records.aggregate(pipeline))
        else:
            return list(get_db().cgpa_records.find(query)
                       .sort("cumulative.cgpa", DESCENDING)
                       .limit(limit))


class FeesModel:
    """Fees model operations"""
    
    @staticmethod
    def get_fees(student_reg_no, semester=None):
        """Get fee records"""
        query = {"student_reg_no": student_reg_no}
        if semester:
            query["semester"] = semester
            return get_db().fees.find_one(query)
        else:
            return list(get_db().fees.find(query).sort("semester", ASCENDING))
    
    @staticmethod
    def record_payment(student_reg_no, semester, payment_data):
        """Record fee payment"""
        payment_data['date'] = datetime.utcnow()
        
        result = get_db().fees.update_one(
            {
                "student_reg_no": student_reg_no,
                "semester": semester
            },
            {
                "$push": {"payments": payment_data},
                "$set": {"updated_at": datetime.utcnow()}
            }
        )
        return result
    
    @staticmethod
    def get_pending_fees():
        """Get all pending fee records"""
        return list(get_db().fees.find({
            "summary.status": {"$in": ["pending", "partial", "overdue"]}
        }))
    
    @staticmethod
    def get_defaulters_list(threshold_days=30):
        """Get fee defaulters"""
        from datetime import timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=threshold_days)
        
        return list(get_db().fees.find({
            "summary.status": {"$in": ["pending", "overdue"]},
            "created_at": {"$lt": cutoff_date}
        }))


class FacultyModel:
    """Faculty model operations"""
    
    @staticmethod
    def create_faculty(faculty_data):
        """Create new faculty"""
        faculty_data['created_at'] = datetime.utcnow()
        faculty_data['updated_at'] = datetime.utcnow()
        faculty_data['is_active'] = True
        
        result = get_db().faculty.insert_one(faculty_data)
        return str(result.inserted_id)
    
    @staticmethod
    def find_by_employee_id(employee_id):
        """Find faculty by employee ID"""
        return get_db().faculty.find_one({"employee_id": employee_id})
    
    @staticmethod
    def find_by_id(faculty_id):
        """Find faculty by ID"""
        return get_db().faculty.find_one({"_id": ObjectId(faculty_id)})
    
    @staticmethod
    def get_all_faculty(department=None, is_advisor=None):
        """Get all faculty with filters"""
        query = {"is_active": True}
        
        if department:
            query["department"] = department
        if is_advisor is not None:
            query["is_advisor"] = is_advisor
            
        return list(get_db().faculty.find(query))
    
    @staticmethod
    def get_advisors():
        """Get all advisors"""
        return list(get_db().faculty.find({"is_advisor": True, "is_active": True}))
    
    @staticmethod
    def update_faculty(faculty_id, update_data):
        """Update faculty"""
        update_data['updated_at'] = datetime.utcnow()
        return get_db().faculty.update_one(
            {"_id": ObjectId(faculty_id)},
            {"$set": update_data}
        )


class NotificationModel:
    """Notification model operations"""
    
    @staticmethod
    def create_notification(notification_data):
        """Create new notification"""
        notification_data['created_at'] = datetime.utcnow()
        notification_data['updated_at'] = datetime.utcnow()
        notification_data['status'] = 'active'
        notification_data['acknowledgments'] = []
        
        result = get_db().notifications.insert_one(notification_data)
        return str(result.inserted_id)
    
    @staticmethod
    def get_notifications(user_role=None, category=None, priority=None, limit=50):
        """Get notifications with filters"""
        query = {"status": "active"}
        
        if user_role:
            query["target.roles"] = user_role
        if category:
            query["category"] = category
        if priority:
            query["priority"] = priority
            
        return list(get_db().notifications.find(query)
                   .sort("created_at", DESCENDING)
                   .limit(limit))
    
    @staticmethod
    def get_notifications_for_student(reg_no, limit=20):
        """Get notifications for specific student"""
        # Get student details
        student = StudentModel.find_by_reg_no(reg_no)
        if not student:
            return []
        
        query = {
            "status": "active",
            "$or": [
                {"target.type": "all"},
                {"target.specific_users": reg_no},
                {
                    "target.roles": "student",
                    "target.branches": student['academic']['branch'],
                    "target.years": student['academic']['year']
                }
            ]
        }
        
        return list(get_db().notifications.find(query)
                   .sort("created_at", DESCENDING)
                   .limit(limit))
    
    @staticmethod
    def acknowledge_notification(notification_id, user_id):
        """Acknowledge notification"""
        return get_db().notifications.update_one(
            {"_id": ObjectId(notification_id)},
            {
                "$push": {
                    "acknowledgments": {
                        "user_id": ObjectId(user_id),
                        "acknowledged_at": datetime.utcnow()
                    }
                },
                "$set": {"updated_at": datetime.utcnow()}
            }
        )


class SubjectModel:
    """Subject model operations"""
    
    @staticmethod
    def create_subject(subject_data):
        """Create new subject"""
        subject_data['created_at'] = datetime.utcnow()
        subject_data['updated_at'] = datetime.utcnow()
        subject_data['is_active'] = True
        
        result = get_db().subjects.insert_one(subject_data)
        return str(result.inserted_id)
    
    @staticmethod
    def find_by_code(code):
        """Find subject by code"""
        return get_db().subjects.find_one({"code": code})
    
    @staticmethod
    def get_subjects(department=None, semester=None, is_active=True):
        """Get subjects with filters"""
        query = {"is_active": is_active}
        
        if department:
            query["department"] = department
        if semester:
            query["semester"] = semester
            
        return list(get_db().subjects.find(query))
    
    @staticmethod
    def update_subject(subject_id, update_data):
        """Update subject"""
        update_data['updated_at'] = datetime.utcnow()
        return get_db().subjects.update_one(
            {"_id": ObjectId(subject_id)},
            {"$set": update_data}
        )


# Utility functions
def get_collection_stats():
    """Get collection statistics"""
    db = get_db()
    stats = {}
    
    collections = [
        'users', 'students', 'attendance', 'marks', 'cgpa_records',
        'fees', 'faculty', 'notifications', 'subjects'
    ]
    
    for collection in collections:
        stats[collection] = db[collection].count_documents({})
    
    return stats


def generate_unique_id(prefix=''):
    """Generate unique ID with optional prefix"""
    import uuid
    unique = str(uuid.uuid4())[:8].upper()
    return f"{prefix}{unique}" if prefix else unique
