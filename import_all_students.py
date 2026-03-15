"""
Import all 50 students from CSV into MongoDB
Run: python import_all_students.py
"""

import csv
import os
from pymongo import MongoClient
from models import MONGO_URI, DB_NAME
import random

def get_grade(grade_point):
    """Convert grade point to letter grade"""
    if grade_point >= 9:
        return 'O'
    elif grade_point >= 8:
        return 'A+'
    elif grade_point >= 7:
        return 'A'
    elif grade_point >= 6:
        return 'B'
    elif grade_point >= 5:
        return 'C'
    elif grade_point >= 4:
        return 'D'
    else:
        return 'F'

def get_class_advisor(year, section='A'):
    """Get class advisor details based on year"""
    advisors = {
        1: {'name': 'Dr. A. Kumar', 'email': 'a.kumar@college.edu', 'phone': '9876501234', 'cabin': 'Block A, Room 101'},
        2: {'name': 'Prof. S. Reddy', 'email': 's.reddy@college.edu', 'phone': '9876501235', 'cabin': 'Block B, Room 201'},
        3: {'name': 'Prof. V. Reddy', 'email': 'venkat.reddy@college.edu', 'phone': '9876501238', 'cabin': 'Block B, Room 205'},
        4: {'name': 'Dr. R. Sharma', 'email': 'r.sharma@college.edu', 'phone': '9876501236', 'cabin': 'Block C, Room 301'},
    }
    return advisors.get(year, advisors[1])

def generate_fee_data(student):
    """Generate fee data for each semester"""
    fees = []
    scholarship_per_sem = student.get('scholarship_amount', 0) // 6 if student.get('scholarship_status') == 'Yes' else 0
    
    for sem in range(1, student['year'] * 2 + 1):
        base_fee = 25000
        amount_due = max(0, base_fee - scholarship_per_sem)
        
        # Simulate payment status
        if student.get('status') == 'At Risk':
            paid = random.randint(0, int(amount_due * 0.7))
        else:
            paid = random.randint(int(amount_due * 0.8), amount_due)
        
        status = 'Paid' if paid >= amount_due else ('Partial' if paid > 0 else 'Pending')
        
        fees.append({
            'semester': sem,
            'amount_due': amount_due,
            'amount_paid': paid,
            'status': status,
            'payment_date': f"202{2 + (sem-1)//2}-{(sem % 2) * 6 + 1:02d}-{random.randint(10, 28):02d}",
            'scholarship_amount': scholarship_per_sem
        })
    return fees

def import_students():
    """Import all students from CSV into MongoDB"""
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    
    # Clear existing data
    print("Clearing existing data...")
    db.students.delete_many({})
    db.marks.delete_many({})
    db.attendance.delete_many({})
    db.fees.delete_many({})
    db.parents.delete_many({})
    
    # Read CSV file
    csv_path = os.path.join(os.path.dirname(__file__), 'student_data.csv')
    
    students = {}
    
    print("Reading student data...")
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            reg_no = row['Reg_No']
            
            if reg_no not in students:
                students[reg_no] = {
                    'reg_no': reg_no,
                    'name': row['Student'],
                    'parent_phone': row['Parent_Phone'],
                    'phone': row['Parent_Phone'],
                    'status': row['Status'],
                    'total_backlogs': int(row['Total_Backlogs']),
                    'year': int(row['Year']),
                    'branch': 'CSE',
                    'section': 'A',
                    'scholarship_status': row['Scholarship_Status'],
                    'scholarship_amount': int(row['Scholarship_Amount']) if row['Scholarship_Amount'].isdigit() else 0,
                    'marks_data': [],
                    'attendance_data': [],
                    'sem_cgpa': {},
                    'year_cgpa': {}
                }
            
            semester = int(row['Semester'])
            marks = int(row['Marks'])
            grade_point = float(row['Grade_Point'])
            backlog = row['Backlog']
            backlog_type = row['Backlog_Type'] if backlog == 'Yes' else None
            
            # Add marks
            students[reg_no]['marks_data'].append({
                'semester': semester,
                'subject': row['Subject'],
                'marks': marks,
                'max_marks': 100,
                'grade': get_grade(grade_point),
                'grade_point': grade_point,
                'backlog_status': 1 if backlog == 'Yes' else 0,
                'backlog_type': backlog_type
            })
            
            # Add attendance
            students[reg_no]['attendance_data'].append({
                'semester': semester,
                'subject': row['Subject'],
                'attendance_pct': float(row['Attendance_%'])
            })
            
            # Track CGPAs
            students[reg_no]['sem_cgpa'][semester] = float(row['Semester_CGPA'])
            students[reg_no]['year_cgpa'][int(row['Year'])] = float(row['Year_Overall_CGPA'])
    
    # Insert into database
    print(f"Importing {len(students)} students...")
    
    total_marks = 0
    total_attendance = 0
    total_fees = 0
    
    for reg_no, student in students.items():
        # Calculate average attendance
        avg_attendance = sum(a['attendance_pct'] for a in student['attendance_data']) / len(student['attendance_data'])
        
        # Get overall CGPA (latest year)
        overall_cgpa = list(student['year_cgpa'].values())[-1] if student['year_cgpa'] else 0
        
        # Get class advisor
        advisor = get_class_advisor(student['year'])
        
        # Insert student record
        student_record = {
            'reg_no': reg_no,
            'name': student['name'],
            'phone': student['phone'],
            'parent_phone': student['parent_phone'],
            'cgpa': overall_cgpa,
            'backlogs': student['total_backlogs'],
            'attendance_pct': round(avg_attendance, 1),
            'course_status': student['status'],
            'year': student['year'],
            'branch': student['branch'],
            'section': student['section'],
            'class_advisor': advisor['name'],
            'advisor_phone': advisor['phone'],
            'advisor_email': advisor['email'],
            'advisor_cabin': advisor['cabin'],
            'scholarship_status': student['scholarship_status'],
            'scholarship_amount': student['scholarship_amount']
        }
        db.students.insert_one(student_record)
        
        # Insert marks
        for mark in student['marks_data']:
            mark['reg_no'] = reg_no
            db.marks.insert_one(mark)
            total_marks += 1
        
        # Insert attendance
        for att in student['attendance_data']:
            att['reg_no'] = reg_no
            db.attendance.insert_one(att)
            total_attendance += 1
        
        # Generate and insert fees
        fee_data = generate_fee_data(student)
        for fee in fee_data:
            fee['reg_no'] = reg_no
            db.fees.insert_one(fee)
            total_fees += 1
        
        # Create parent record
        parent_record = {
            'phone': student['parent_phone'],
            'student_reg_no': reg_no,
            'student_name': student['name'],
            'relationship': 'Parent/Guardian'
        }
        db.parents.insert_one(parent_record)
    
    client.close()
    
    print(f"\n✅ Successfully imported {len(students)} students!")
    print(f"   📊 Students: {len(students)}")
    print(f"   📝 Marks records: {total_marks}")
    print(f"   📅 Attendance records: {total_attendance}")
    print(f"   💰 Fee records: {total_fees}")
    print(f"   👨‍👩‍👧 Parent records: {len(students)}")
    
    return len(students)

if __name__ == "__main__":
    import_students()
