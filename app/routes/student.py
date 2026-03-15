"""
Student Routes
Endpoints for students to view their own academic information
"""

from flask import Blueprint, request, jsonify
from bson import ObjectId
from datetime import datetime
from app.models import (
    StudentModel, AttendanceModel, MarksModel, CGPAModel,
    FeesModel, NotificationModel
)
from app.utils.decorators import student_required, check_student_access
from app.utils.helpers import format_currency, time_ago, get_attendance_status

student_bp = Blueprint('student', __name__)


@student_bp.route('/dashboard', methods=['GET'])
@student_required
def get_dashboard(current_user):
    """Get student dashboard"""
    reg_no = current_user.get('role_specific', {}).get('student_reg_no')
    
    if not reg_no:
        return jsonify({
            'success': False,
            'message': 'Student registration number not found'
        }), 400
    
    student = StudentModel.find_by_reg_no(reg_no)
    if not student:
        return jsonify({
            'success': False,
            'message': 'Student record not found'
        }), 404
    
    # Get attendance summary
    attendance_records = AttendanceModel.get_attendance(reg_no)
    attendance_summary = calculate_overall_attendance(attendance_records)
    
    # Get current CGPA
    current_cgpa = CGPAModel.get_current_cgpa(reg_no)
    
    # Get notifications
    notifications = NotificationModel.get_notifications_for_student(reg_no, limit=5)
    
    # Get upcoming exams (from notifications)
    upcoming_exams = [n for n in notifications if n.get('category') == 'exam']
    
    dashboard_data = {
        'success': True,
        'profile': {
            'reg_no': student.get('reg_no'),
            'name': f"{student.get('personal_info', {}).get('first_name', '')} "
                    f"{student.get('personal_info', {}).get('last_name', '')}".strip(),
            'branch': student.get('academic', {}).get('branch'),
            'year': student.get('academic', {}).get('year'),
            'semester': student.get('academic', {}).get('semester'),
            'section': student.get('academic', {}).get('section'),
            'cgpa': current_cgpa,
            'backlogs': student.get('academic', {}).get('backlogs', 0),
            'roll_no': student.get('roll_no')
        },
        'attendance_summary': attendance_summary,
        'quick_stats': {
            'cgpa': current_cgpa,
            'attendance': attendance_summary.get('overall_percentage', 0),
            'backlogs': student.get('academic', {}).get('backlogs', 0),
            'semester': student.get('academic', {}).get('semester')
        },
        'notifications': format_notifications(notifications),
        'upcoming_exams': format_notifications(upcoming_exams),
        'advisor': student.get('advisor', {})
    }
    
    return jsonify(dashboard_data), 200


@student_bp.route('/profile', methods=['GET'])
@student_required
def get_profile(current_user):
    """Get student profile"""
    reg_no = current_user.get('role_specific', {}).get('student_reg_no')
    
    student = StudentModel.find_by_reg_no(reg_no)
    if not student:
        return jsonify({
            'success': False,
            'message': 'Student not found'
        }), 404
    
    profile_data = {
        'id': str(student['_id']),
        'reg_no': student.get('reg_no'),
        'roll_no': student.get('roll_no'),
        'personal_info': student.get('personal_info'),
        'academic': student.get('academic'),
        'contact': student.get('contact'),
        'family': student.get('family'),
        'admission': student.get('admission'),
        'advisor': student.get('advisor'),
        'created_at': student.get('created_at')
    }
    
    return jsonify({
        'success': True,
        'profile': profile_data
    }), 200


@student_bp.route('/profile', methods=['PUT'])
@student_required
def update_profile(current_user):
    """Update student profile (limited fields)"""
    reg_no = current_user.get('role_specific', {}).get('student_reg_no')
    data = request.get_json()
    
    # Students can only update limited fields
    allowed_updates = {}
    
    if 'contact' in data:
        allowed_updates['contact'] = data['contact']
    if 'address' in data:
        allowed_updates['contact.address'] = data['address']
    if 'phone' in data:
        allowed_updates['personal_info.phone'] = data['phone']
    if 'email' in data:
        allowed_updates['personal_info.email'] = data['email']
    
    if allowed_updates:
        result = StudentModel.update_student(reg_no, allowed_updates)
        
        return jsonify({
            'success': True,
            'message': 'Profile updated successfully',
            'modified_count': result.modified_count
        }), 200
    
    return jsonify({
        'success': False,
        'message': 'No valid fields to update'
    }), 400


@student_bp.route('/attendance', methods=['GET'])
@student_required
def get_attendance(current_user):
    """Get own attendance"""
    reg_no = current_user.get('role_specific', {}).get('student_reg_no')
    semester = request.args.get('semester', type=int)
    
    attendance_records = AttendanceModel.get_attendance(reg_no, semester=semester)
    
    if not attendance_records:
        return jsonify({
            'success': True,
            'attendance': [],
            'message': 'No attendance records found'
        }), 200
    
    if not isinstance(attendance_records, list):
        attendance_records = [attendance_records]
    
    # Format attendance data
    formatted_attendance = []
    overall_total = 0
    overall_present = 0
    
    for record in attendance_records:
        summary = record.get('summary', {})
        formatted_attendance.append({
            'subject_code': record.get('subject_code'),
            'subject_name': record.get('subject_name'),
            'semester': record.get('semester'),
            'total_classes': summary.get('total_classes', 0),
            'attended': summary.get('attended', 0),
            'absent': summary.get('absent', 0),
            'late': summary.get('late', 0),
            'percentage': summary.get('percentage', 0),
            'status': summary.get('status', 'unknown'),
            'records': record.get('records', [])[-10:]  # Last 10 records
        })
        
        overall_total += summary.get('total_classes', 0)
        overall_present += summary.get('attended', 0)
    
    overall_percentage = (overall_present / overall_total * 100) if overall_total > 0 else 0
    
    # Get attendance trend
    monthly_trend = calculate_attendance_trend(attendance_records)
    
    return jsonify({
        'success': True,
        'overall': {
            'total_classes': overall_total,
            'attended': overall_present,
            'percentage': round(overall_percentage, 2),
            'status': get_attendance_status(overall_percentage)
        },
        'subject_wise': formatted_attendance,
        'monthly_trend': monthly_trend,
        'deficit': max(0, 75 - overall_percentage)
    }), 200


@student_bp.route('/marks', methods=['GET'])
@student_required
def get_marks(current_user):
    """Get own marks"""
    reg_no = current_user.get('role_specific', {}).get('student_reg_no')
    semester = request.args.get('semester', type=int)
    
    marks_records = MarksModel.get_marks(reg_no, semester=semester)
    
    if not marks_records:
        return jsonify({
            'success': True,
            'marks': [],
            'message': 'No marks records found'
        }), 200
    
    if not isinstance(marks_records, list):
        marks_records = [marks_records]
    
    # Get CGPA records
    cgpa_records = CGPAModel.get_cgpa_records(reg_no)
    
    # Format marks data
    formatted_marks = []
    for record in marks_records:
        total = record.get('total', {})
        formatted_marks.append({
            'subject_code': record.get('subject_code'),
            'subject_name': record.get('subject_name'),
            'semester': record.get('semester'),
            'internal_marks': record.get('components', {}).get('internal', {}).get('marks'),
            'external_marks': record.get('components', {}).get('external', {}).get('marks'),
            'total_marks': total.get('marks'),
            'max_marks': total.get('max_marks'),
            'percentage': total.get('percentage'),
            'grade': total.get('grade'),
            'result': total.get('result'),
            'backlog_status': record.get('backlog_status', False)
        })
    
    current_cgpa = CGPAModel.get_current_cgpa(reg_no)
    
    return jsonify({
        'success': True,
        'current_cgpa': current_cgpa,
        'semester_wise_sgpa': [
            {
                'semester': r.get('semester'),
                'sgpa': r.get('sgpa'),
                'credits': r.get('credits_earned'),
                'class_rank': r.get('class_rank')
            }
            for r in cgpa_records
        ],
        'subject_wise': formatted_marks
    }), 200


@student_bp.route('/results', methods=['GET'])
@student_required
def get_results(current_user):
    """Get complete results with analytics"""
    reg_no = current_user.get('role_specific', {}).get('student_reg_no')
    
    marks_records = MarksModel.get_marks(reg_no)
    cgpa_records = CGPAModel.get_cgpa_records(reg_no)
    
    if not marks_records:
        marks_records = []
    
    if not isinstance(marks_records, list):
        marks_records = [marks_records]
    
    # Calculate analytics
    total_subjects = len(marks_records)
    passed = len([m for m in marks_records if m.get('total', {}).get('result') == 'pass'])
    failed = total_subjects - passed
    
    percentages = [m.get('total', {}).get('percentage', 0) for m in marks_records]
    average_percentage = sum(percentages) / len(percentages) if percentages else 0
    
    highest_mark = max(percentages) if percentages else 0
    lowest_mark = min(percentages) if percentages else 0
    
    # Get grade distribution
    grade_distribution = {}
    for mark in marks_records:
        grade = mark.get('total', {}).get('grade', 'F')
        grade_distribution[grade] = grade_distribution.get(grade, 0) + 1
    
    return jsonify({
        'success': True,
        'summary': {
            'total_subjects': total_subjects,
            'passed': passed,
            'failed': failed,
            'backlogs': len([m for m in marks_records if m.get('backlog_status')]),
            'average_percentage': round(average_percentage, 2),
            'highest_percentage': highest_mark,
            'lowest_percentage': lowest_mark,
            'current_cgpa': CGPAModel.get_current_cgpa(reg_no)
        },
        'cgpa_history': [
            {
                'semester': r.get('semester'),
                'sgpa': r.get('sgpa'),
                'cgpa': r.get('cumulative', {}).get('cgpa'),
                'class_rank': r.get('class_rank'),
                'credits': r.get('credits_earned')
            }
            for r in cgpa_records
        ],
        'grade_distribution': grade_distribution,
        'semester_results': group_marks_by_semester(marks_records)
    }), 200


@student_bp.route('/fees', methods=['GET'])
@student_required
def get_fees(current_user):
    """Get own fee status"""
    reg_no = current_user.get('role_specific', {}).get('student_reg_no')
    
    fees_records = FeesModel.get_fees(reg_no)
    
    if not fees_records:
        return jsonify({
            'success': True,
            'fees': [],
            'message': 'No fee records found'
        }), 200
    
    if not isinstance(fees_records, list):
        fees_records = [fees_records]
    
    # Format fees data
    formatted_fees = []
    total_paid = 0
    total_pending = 0
    
    for record in fees_records:
        summary = record.get('summary', {})
        
        formatted_record = {
            'semester': record.get('semester'),
            'academic_year': record.get('academic_year'),
            'total_due': summary.get('total_due'),
            'total_paid': summary.get('total_paid'),
            'pending': summary.get('pending'),
            'status': summary.get('status'),
            'due_date': record.get('summary', {}).get('due_date'),
            'payments': [
                {
                    'receipt_no': p.get('receipt_no'),
                    'amount': p.get('amount'),
                    'date': p.get('date'),
                    'mode': p.get('mode'),
                    'status': p.get('status')
                }
                for p in record.get('payments', [])
            ]
        }
        
        formatted_fees.append(formatted_record)
        total_paid += summary.get('total_paid', 0)
        total_pending += summary.get('pending', 0)
    
    # Check scholarship
    scholarship_info = None
    for record in fees_records:
        if record.get('scholarship', {}).get('eligible'):
            scholarship_info = record.get('scholarship')
            break
    
    return jsonify({
        'success': True,
        'summary': {
            'total_paid': total_paid,
            'total_pending': total_pending,
            'formatted_total_paid': format_currency(total_paid),
            'formatted_total_pending': format_currency(total_pending)
        },
        'semester_wise': formatted_fees,
        'scholarship': scholarship_info
    }), 200


@student_bp.route('/notifications', methods=['GET'])
@student_required
def get_notifications(current_user):
    """Get notifications for student"""
    reg_no = current_user.get('role_specific', {}).get('student_reg_no')
    limit = min(int(request.args.get('limit', 20)), 50)
    
    notifications = NotificationModel.get_notifications_for_student(reg_no, limit)
    
    formatted_notifications = []
    for notif in notifications:
        formatted_notifications.append({
            'id': str(notif.get('_id')),
            'title': notif.get('title'),
            'message': notif.get('message'),
            'category': notif.get('category'),
            'priority': notif.get('priority'),
            'posted_at': notif.get('created_at'),
            'time_ago': time_ago(notif.get('created_at', datetime.utcnow())),
            'attachments': notif.get('attachments', [])
        })
    
    return jsonify({
        'success': True,
        'notifications': formatted_notifications,
        'count': len(formatted_notifications)
    }), 200


@student_bp.route('/timetable', methods=['GET'])
@student_required
def get_timetable(current_user):
    """Get class timetable"""
    reg_no = current_user.get('role_specific', {}).get('student_reg_no')
    
    student = StudentModel.find_by_reg_no(reg_no)
    if not student:
        return jsonify({
            'success': False,
            'message': 'Student not found'
        }), 404
    
    # This would typically come from a timetable collection
    # For now, return a sample structure
    branch = student.get('academic', {}).get('branch')
    year = student.get('academic', {}).get('year')
    section = student.get('academic', {}).get('section')
    
    return jsonify({
        'success': True,
        'timetable': {
            'branch': branch,
            'year': year,
            'section': section,
            'days': ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],
            'schedule': []  # Would be populated from database
        },
        'message': 'Timetable feature implementation in progress'
    }), 200


# Helper functions

def calculate_overall_attendance(attendance_records):
    """Calculate overall attendance from records"""
    if not attendance_records:
        return {
            'overall_percentage': 0,
            'subjects_count': 0,
            'status': 'no_data'
        }
    
    if not isinstance(attendance_records, list):
        attendance_records = [attendance_records]
    
    total_classes = 0
    total_attended = 0
    
    for record in attendance_records:
        summary = record.get('summary', {})
        total_classes += summary.get('total_classes', 0)
        total_attended += summary.get('attended', 0)
    
    percentage = (total_attended / total_classes * 100) if total_classes > 0 else 0
    
    return {
        'overall_percentage': round(percentage, 2),
        'subjects_count': len(attendance_records),
        'status': get_attendance_status(percentage)
    }


def calculate_attendance_trend(attendance_records):
    """Calculate monthly attendance trend"""
    # Group records by month and calculate average
    monthly_data = {}
    
    for record in attendance_records:
        for rec in record.get('records', []):
            date = rec.get('date')
            if isinstance(date, datetime):
                month_key = date.strftime('%Y-%m')
                
                if month_key not in monthly_data:
                    monthly_data[month_key] = {'total': 0, 'present': 0}
                
                monthly_data[month_key]['total'] += 1
                if rec.get('status') == 'present':
                    monthly_data[month_key]['present'] += 1
    
    trend = []
    for month, data in sorted(monthly_data.items()):
        percentage = (data['present'] / data['total'] * 100) if data['total'] > 0 else 0
        trend.append({
            'month': month,
            'percentage': round(percentage, 2),
            'classes': data['total']
        })
    
    return trend


def format_notifications(notifications):
    """Format notifications for display"""
    formatted = []
    for notif in notifications:
        formatted.append({
            'id': str(notif.get('_id')),
            'title': notif.get('title'),
            'message': notif.get('message'),
            'category': notif.get('category'),
            'time_ago': time_ago(notif.get('created_at', datetime.utcnow()))
        })
    return formatted


def group_marks_by_semester(marks_records):
    """Group marks by semester"""
    grouped = {}
    
    for mark in marks_records:
        semester = mark.get('semester')
        if semester not in grouped:
            grouped[semester] = []
        
        total = mark.get('total', {})
        grouped[semester].append({
            'subject_code': mark.get('subject_code'),
            'subject_name': mark.get('subject_name'),
            'marks': total.get('marks'),
            'max_marks': total.get('max_marks'),
            'percentage': total.get('percentage'),
            'grade': total.get('grade'),
            'result': total.get('result')
        })
    
    # Sort by semester
    return [
        {
            'semester': sem,
            'subjects': grouped[sem]
        }
        for sem in sorted(grouped.keys())
    ]
