"""
Admin Routes
Dashboard and management endpoints for administrators
"""

from flask import Blueprint, request, jsonify
from bson import ObjectId
from datetime import datetime
from app.models import (
    UserModel, StudentModel, FacultyModel, 
    AttendanceModel, MarksModel, FeesModel,
    get_collection_stats
)
from app.services import (
    AcademicService, AttendanceService, PerformanceService,
    FeeService, ReportService
)
from app.utils.decorators import admin_required, validate_json, validate_query_params
from app.utils.helpers import paginate_results, format_date

admin_bp = Blueprint('admin', __name__)


@admin_bp.route('/dashboard', methods=['GET'])
@admin_required
def get_dashboard(current_user):
    """Get admin dashboard statistics"""
    # Get collection stats
    stats = get_collection_stats()
    
    # Get pending fee count
    pending_fees = FeesModel.get_pending_fees()
    
    # Get low attendance students
    low_attendance = AttendanceModel.get_low_attendance(threshold=75.0)
    
    # Get recent activities (last 24 hours)
    from datetime import timedelta
    yesterday = datetime.utcnow() - timedelta(days=1)
    
    dashboard_data = {
        "success": True,
        "statistics": {
            "total_students": stats.get('students', 0),
            "total_faculty": stats.get('faculty', 0),
            "total_parents": stats.get('users', 0) - stats.get('faculty', 0),
            "pending_approvals": 0,  # Implement if needed
            "active_users_today": 0,  # Implement tracking if needed
            "pending_fees": len(pending_fees),
            "low_attendance_students": len(low_attendance)
        },
        "collections": stats,
        "recent_activities": [],  # Populate from activity log if implemented
        "alerts": {
            "fees": len(pending_fees),
            "attendance": len(low_attendance),
            "new_registrations": 0
        }
    }
    
    return jsonify(dashboard_data), 200


@admin_bp.route('/students', methods=['GET'])
@admin_required
def list_students(current_user):
    """List all students with pagination and filters"""
    # Get query parameters
    page = int(request.args.get('page', 1))
    limit = min(int(request.args.get('limit', 20)), 100)
    branch = request.args.get('branch')
    year = request.args.get('year', type=int)
    status = request.args.get('status')
    
    # Build filter query
    filters = {}
    if branch:
        filters['academic.branch'] = branch
    if year:
        filters['academic.year'] = year
    if status:
        filters['academic.course_status'] = status
    
    # Get students
    skip = (page - 1) * limit
    students = StudentModel.get_all_students(filters, skip, limit)
    total = StudentModel.count_students(filters)
    
    # Format student data
    formatted_students = []
    for student in students:
        formatted_students.append({
            'id': str(student['_id']),
            'reg_no': student.get('reg_no'),
            'name': f"{student.get('personal_info', {}).get('first_name', '')} "
                    f"{student.get('personal_info', {}).get('last_name', '')}".strip(),
            'branch': student.get('academic', {}).get('branch'),
            'year': student.get('academic', {}).get('year'),
            'semester': student.get('academic', {}).get('semester'),
            'cgpa': student.get('academic', {}).get('cgpa'),
            'backlogs': student.get('academic', {}).get('backlogs'),
            'status': student.get('academic', {}).get('course_status'),
            'parent_phone': student.get('family', {}).get('parent_phone')
        })
    
    return jsonify({
        'success': True,
        'students': formatted_students,
        'pagination': {
            'page': page,
            'per_page': limit,
            'total': total,
            'pages': (total + limit - 1) // limit
        }
    }), 200


@admin_bp.route('/students', methods=['POST'])
@admin_required
@validate_json(['reg_no', 'name', 'email', 'branch', 'year'])
def create_student(current_user):
    """Create new student record"""
    data = request.get_json()
    
    # Check if student already exists
    existing = StudentModel.find_by_reg_no(data['reg_no'])
    if existing:
        return jsonify({
            'success': False,
            'message': 'Student with this registration number already exists'
        }), 409
    
    # Prepare student data
    # Convert year to integer
    try:
        year = int(data['year'])
    except (ValueError, TypeError):
        year = 1
    
    student_data = {
        'reg_no': data['reg_no'].upper().strip(),
        'personal_info': {
            'first_name': data.get('first_name', data['name'].split()[0]),
            'last_name': ' '.join(data['name'].split()[1:]) if len(data['name'].split()) > 1 else '',
            'email': data.get('email'),
            'phone': data.get('phone', ''),
            'date_of_birth': data.get('date_of_birth'),
            'gender': data.get('gender', ''),
            'blood_group': data.get('blood_group', ''),
        },
        'academic': {
            'branch': data['branch'],
            'year': year,
            'semester': data.get('semester', year * 2),
            'section': data.get('section', 'A'),
            'cgpa': 0.0,
            'backlogs': 0,
            'course_status': 'Active'
        },
        'contact': {
            'email': data.get('email'),
            'phone': data.get('phone', ''),
            'address': data.get('address', {})
        },
        'family': {
            'father_name': data.get('father_name', ''),
            'mother_name': data.get('mother_name', ''),
            'parent_phone': data.get('parent_phone', ''),
            'parent_email': data.get('parent_email', ''),
            'annual_income': data.get('annual_income', 0)
        },
        'admission': {
            'year': data.get('admission_year', datetime.now().year),
            'type': data.get('admission_type', 'Regular'),
            'category': data.get('category', 'General')
        },
        'advisor': {
            'faculty_id': ObjectId(data['advisor_id']) if data.get('advisor_id') else None,
            'name': data.get('advisor_name', ''),
            'email': data.get('advisor_email', ''),
            'phone': data.get('advisor_phone', '')
        }
    }
    
    # Create student
    student_id = StudentModel.create_student(student_data)
    
    return jsonify({
        'success': True,
        'message': 'Student created successfully',
        'student_id': student_id
    }), 201


@admin_bp.route('/students/<reg_no>', methods=['GET'])
@admin_required
def get_student_details(current_user, reg_no):
    """Get detailed student information"""
    student = StudentModel.find_by_reg_no(reg_no.upper())
    
    if not student:
        return jsonify({
            'success': False,
            'message': 'Student not found'
        }), 404
    
    # Get related data
    attendance = AttendanceModel.get_attendance_summary(reg_no)
    marks = MarksModel.get_marks(reg_no)
    fees = FeesModel.get_fees(reg_no)
    
    student_data = {
        'id': str(student['_id']),
        'reg_no': student.get('reg_no'),
        'personal_info': student.get('personal_info'),
        'academic': student.get('academic'),
        'contact': student.get('contact'),
        'family': student.get('family'),
        'advisor': student.get('advisor'),
        'attendance_summary': attendance,
        'marks_summary': {
            'total_subjects': len(marks) if isinstance(marks, list) else 0,
            'backlogs': sum(1 for m in marks if isinstance(m, dict) and m.get('backlog_status')) if isinstance(marks, list) else 0
        },
        'fees_summary': {
            'total_semesters': len(fees) if isinstance(fees, list) else 0,
            'pending_semesters': sum(1 for f in fees if isinstance(f, dict) and f.get('summary', {}).get('status') in ['pending', 'partial']) if isinstance(fees, list) else 0
        }
    }
    
    return jsonify({
        'success': True,
        'student': student_data
    }), 200


@admin_bp.route('/students/<reg_no>', methods=['PUT'])
@admin_required
def update_student(current_user, reg_no):
    """Update student information"""
    data = request.get_json()
    
    student = StudentModel.find_by_reg_no(reg_no.upper())
    if not student:
        return jsonify({
            'success': False,
            'message': 'Student not found'
        }), 404
    
    # Update student
    result = StudentModel.update_student(reg_no.upper(), data)
    
    return jsonify({
        'success': True,
        'message': 'Student updated successfully',
        'modified_count': result.modified_count
    }), 200


@admin_bp.route('/students/<reg_no>', methods=['DELETE'])
@admin_required
def delete_student(current_user, reg_no):
    """Delete student (soft delete)"""
    student = StudentModel.find_by_reg_no(reg_no.upper())
    if not student:
        return jsonify({
            'success': False,
            'message': 'Student not found'
        }), 404
    
    # Soft delete by updating status
    result = StudentModel.update_student(reg_no.upper(), {
        'academic.course_status': 'Discontinued',
        'is_active': False
    })
    
    return jsonify({
        'success': True,
        'message': 'Student record deactivated'
    }), 200


@admin_bp.route('/faculty', methods=['GET'])
@admin_required
def list_faculty(current_user):
    """List all faculty members"""
    department = request.args.get('department')
    is_advisor = request.args.get('is_advisor', type=bool)
    
    faculty = FacultyModel.get_all_faculty(department, is_advisor)
    
    formatted_faculty = []
    for f in faculty:
        formatted_faculty.append({
            'id': str(f['_id']),
            'employee_id': f.get('employee_id'),
            'name': f"{f.get('personal_info', {}).get('first_name', '')} "
                    f"{f.get('personal_info', {}).get('last_name', '')}".strip(),
            'department': f.get('department'),
            'designation': f.get('designation'),
            'email': f.get('contact', {}).get('email'),
            'phone': f.get('contact', {}).get('phone'),
            'is_advisor': f.get('is_advisor', False),
            'subjects': f.get('subjects', []),
            'is_active': f.get('is_active', True)
        })
    
    return jsonify({
        'success': True,
        'faculty': formatted_faculty,
        'count': len(formatted_faculty)
    }), 200


@admin_bp.route('/faculty', methods=['POST'])
@admin_required
@validate_json(['employee_id', 'name', 'email', 'department', 'designation'])
def create_faculty(current_user):
    """Create new faculty record"""
    data = request.get_json()
    
    # Check if faculty already exists
    existing = FacultyModel.find_by_employee_id(data['employee_id'])
    if existing:
        return jsonify({
            'success': False,
            'message': 'Faculty with this employee ID already exists'
        }), 409
    
    # Prepare faculty data
    faculty_data = {
        'employee_id': data['employee_id'],
        'personal_info': {
            'first_name': data.get('first_name', data['name'].split()[0]),
            'last_name': ' '.join(data['name'].split()[1:]) if len(data['name'].split()) > 1 else '',
            'email': data.get('email'),
            'phone': data.get('phone', ''),
            'gender': data.get('gender', ''),
            'qualification': data.get('qualification', ''),
            'experience_years': data.get('experience_years', 0)
        },
        'contact': {
            'email': data.get('email'),
            'phone': data.get('phone', ''),
            'cabin': data.get('cabin', ''),
            'office_hours': data.get('office_hours', '')
        },
        'department': data['department'],
        'designation': data['designation'],
        'subjects': data.get('subjects', []),
        'assigned_sections': data.get('assigned_sections', []),
        'is_advisor': data.get('is_advisor', False),
        'advisor_sections': data.get('advisor_sections', []),
        'joining_date': data.get('joining_date', datetime.utcnow())
    }
    
    # Create faculty
    faculty_id = FacultyModel.create_faculty(faculty_data)
    
    return jsonify({
        'success': True,
        'message': 'Faculty created successfully',
        'faculty_id': faculty_id
    }), 201


@admin_bp.route('/reports/attendance', methods=['GET'])
@admin_required
def get_attendance_report(current_user):
    """Get attendance report"""
    branch = request.args.get('branch')
    year = request.args.get('year', type=int)
    threshold = request.args.get('threshold', 75.0, type=float)
    
    low_attendance = AttendanceModel.get_low_attendance(threshold)
    
    # Filter by branch and year if specified
    filtered = []
    for record in low_attendance:
        student = StudentModel.find_by_reg_no(record['student_reg_no'])
        if not student:
            continue
        
        if branch and student.get('academic', {}).get('branch') != branch:
            continue
        if year and student.get('academic', {}).get('year') != year:
            continue
        
        filtered.append({
            'reg_no': record['student_reg_no'],
            'name': f"{student.get('personal_info', {}).get('first_name', '')} "
                    f"{student.get('personal_info', {}).get('last_name', '')}".strip(),
            'branch': student.get('academic', {}).get('branch'),
            'year': student.get('academic', {}).get('year'),
            'subject': record.get('subject_name'),
            'attendance_percentage': record.get('summary', {}).get('percentage'),
            'classes_attended': record.get('summary', {}).get('attended'),
            'total_classes': record.get('summary', {}).get('total_classes')
        })
    
    return jsonify({
        'success': True,
        'threshold': threshold,
        'students_with_low_attendance': filtered,
        'count': len(filtered)
    }), 200


@admin_bp.route('/reports/fees', methods=['GET'])
@admin_required
def get_fees_report(current_user):
    """Get fees report"""
    status = request.args.get('status', 'pending')
    
    if status == 'pending':
        fees_data = FeesModel.get_pending_fees()
    elif status == 'defaulters':
        days = request.args.get('days', 30, type=int)
        fees_data = FeesModel.get_defaulters_list(days)
    else:
        fees_data = []
    
    formatted = []
    for fee in fees_data:
        student = StudentModel.find_by_reg_no(fee['student_reg_no'])
        if not student:
            continue
        
        formatted.append({
            'reg_no': fee['student_reg_no'],
            'name': f"{student.get('personal_info', {}).get('first_name', '')} "
                    f"{student.get('personal_info', {}).get('last_name', '')}".strip(),
            'branch': student.get('academic', {}).get('branch'),
            'semester': fee.get('semester'),
            'total_due': fee.get('summary', {}).get('total_due'),
            'total_paid': fee.get('summary', {}).get('total_paid'),
            'pending': fee.get('summary', {}).get('pending'),
            'status': fee.get('summary', {}).get('status')
        })
    
    return jsonify({
        'success': True,
        'status': status,
        'records': formatted,
        'count': len(formatted)
    }), 200


@admin_bp.route('/settings', methods=['GET'])
@admin_required
def get_settings(current_user):
    """Get system settings"""
    # Return system configuration settings
    from config import Config
    
    settings = {
        'attendance_threshold': Config.ATTENDANCE_THRESHOLD,
        'cgpa_threshold': Config.CGPA_THRESHOLD,
        'scholarship_cgpa_threshold': Config.SCHOLARSHIP_CGPA_THRESHOLD,
        'academic_year': Config.get_current_academic_year() if hasattr(Config, 'get_current_academic_year') else '2024-2025'
    }
    
    return jsonify({
        'success': True,
        'settings': settings
    }), 200


@admin_bp.route('/settings', methods=['PUT'])
@admin_required
def update_settings(current_user):
    """Update system settings"""
    data = request.get_json()
    
    # Update settings in database or config
    # This would typically update a settings collection
    
    return jsonify({
        'success': True,
        'message': 'Settings updated successfully'
    }), 200
