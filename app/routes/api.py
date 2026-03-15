"""
API Routes - REST API Endpoints for Common Operations
"""

from flask import Blueprint, request, jsonify
from bson import ObjectId
from datetime import datetime
from app.models import (
    StudentModel, AttendanceModel, MarksModel, CGPAModel,
    FeesModel, NotificationModel, FacultyModel, get_collection_stats
)
from app.services import (
    AcademicService, AttendanceService, PerformanceService,
    FeeService, ReportService
)
from app.utils.decorators import any_role_required, validate_query_params
from app.utils.helpers import (
    format_currency, format_date, get_current_academic_year,
    get_branch_full_name, get_semester_name
)

api_bp = Blueprint('api', __name__)


@api_bp.route('/stats', methods=['GET'])
@any_role_required
def get_system_stats(current_user):
    """Get system-wide statistics"""
    stats = get_collection_stats()
    
    return jsonify({
        'success': True,
        'stats': stats
    }), 200


@api_bp.route('/academic-year', methods=['GET'])
def get_academic_year():
    """Get current academic year information"""
    current_year = get_current_academic_year()
    
    return jsonify({
        'success': True,
        'current_academic_year': current_year,
        'current_semester': 'Odd' if datetime.now().month >= 7 else 'Even'
    }), 200


@api_bp.route('/branches', methods=['GET'])
def get_branches():
    """Get list of branches/departments"""
    branches = [
        {'code': 'CSE', 'name': 'Computer Science and Engineering'},
        {'code': 'ECE', 'name': 'Electronics and Communication Engineering'},
        {'code': 'EEE', 'name': 'Electrical and Electronics Engineering'},
        {'code': 'ME', 'name': 'Mechanical Engineering'},
        {'code': 'CE', 'name': 'Civil Engineering'},
        {'code': 'IT', 'name': 'Information Technology'},
        {'code': 'AI', 'name': 'Artificial Intelligence'},
        {'code': 'DS', 'name': 'Data Science'},
        {'code': 'CY', 'name': 'Cyber Security'}
    ]
    
    return jsonify({
        'success': True,
        'branches': branches
    }), 200


@api_bp.route('/search', methods=['GET'])
@any_role_required
@validate_query_params(allowed_params=['q', 'type', 'limit'])
def search(current_user):
    """Search students, faculty, or courses"""
    query = request.args.get('q', '').strip()
    search_type = request.args.get('type', 'all')  # student, faculty, course, all
    limit = min(int(request.args.get('limit', 20)), 50)
    
    if not query:
        return jsonify({
            'success': False,
            'message': 'Search query is required'
        }), 400
    
    results = {
        'students': [],
        'faculty': [],
        'courses': []
    }
    
    # Search students
    if search_type in ['all', 'student']:
        # Simple search by name or reg_no
        students = list(StudentModel.get_all_students({}, 0, limit))
        for student in students:
            name = f"{student.get('personal_info', {}).get('first_name', '')} {student.get('personal_info', {}).get('last_name', '')}".strip()
            reg_no = student.get('reg_no', '')
            
            if query.lower() in name.lower() or query.upper() in reg_no.upper():
                results['students'].append({
                    'id': str(student['_id']),
                    'reg_no': reg_no,
                    'name': name,
                    'branch': student.get('academic', {}).get('branch'),
                    'year': student.get('academic', {}).get('year')
                })
    
    # Search faculty
    if search_type in ['all', 'faculty']:
        faculty_list = FacultyModel.get_all_faculty()
        for faculty in faculty_list:
            name = f"{faculty.get('personal_info', {}).get('first_name', '')} {faculty.get('personal_info', {}).get('last_name', '')}".strip()
            emp_id = faculty.get('employee_id', '')
            
            if query.lower() in name.lower() or query.upper() in emp_id.upper():
                results['faculty'].append({
                    'id': str(faculty['_id']),
                    'employee_id': emp_id,
                    'name': name,
                    'department': faculty.get('department'),
                    'designation': faculty.get('designation')
                })
    
    return jsonify({
        'success': True,
        'query': query,
        'results': results,
        'total': len(results['students']) + len(results['faculty'])
    }), 200


@api_bp.route('/student/<reg_no>/summary', methods=['GET'])
@any_role_required
def get_student_summary(current_user, reg_no):
    """Get quick summary for a student"""
    summary = AcademicService.get_student_academic_summary(reg_no)
    
    if not summary:
        return jsonify({
            'success': False,
            'message': 'Student not found'
        }), 404
    
    return jsonify({
        'success': True,
        'summary': summary
    }), 200


@api_bp.route('/student/<reg_no>/performance', methods=['GET'])
@any_role_required
def get_student_performance(current_user, reg_no):
    """Get detailed performance analysis"""
    analysis = PerformanceService.analyze_student_performance(reg_no)
    prediction = PerformanceService.predict_cgpa(reg_no, 0)
    
    return jsonify({
        'success': True,
        'reg_no': reg_no,
        'analysis': analysis,
        'prediction': prediction
    }), 200


@api_bp.route('/class/performance', methods=['GET'])
@any_role_required
def get_class_performance_metrics(current_user):
    """Get class performance metrics"""
    branch = request.args.get('branch')
    year = request.args.get('year', type=int)
    semester = request.args.get('semester', type=int)
    
    if not branch or not year:
        return jsonify({
            'success': False,
            'message': 'Branch and year are required'
        }), 400
    
    metrics = AcademicService.get_class_performance(branch, year, semester or (year * 2))
    
    return jsonify({
        'success': True,
        'branch': branch,
        'year': year,
        'semester': semester,
        'metrics': metrics
    }), 200


@api_bp.route('/attendance/defaulters', methods=['GET'])
@any_role_required
def get_attendance_defaulters(current_user):
    """Get attendance defaulters list"""
    threshold = request.args.get('threshold', 75.0, type=float)
    branch = request.args.get('branch')
    year = request.args.get('year', type=int)
    
    defaulters = AttendanceService.get_defaulter_list(threshold, branch, year)
    
    return jsonify({
        'success': True,
        'threshold': threshold,
        'defaulters': defaulters,
        'count': len(defaulters)
    }), 200


@api_bp.route('/fees/defaulters', methods=['GET'])
@any_role_required
def get_fee_defaulters(current_user):
    """Get fee defaulters list"""
    min_pending = request.args.get('min_pending', 1000, type=float)
    days_overdue = request.args.get('days_overdue', 30, type=int)
    
    defaulters = FeeService.get_defaulters_list(min_pending, days_overdue)
    
    return jsonify({
        'success': True,
        'defaulters': defaulters,
        'count': len(defaulters)
    }), 200


@api_bp.route('/reports/student/<reg_no>', methods=['GET'])
@any_role_required
def generate_student_report(current_user, reg_no):
    """Generate comprehensive student report"""
    report = ReportService.generate_student_report(reg_no)
    
    if not report:
        return jsonify({
            'success': False,
            'message': 'Student not found'
        }), 404
    
    return jsonify({
        'success': True,
        'report': report
    }), 200


@api_bp.route('/reports/class', methods=['GET'])
@any_role_required
def generate_class_report(current_user):
    """Generate class-level report"""
    branch = request.args.get('branch')
    year = request.args.get('year', type=int)
    semester = request.args.get('semester', type=int)
    
    if not branch or not year:
        return jsonify({
            'success': False,
            'message': 'Branch and year are required'
        }), 400
    
    report = ReportService.generate_class_report(branch, year, semester or (year * 2))
    
    return jsonify({
        'success': True,
        'report': report
    }), 200


@api_bp.route('/calendar', methods=['GET'])
def get_academic_calendar():
    """Get academic calendar"""
    year = request.args.get('year', get_current_academic_year())
    semester = request.args.get('semester', type=int)
    
    # Sample calendar data - in production, fetch from database
    calendar = {
        'academic_year': year,
        'events': [
            {
                'title': 'Semester Start',
                'date': '2025-01-01',
                'type': 'academic',
                'description': 'Classes begin'
            },
            {
                'title': 'Mid-Semester Exams',
                'date': '2025-03-15',
                'end_date': '2025-03-22',
                'type': 'exam',
                'description': 'Mid-semester examination'
            },
            {
                'title': 'End-Semester Exams',
                'date': '2025-04-20',
                'end_date': '2025-05-05',
                'type': 'exam',
                'description': 'End-semester examination'
            },
            {
                'title': 'Fee Payment Deadline',
                'date': '2025-01-31',
                'type': 'fee',
                'description': 'Last date for fee payment'
            },
            {
                'title': 'Result Declaration',
                'date': '2025-05-20',
                'type': 'academic',
                'description': 'Semester results'
            }
        ]
    }
    
    return jsonify({
        'success': True,
        'calendar': calendar
    }), 200


@api_bp.route('/faculty-contacts', methods=['GET'])
def get_faculty_contacts():
    """Get faculty contact information"""
    department = request.args.get('department')
    
    faculty_list = FacultyModel.get_all_faculty(department)
    
    contacts = []
    for faculty in faculty_list:
        contacts.append({
            'id': str(faculty['_id']),
            'employee_id': faculty.get('employee_id'),
            'name': f"{faculty.get('personal_info', {}).get('first_name', '')} "
                    f"{faculty.get('personal_info', {}).get('last_name', '')}".strip(),
            'department': faculty.get('department'),
            'designation': faculty.get('designation'),
            'email': faculty.get('contact', {}).get('email'),
            'phone': faculty.get('contact', {}).get('phone'),
            'cabin': faculty.get('contact', {}).get('cabin'),
            'office_hours': faculty.get('contact', {}).get('office_hours'),
            'is_advisor': faculty.get('is_advisor', False)
        })
    
    return jsonify({
        'success': True,
        'contacts': contacts,
        'count': len(contacts)
    }), 200


@api_bp.route('/academic-office', methods=['GET'])
def get_academic_office_contacts():
    """Get academic office contact information"""
    contacts = [
        {
            'department': 'Academic Dean',
            'contact': '040-12345678',
            'email': 'dean.academic@college.edu',
            'timing': 'Mon-Fri 9AM-5PM',
            'location': 'Block A, Ground Floor'
        },
        {
            'department': 'Examination Cell',
            'contact': '040-12345679',
            'email': 'exam@college.edu',
            'timing': 'Mon-Fri 10AM-4PM',
            'location': 'Block A, First Floor'
        },
        {
            'department': 'Student Affairs',
            'contact': '040-12345680',
            'email': 'student.affairs@college.edu',
            'timing': 'Mon-Fri 9AM-5PM',
            'location': 'Block B, Ground Floor'
        },
        {
            'department': 'Accounts Office',
            'contact': '040-12345681',
            'email': 'accounts@college.edu',
            'timing': 'Mon-Fri 9AM-4PM',
            'location': 'Block A, Ground Floor'
        },
        {
            'department': 'Admission Office',
            'contact': '040-12345682',
            'email': 'admissions@college.edu',
            'timing': 'Mon-Sat 9AM-5PM',
            'location': 'Main Building, Ground Floor'
        }
    ]
    
    return jsonify({
        'success': True,
        'contacts': contacts
    }), 200


@api_bp.route('/health', methods=['GET'])
def health_check():
    """API health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    }), 200
