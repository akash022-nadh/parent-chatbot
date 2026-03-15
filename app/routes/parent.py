"""
Parent Routes
Endpoints for parents to view their child's academic information
"""

from flask import Blueprint, request, jsonify
from bson import ObjectId
from datetime import datetime
from app.models import (
    StudentModel, AttendanceModel, MarksModel, CGPAModel,
    FeesModel, NotificationModel
)
from app.utils.decorators import parent_required, check_student_access
from app.utils.helpers import format_currency, get_attendance_status, time_ago

parent_bp = Blueprint('parent', __name__)


@parent_bp.route('/dashboard', methods=['GET'])
@parent_required
def get_dashboard(current_user):
    """Get parent dashboard with child's summary"""
    reg_no = current_user.get('role_specific', {}).get('student_reg_no')
    
    if not reg_no:
        return jsonify({
            'success': False,
            'message': 'No student linked to this parent account'
        }), 400
    
    student = StudentModel.find_by_reg_no(reg_no)
    if not student:
        return jsonify({
            'success': False,
            'message': 'Student not found'
        }), 404
    
    # Get attendance summary
    attendance_records = AttendanceModel.get_attendance(reg_no)
    attendance_summary = calculate_overall_attendance(attendance_records)
    
    # Get current CGPA
    current_cgpa = CGPAModel.get_current_cgpa(reg_no)
    
    # Get fees summary
    fees_records = FeesModel.get_fees(reg_no)
    fees_summary = calculate_fees_summary(fees_records)
    
    # Get recent marks
    marks_records = MarksModel.get_marks(reg_no)
    recent_marks = get_recent_marks(marks_records, limit=5)
    
    # Get alerts
    alerts = generate_alerts(student, attendance_records, fees_records, marks_records)
    
    # Get upcoming events (from notifications)
    notifications = NotificationModel.get_notifications_for_student(reg_no, limit=5)
    
    dashboard_data = {
        'success': True,
        'student': {
            'reg_no': student.get('reg_no'),
            'name': f"{student.get('personal_info', {}).get('first_name', '')} "
                    f"{student.get('personal_info', {}).get('last_name', '')}".strip(),
            'branch': student.get('academic', {}).get('branch'),
            'year': student.get('academic', {}).get('year'),
            'semester': student.get('academic', {}).get('semester'),
            'section': student.get('academic', {}).get('section'),
            'cgpa': current_cgpa,
            'backlogs': student.get('academic', {}).get('backlogs', 0),
            'course_status': student.get('academic', {}).get('course_status')
        },
        'attendance_summary': attendance_summary,
        'fees_summary': fees_summary,
        'recent_marks': recent_marks,
        'alerts': alerts,
        'upcoming_events': format_notifications(notifications),
        'advisor': student.get('advisor', {}),
        'last_updated': datetime.utcnow().isoformat()
    }
    
    return jsonify(dashboard_data), 200


@parent_bp.route('/attendance/<reg_no>', methods=['GET'])
@parent_required
@check_student_access
def get_attendance(current_user, reg_no):
    """Get detailed attendance report"""
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
            'status': summary.get('status', 'unknown')
        })
        
        overall_total += summary.get('total_classes', 0)
        overall_present += summary.get('attended', 0)
    
    overall_percentage = (overall_present / overall_total * 100) if overall_total > 0 else 0
    
    # Get low attendance subjects
    low_attendance = [a for a in formatted_attendance if a['percentage'] < 75]
    
    return jsonify({
        'success': True,
        'overall': {
            'total_classes': overall_total,
            'attended': overall_present,
            'percentage': round(overall_percentage, 2),
            'status': get_attendance_status(overall_percentage)
        },
        'subject_wise': formatted_attendance,
        'low_attendance_alerts': low_attendance,
        'semester': semester
    }), 200


@parent_bp.route('/marks/<reg_no>', methods=['GET'])
@parent_required
@check_student_access
def get_marks(current_user, reg_no):
    """Get marks report"""
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
    backlogs = []
    strong_subjects = []
    weak_subjects = []
    
    for record in marks_records:
        total = record.get('total', {})
        formatted_mark = {
            'subject_code': record.get('subject_code'),
            'subject_name': record.get('subject_name'),
            'semester': record.get('semester'),
            'exam_type': record.get('exam_type'),
            'internal_marks': record.get('components', {}).get('internal', {}).get('marks'),
            'external_marks': record.get('components', {}).get('external', {}).get('marks'),
            'total_marks': total.get('marks'),
            'max_marks': total.get('max_marks'),
            'percentage': total.get('percentage'),
            'grade': total.get('grade'),
            'result': total.get('result'),
            'backlog_status': record.get('backlog_status', False)
        }
        
        formatted_marks.append(formatted_mark)
        
        # Categorize subjects
        if record.get('backlog_status'):
            backlogs.append(formatted_mark)
        elif total.get('percentage', 0) >= 80:
            strong_subjects.append(formatted_mark['subject_name'])
        elif total.get('percentage', 0) < 60:
            weak_subjects.append(formatted_mark['subject_name'])
    
    # Format CGPA records
    formatted_cgpa = []
    for record in cgpa_records:
        formatted_cgpa.append({
            'semester': record.get('semester'),
            'sgpa': record.get('sgpa'),
            'credits_earned': record.get('credits_earned'),
            'cumulative_cgpa': record.get('cumulative', {}).get('cgpa'),
            'class_rank': record.get('class_rank'),
            'result_status': record.get('result_status')
        })
    
    current_cgpa = CGPAModel.get_current_cgpa(reg_no)
    
    return jsonify({
        'success': True,
        'current_cgpa': current_cgpa,
        'semester_wise_cgpa': formatted_cgpa,
        'subject_wise_marks': formatted_marks,
        'backlogs': backlogs,
        'strong_subjects': strong_subjects,
        'weak_subjects': weak_subjects,
        'performance_summary': {
            'total_subjects': len(formatted_marks),
            'passed': len([m for m in formatted_marks if m['result'] == 'pass']),
            'failed': len([m for m in formatted_marks if m['result'] == 'fail']),
            'backlogs': len(backlogs)
        }
    }), 200


@parent_bp.route('/fees/<reg_no>', methods=['GET'])
@parent_required
@check_student_access
def get_fees(current_user, reg_no):
    """Get fee details"""
    semester = request.args.get('semester', type=int)
    
    fees_records = FeesModel.get_fees(reg_no, semester=semester)
    
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
        payments = record.get('payments', [])
        
        formatted_payments = []
        for payment in payments:
            formatted_payments.append({
                'receipt_no': payment.get('receipt_no'),
                'amount': payment.get('amount'),
                'mode': payment.get('mode'),
                'date': payment.get('date'),
                'status': payment.get('status')
            })
        
        formatted_record = {
            'semester': record.get('semester'),
            'academic_year': record.get('academic_year'),
            'fee_structure': record.get('fee_structure'),
            'payments': formatted_payments,
            'summary': {
                'total_due': summary.get('total_due'),
                'total_paid': summary.get('total_paid'),
                'pending': summary.get('pending'),
                'status': summary.get('status')
            },
            'scholarship': record.get('scholarship'),
            'due_date': record.get('summary', {}).get('due_date')
        }
        
        formatted_fees.append(formatted_record)
        total_paid += summary.get('total_paid', 0)
        total_pending += summary.get('pending', 0)
    
    # Get scholarship status
    scholarship_eligible = any(
        r.get('scholarship', {}).get('eligible', False) 
        for r in fees_records
    )
    
    return jsonify({
        'success': True,
        'summary': {
            'total_paid': total_paid,
            'total_pending': total_pending,
            'currency': 'INR',
            'formatted_total_paid': format_currency(total_paid),
            'formatted_total_pending': format_currency(total_pending)
        },
        'semester_wise': formatted_fees,
        'scholarship_status': {
            'eligible': scholarship_eligible,
            'message': 'Eligible for merit scholarship' if scholarship_eligible else 'Not eligible'
        }
    }), 200


@parent_bp.route('/backlogs/<reg_no>', methods=['GET'])
@parent_required
@check_student_access
def get_backlogs(current_user, reg_no):
    """Get backlog information"""
    marks_records = MarksModel.get_marks(reg_no)
    
    if not marks_records:
        marks_records = []
    
    if not isinstance(marks_records, list):
        marks_records = [marks_records]
    
    # Get backlogs
    backlogs = []
    repeated_subjects = {}
    incomplete_subjects = []
    
    for record in marks_records:
        if record.get('backlog_status'):
            subject_name = record.get('subject_name')
            
            backlog_info = {
                'subject_code': record.get('subject_code'),
                'subject_name': subject_name,
                'semester': record.get('semester'),
                'marks': record.get('total', {}).get('marks'),
                'max_marks': record.get('total', {}).get('max_marks'),
                'attempts': 1
            }
            
            # Check for repeated subjects
            if subject_name in repeated_subjects:
                repeated_subjects[subject_name]['attempts'] += 1
                repeated_subjects[subject_name]['semesters'].append(record.get('semester'))
            else:
                repeated_subjects[subject_name] = {
                    'info': backlog_info,
                    'attempts': 1,
                    'semesters': [record.get('semester')]
                }
            
            backlogs.append(backlog_info)
        
        # Check for incomplete subjects (in progress or no marks)
        if record.get('total', {}).get('marks', 0) == 0:
            incomplete_subjects.append({
                'subject_code': record.get('subject_code'),
                'subject_name': record.get('subject_name'),
                'semester': record.get('semester'),
                'status': 'in_progress'
            })
    
    return jsonify({
        'success': True,
        'total_backlogs': len(backlogs),
        'backlogs': backlogs,
        'repeated_subjects': [
            {
                'subject': name,
                'attempts': data['attempts'],
                'semesters': data['semesters'],
                'best_marks': max([b['marks'] for b in backlogs if b['subject_name'] == name] or [0])
            }
            for name, data in repeated_subjects.items() if data['attempts'] > 1
        ],
        'incomplete_subjects': incomplete_subjects,
        'clearance_advice': generate_clearance_advice(backlogs)
    }), 200


@parent_bp.route('/notifications/<reg_no>', methods=['GET'])
@parent_required
@check_student_access
def get_notifications(current_user, reg_no):
    """Get notifications for student"""
    limit = min(int(request.args.get('limit', 20)), 50)
    
    notifications = NotificationModel.get_notifications_for_student(reg_no, limit)
    
    formatted_notifications = []
    for notif in notifications:
        formatted_notifications.append({
            'id': str(notif['_id']),
            'title': notif.get('title'),
            'message': notif.get('message'),
            'category': notif.get('category'),
            'priority': notif.get('priority'),
            'posted_at': notif.get('created_at'),
            'time_ago': time_ago(notif.get('created_at', datetime.utcnow())),
            'acknowledgment_required': notif.get('acknowledgment_required', False),
            'attachments': notif.get('attachments', [])
        })
    
    return jsonify({
        'success': True,
        'notifications': formatted_notifications,
        'count': len(formatted_notifications),
        'unread_count': len([n for n in formatted_notifications if True])  # Implement read tracking
    }), 200


@parent_bp.route('/performance-insights/<reg_no>', methods=['GET'])
@parent_required
@check_student_access
def get_performance_insights(current_user, reg_no):
    """Get performance insights for student"""
    marks_records = MarksModel.get_marks(reg_no)
    
    if not marks_records:
        return jsonify({
            'success': True,
            'insights': {
                'strong_subjects': [],
                'weak_subjects': [],
                'suggestions': ['No marks data available']
            }
        }), 200
    
    if not isinstance(marks_records, list):
        marks_records = [marks_records]
    
    # Sort by marks
    sorted_marks = sorted(
        marks_records, 
        key=lambda x: x.get('total', {}).get('percentage', 0)
    )
    
    weak_subjects = sorted_marks[:3] if len(sorted_marks) >= 3 else sorted_marks
    strong_subjects = sorted_marks[-3:] if len(sorted_marks) >= 3 else sorted_marks
    
    # Calculate average
    total_percentage = sum(
        m.get('total', {}).get('percentage', 0) 
        for m in marks_records
    )
    average = total_percentage / len(marks_records) if marks_records else 0
    
    # Generate suggestions
    suggestions = []
    if average >= 80:
        suggestions.append("🌟 Excellent performance! Keep up the great work.")
    elif average >= 60:
        suggestions.append("📈 Good performance. Focus on weak subjects to improve further.")
        if weak_subjects:
            weak_names = [s.get('subject_name') for s in weak_subjects]
            suggestions.append(f"⚡ Seek faculty guidance for: {', '.join(weak_names)}")
    else:
        suggestions.append("⚠️ Performance needs improvement. Consider extra coaching.")
        suggestions.append("📚 Regular study schedule and practice tests recommended.")
    
    # Check attendance impact
    attendance_records = AttendanceModel.get_attendance(reg_no)
    low_attendance_subjects = []
    if isinstance(attendance_records, list):
        for att in attendance_records:
            if att.get('summary', {}).get('percentage', 0) < 75:
                low_attendance_subjects.append(att.get('subject_name'))
    
    if low_attendance_subjects:
        suggestions.append(
            f"📌 Low attendance may be affecting performance in: {', '.join(low_attendance_subjects)}"
        )
    
    return jsonify({
        'success': True,
        'insights': {
            'overall_average': round(average, 2),
            'strong_subjects': [
                {
                    'subject': s.get('subject_name'),
                    'marks': s.get('total', {}).get('marks'),
                    'percentage': s.get('total', {}).get('percentage'),
                    'grade': s.get('total', {}).get('grade')
                }
                for s in strong_subjects
            ],
            'weak_subjects': [
                {
                    'subject': s.get('subject_name'),
                    'marks': s.get('total', {}).get('marks'),
                    'percentage': s.get('total', {}).get('percentage'),
                    'grade': s.get('total', {}).get('grade')
                }
                for s in weak_subjects
            ],
            'suggestions': suggestions,
            'improvement_areas': [s.get('subject_name') for s in weak_subjects],
            'strength_areas': [s.get('subject_name') for s in strong_subjects]
        }
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


def calculate_fees_summary(fees_records):
    """Calculate fees summary"""
    if not fees_records:
        return {
            'total_paid': 0,
            'total_pending': 0,
            'semesters_paid': 0,
            'semesters_pending': 0
        }
    
    if not isinstance(fees_records, list):
        fees_records = [fees_records]
    
    total_paid = 0
    total_pending = 0
    semesters_paid = 0
    semesters_pending = 0
    
    for record in fees_records:
        summary = record.get('summary', {})
        total_paid += summary.get('total_paid', 0)
        total_pending += summary.get('pending', 0)
        
        if summary.get('status') == 'paid':
            semesters_paid += 1
        else:
            semesters_pending += 1
    
    return {
        'total_paid': total_paid,
        'total_pending': total_pending,
        'formatted_total_paid': format_currency(total_paid),
        'formatted_total_pending': format_currency(total_pending),
        'semesters_paid': semesters_paid,
        'semesters_pending': semesters_pending
    }


def get_recent_marks(marks_records, limit=5):
    """Get recent marks"""
    if not marks_records:
        return []
    
    if not isinstance(marks_records, list):
        marks_records = [marks_records]
    
    # Sort by upload date if available, otherwise by semester
    sorted_marks = sorted(
        marks_records,
        key=lambda x: x.get('uploaded_at', datetime.min),
        reverse=True
    )
    
    recent = sorted_marks[:limit]
    
    return [
        {
            'subject': m.get('subject_name'),
            'marks': m.get('total', {}).get('marks'),
            'max_marks': m.get('total', {}).get('max_marks'),
            'grade': m.get('total', {}).get('grade'),
            'semester': m.get('semester')
        }
        for m in recent
    ]


def generate_alerts(student, attendance_records, fees_records, marks_records):
    """Generate alerts for parent dashboard"""
    alerts = []
    
    # Attendance alerts
    if isinstance(attendance_records, list):
        for att in attendance_records:
            percentage = att.get('summary', {}).get('percentage', 0)
            if percentage < 75:
                alerts.append({
                    'type': 'attendance',
                    'priority': 'high' if percentage < 65 else 'medium',
                    'message': f"Low attendance in {att.get('subject_name')}: {percentage}%",
                    'action': 'View Attendance'
                })
    
    # Fee alerts
    if isinstance(fees_records, list):
        for fee in fees_records:
            if fee.get('summary', {}).get('status') in ['pending', 'overdue']:
                alerts.append({
                    'type': 'fee',
                    'priority': 'high',
                    'message': f"Pending fee for Semester {fee.get('semester')}: ₹{fee.get('summary', {}).get('pending', 0)}",
                    'action': 'View Fees'
                })
    
    # Backlog alerts
    if isinstance(marks_records, list):
        backlogs = [m for m in marks_records if m.get('backlog_status')]
        if backlogs:
            alerts.append({
                'type': 'backlog',
                'priority': 'high',
                'message': f"{len(backlogs)} active backlog(s). Please clear before graduation.",
                'action': 'View Backlogs'
            })
    
    return alerts


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


def generate_clearance_advice(backlogs):
    """Generate advice for clearing backlogs"""
    if not backlogs:
        return "All subjects cleared!"
    
    advice = []
    advice.append(f"Apply for supplementary examination for {len(backlogs)} subject(s).")
    advice.append("Contact examination cell for registration dates.")
    advice.append("Focus on previous year question papers.")
    
    if len(backlogs) > 3:
        advice.append("⚠️ Multiple backlogs detected. Meet your advisor immediately.")
    
    return " ".join(advice)
