"""
Faculty Routes
Endpoints for faculty members to manage attendance, marks, and view student data
"""

from flask import Blueprint, request, jsonify
from bson import ObjectId
from datetime import datetime
from app.models import (
    StudentModel, FacultyModel, AttendanceModel, 
    MarksModel, CGPAModel, UserModel
)
from app.utils.decorators import faculty_required, validate_json
from app.utils.helpers import format_date, get_attendance_status, calculate_percentage

faculty_bp = Blueprint('faculty', __name__)


@faculty_bp.route('/dashboard', methods=['GET'])
@faculty_required
def get_dashboard(current_user):
    """Get faculty dashboard data"""
    faculty_id = current_user.get('role_specific', {}).get('employee_id')
    faculty = FacultyModel.find_by_id(current_user.get('_id'))
    
    if not faculty:
        return jsonify({
            'success': False,
            'message': 'Faculty record not found'
        }), 404
    
    # Get assigned students
    assigned_students = StudentModel.get_students_by_advisor(current_user.get('_id'))
    
    # Get students in assigned sections
    section_students = []
    for section in faculty.get('assigned_sections', []):
        students = StudentModel.get_students_by_branch_year(
            faculty.get('department'), 
            section.get('year')
        )
        section_students.extend(students)
    
    # Get low attendance alerts
    low_attendance = []
    for student in section_students[:50]:  # Limit to first 50
        reg_no = student.get('reg_no')
        attendance = AttendanceModel.get_attendance(reg_no)
        
        if isinstance(attendance, list):
            for att in attendance:
                if att.get('summary', {}).get('percentage', 0) < 75:
                    low_attendance.append({
                        'reg_no': reg_no,
                        'name': f"{student.get('personal_info', {}).get('first_name', '')} "
                                f"{student.get('personal_info', {}).get('last_name', '')}".strip(),
                        'subject': att.get('subject_name'),
                        'attendance': att.get('summary', {}).get('percentage')
                    })
    
    dashboard_data = {
        'success': True,
        'faculty': {
            'id': str(faculty['_id']),
            'employee_id': faculty.get('employee_id'),
            'name': f"{faculty.get('personal_info', {}).get('first_name', '')} "
                    f"{faculty.get('personal_info', {}).get('last_name', '')}".strip(),
            'department': faculty.get('department'),
            'designation': faculty.get('designation'),
            'is_advisor': faculty.get('is_advisor', False)
        },
        'statistics': {
            'advisor_students': len(assigned_students),
            'section_students': len(section_students),
            'subjects_handled': len(faculty.get('subjects', [])),
            'low_attendance_alerts': len(low_attendance)
        },
        'assigned_sections': faculty.get('assigned_sections', []),
        'subjects': faculty.get('subjects', []),
        'alerts': {
            'low_attendance': low_attendance[:10]  # Top 10 alerts
        }
    }
    
    return jsonify(dashboard_data), 200


@faculty_bp.route('/students', methods=['GET'])
@faculty_required
def get_students(current_user):
    """Get students assigned to faculty"""
    faculty_id = current_user.get('_id')
    faculty = FacultyModel.find_by_id(faculty_id)
    
    if not faculty:
        return jsonify({
            'success': False,
            'message': 'Faculty record not found'
        }), 404
    
    # Get advisor students
    advisor_students = StudentModel.get_students_by_advisor(faculty_id)
    
    # Get section students
    section_students = []
    for section in faculty.get('assigned_sections', []):
        students = StudentModel.get_students_by_branch_year(
            faculty.get('department'),
            section.get('year')
        )
        section_students.extend(students)
    
    # Combine and remove duplicates
    all_students = {s['reg_no']: s for s in advisor_students + section_students}
    
    formatted_students = []
    for reg_no, student in all_students.items():
        formatted_students.append({
            'id': str(student['_id']),
            'reg_no': student.get('reg_no'),
            'name': f"{student.get('personal_info', {}).get('first_name', '')} "
                    f"{student.get('personal_info', {}).get('last_name', '')}".strip(),
            'roll_no': student.get('roll_no'),
            'branch': student.get('academic', {}).get('branch'),
            'year': student.get('academic', {}).get('year'),
            'section': student.get('academic', {}).get('section'),
            'cgpa': student.get('academic', {}).get('cgpa'),
            'is_advisee': any(s['reg_no'] == reg_no for s in advisor_students)
        })
    
    return jsonify({
        'success': True,
        'students': formatted_students,
        'count': len(formatted_students)
    }), 200


@faculty_bp.route('/student/<reg_no>', methods=['GET'])
@faculty_required
def get_student_details(current_user, reg_no):
    """Get detailed student information"""
    student = StudentModel.find_by_reg_no(reg_no.upper())
    
    if not student:
        return jsonify({
            'success': False,
            'message': 'Student not found'
        }), 404
    
    # Check if faculty has access to this student
    faculty = FacultyModel.find_by_id(current_user.get('_id'))
    
    # Faculty can access if:
    # 1. They are the advisor
    # 2. They teach a subject to the student's section
    has_access = False
    
    if str(student.get('advisor', {}).get('faculty_id')) == str(current_user.get('_id')):
        has_access = True
    
    if not has_access:
        for section in faculty.get('assigned_sections', []):
            if (section.get('year') == student.get('academic', {}).get('year') and
                student.get('academic', {}).get('branch') == faculty.get('department')):
                has_access = True
                break
    
    if not has_access:
        return jsonify({
            'success': False,
            'message': 'You do not have access to this student\'s data'
        }), 403
    
    # Get student data
    attendance = AttendanceModel.get_attendance(reg_no)
    marks = MarksModel.get_marks(reg_no)
    cgpa_records = CGPAModel.get_cgpa_records(reg_no)
    
    student_data = {
        'id': str(student['_id']),
        'reg_no': student.get('reg_no'),
        'personal_info': {
            'first_name': student.get('personal_info', {}).get('first_name'),
            'last_name': student.get('personal_info', {}).get('last_name'),
            'email': student.get('personal_info', {}).get('email'),
            'phone': student.get('personal_info', {}).get('phone')
        },
        'academic': student.get('academic'),
        'attendance': attendance if isinstance(attendance, list) else [attendance] if attendance else [],
        'marks': marks if isinstance(marks, list) else [marks] if marks else [],
        'cgpa_history': cgpa_records
    }
    
    return jsonify({
        'success': True,
        'student': student_data
    }), 200


@faculty_bp.route('/attendance/mark', methods=['POST'])
@faculty_required
@validate_json(['subject_code', 'date', 'attendance'])
def mark_attendance(current_user):
    """Mark attendance for students"""
    data = request.get_json()
    
    subject_code = data.get('subject_code')
    date_str = data.get('date')
    attendance_list = data.get('attendance', [])
    semester = data.get('semester')
    
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d')
    except ValueError:
        return jsonify({
            'success': False,
            'message': 'Invalid date format. Use YYYY-MM-DD'
        }), 400
    
    results = []
    for att in attendance_list:
        reg_no = att.get('reg_no')
        status = att.get('status')  # present, absent, late
        
        student = StudentModel.find_by_reg_no(reg_no)
        if not student:
            results.append({
                'reg_no': reg_no,
                'status': 'error',
                'message': 'Student not found'
            })
            continue
        
        attendance_record = {
            'student_reg_no': reg_no,
            'subject_code': subject_code,
            'semester': semester or student.get('academic', {}).get('semester'),
            'record': {
                'date': date,
                'status': status,
                'period': att.get('period', 1),
                'marked_by': current_user.get('_id'),
                'marked_at': datetime.utcnow(),
                'remarks': att.get('remarks', '')
            }
        }
        
        result = AttendanceModel.mark_attendance(attendance_record)
        results.append({
            'reg_no': reg_no,
            'status': 'success' if result.modified_count or result.upserted_id else 'unchanged'
        })
    
    return jsonify({
        'success': True,
        'message': f'Attendance marked for {len([r for r in results if r["status"] == "success"])} students',
        'results': results
    }), 200


@faculty_bp.route('/attendance/subject/<subject_code>', methods=['GET'])
@faculty_required
def get_subject_attendance(current_user, subject_code):
    """Get attendance for a specific subject"""
    semester = request.args.get('semester', type=int)
    
    # Get all students for this subject
    faculty = FacultyModel.find_by_id(current_user.get('_id'))
    
    # Find which year/section this subject belongs to
    subject_info = None
    for subj in faculty.get('subjects', []):
        if subj.get('code') == subject_code:
            subject_info = subj
            break
    
    if not subject_info:
        return jsonify({
            'success': False,
            'message': 'Subject not found or you do not teach this subject'
        }), 403
    
    # Get students
    students = []
    for year in subject_info.get('semester', []):
        students.extend(StudentModel.get_students_by_branch_year(
            faculty.get('department'), year
        ))
    
    # Get attendance for each student
    attendance_data = []
    for student in students:
        reg_no = student.get('reg_no')
        attendance = AttendanceModel.get_attendance(reg_no, subject_code, semester)
        
        attendance_data.append({
            'reg_no': reg_no,
            'name': f"{student.get('personal_info', {}).get('first_name', '')} "
                    f"{student.get('personal_info', {}).get('last_name', '')}".strip(),
            'roll_no': student.get('roll_no'),
            'attendance': attendance
        })
    
    return jsonify({
        'success': True,
        'subject': subject_code,
        'semester': semester,
        'attendance': attendance_data,
        'count': len(attendance_data)
    }), 200


@faculty_bp.route('/marks/upload', methods=['POST'])
@faculty_required
@validate_json(['subject_code', 'exam_type', 'marks'])
def upload_marks(current_user):
    """Upload marks for students"""
    data = request.get_json()
    
    subject_code = data.get('subject_code')
    exam_type = data.get('exam_type')  # mid1, mid2, assignment, external
    semester = data.get('semester')
    marks_list = data.get('marks', [])
    
    results = []
    for mark_data in marks_list:
        reg_no = mark_data.get('reg_no')
        marks = mark_data.get('marks')
        max_marks = mark_data.get('max_marks', 100)
        
        student = StudentModel.find_by_reg_no(reg_no)
        if not student:
            results.append({
                'reg_no': reg_no,
                'status': 'error',
                'message': 'Student not found'
            })
            continue
        
        # Calculate grade
        percentage = calculate_percentage(marks, max_marks)
        grade = get_grade_from_percentage(percentage)
        
        marks_record = {
            'student_reg_no': reg_no,
            'subject_code': subject_code,
            'subject_name': mark_data.get('subject_name', ''),
            'semester': semester or student.get('academic', {}).get('semester'),
            'academic_year': data.get('academic_year'),
            'exam_type': exam_type,
            'components': {
                'internal' if exam_type in ['mid1', 'mid2', 'assignment'] else 'external': {
                    'marks': marks,
                    'max_marks': max_marks,
                    'percentage': percentage
                }
            },
            'total': {
                'marks': marks,
                'max_marks': max_marks,
                'percentage': percentage,
                'grade': grade,
                'grade_point': get_grade_point(grade),
                'result': 'pass' if percentage >= 40 else 'fail'
            },
            'backlog_status': percentage < 40,
            'uploaded_by': current_user.get('_id')
        }
        
        result = MarksModel.upload_marks(marks_record)
        results.append({
            'reg_no': reg_no,
            'status': 'success' if result.modified_count or result.upserted_id else 'unchanged'
        })
    
    return jsonify({
        'success': True,
        'message': f'Marks uploaded for {len([r for r in results if r["status"] == "success"])} students',
        'results': results
    }), 200


@faculty_bp.route('/marks/subject/<subject_code>', methods=['GET'])
@faculty_required
def get_subject_marks(current_user, subject_code):
    """Get marks for a specific subject"""
    semester = request.args.get('semester', type=int)
    exam_type = request.args.get('exam_type')
    
    # Get faculty info
    faculty = FacultyModel.find_by_id(current_user.get('_id'))
    
    # Get all marks for this subject
    # This would need to aggregate across all students
    # For now, return a placeholder response
    
    return jsonify({
        'success': True,
        'subject': subject_code,
        'semester': semester,
        'exam_type': exam_type,
        'marks': [],  # Would be populated from database
        'message': 'Feature implementation in progress'
    }), 200


def get_grade_from_percentage(percentage):
    """Get grade from percentage"""
    if percentage >= 90:
        return 'A+'
    elif percentage >= 80:
        return 'A'
    elif percentage >= 70:
        return 'B'
    elif percentage >= 60:
        return 'C'
    elif percentage >= 50:
        return 'D'
    elif percentage >= 40:
        return 'E'
    else:
        return 'F'


def get_grade_point(grade):
    """Get grade point from grade"""
    points = {
        'A+': 10, 'A': 9, 'B': 8, 'C': 7,
        'D': 6, 'E': 5, 'F': 0
    }
    return points.get(grade, 0)
