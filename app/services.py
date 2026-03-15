"""
Service Layer - Business Logic for Academic Monitoring System
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from app.models import (
    StudentModel, AttendanceModel, MarksModel, CGPAModel,
    FeesModel, NotificationModel, FacultyModel
)
from app.utils.helpers import (
    calculate_percentage, calculate_grade, calculate_grade_point,
    get_attendance_status, format_currency
)


class AcademicService:
    """Service for academic-related operations"""
    
    @staticmethod
    def get_student_academic_summary(reg_no: str) -> Dict:
        """Get comprehensive academic summary for a student"""
        student = StudentModel.find_by_reg_no(reg_no)
        if not student:
            return None
        
        # Get all academic data
        attendance = AttendanceModel.get_attendance(reg_no)
        marks = MarksModel.get_marks(reg_no)
        cgpa_records = CGPAModel.get_cgpa_records(reg_no)
        
        return {
            'student_info': {
                'reg_no': student.get('reg_no'),
                'name': f"{student.get('personal_info', {}).get('first_name', '')} "
                        f"{student.get('personal_info', {}).get('last_name', '')}".strip(),
                'branch': student.get('academic', {}).get('branch'),
                'year': student.get('academic', {}).get('year'),
                'semester': student.get('academic', {}).get('semester'),
                'cgpa': student.get('academic', {}).get('cgpa')
            },
            'attendance_summary': AcademicService._calculate_attendance_summary(attendance),
            'marks_summary': AcademicService._calculate_marks_summary(marks),
            'cgpa_trend': [
                {'semester': r.get('semester'), 'sgpa': r.get('sgpa')}
                for r in cgpa_records
            ],
            'standing': AcademicService._calculate_academic_standing(marks, attendance)
        }
    
    @staticmethod
    def _calculate_attendance_summary(attendance_records) -> Dict:
        """Calculate attendance summary"""
        if not attendance_records:
            return {'overall': 0, 'status': 'no_data'}
        
        if not isinstance(attendance_records, list):
            attendance_records = [attendance_records]
        
        total_classes = sum(r.get('summary', {}).get('total_classes', 0) for r in attendance_records)
        total_attended = sum(r.get('summary', {}).get('attended', 0) for r in attendance_records)
        
        percentage = (total_attended / total_classes * 100) if total_classes > 0 else 0
        
        return {
            'overall': round(percentage, 2),
            'status': get_attendance_status(percentage),
            'subjects_count': len(attendance_records)
        }
    
    @staticmethod
    def _calculate_marks_summary(marks_records) -> Dict:
        """Calculate marks summary"""
        if not marks_records:
            return {'average': 0, 'subjects': 0}
        
        if not isinstance(marks_records, list):
            marks_records = [marks_records]
        
        total_percentage = sum(
            m.get('total', {}).get('percentage', 0) 
            for m in marks_records
        )
        
        average = total_percentage / len(marks_records) if marks_records else 0
        
        return {
            'average': round(average, 2),
            'subjects': len(marks_records),
            'backlogs': len([m for m in marks_records if m.get('backlog_status')])
        }
    
    @staticmethod
    def _calculate_academic_standing(marks, attendance) -> str:
        """Calculate overall academic standing"""
        marks_summary = AcademicService._calculate_marks_summary(marks)
        attendance_summary = AcademicService._calculate_attendance_summary(attendance)
        
        avg_marks = marks_summary.get('average', 0)
        avg_attendance = attendance_summary.get('overall', 0)
        
        if avg_marks >= 85 and avg_attendance >= 85:
            return 'Excellent'
        elif avg_marks >= 70 and avg_attendance >= 75:
            return 'Good'
        elif avg_marks >= 60 and avg_attendance >= 65:
            return 'Satisfactory'
        else:
            return 'Needs Improvement'
    
    @staticmethod
    def get_class_performance(branch: str, year: int, semester: int) -> Dict:
        """Get class-level performance metrics"""
        students = StudentModel.get_students_by_branch_year(branch, year)
        
        cgpa_list = []
        attendance_list = []
        
        for student in students:
            reg_no = student.get('reg_no')
            
            # Get CGPA
            cgpa = CGPAModel.get_current_cgpa(reg_no)
            cgpa_list.append(cgpa)
            
            # Get attendance
            attendance = AttendanceModel.get_attendance(reg_no, semester=semester)
            if isinstance(attendance, list) and attendance:
                avg_att = sum(a.get('summary', {}).get('percentage', 0) for a in attendance) / len(attendance)
                attendance_list.append(avg_att)
        
        return {
            'total_students': len(students),
            'average_cgpa': round(sum(cgpa_list) / len(cgpa_list), 2) if cgpa_list else 0,
            'average_attendance': round(sum(attendance_list) / len(attendance_list), 2) if attendance_list else 0,
            'topper_cgpa': max(cgpa_list) if cgpa_list else 0,
            'students_below_75_attendance': len([a for a in attendance_list if a < 75])
        }


class AttendanceService:
    """Service for attendance-related operations"""
    
    @staticmethod
    def get_defaulter_list(threshold: float = 75.0, branch: str = None, year: int = None) -> List[Dict]:
        """Get list of students with attendance below threshold"""
        low_attendance = AttendanceModel.get_low_attendance(threshold)
        
        defaulters = []
        for record in low_attendance:
            student = StudentModel.find_by_reg_no(record.get('student_reg_no'))
            if not student:
                continue
            
            # Apply filters
            if branch and student.get('academic', {}).get('branch') != branch:
                continue
            if year and student.get('academic', {}).get('year') != year:
                continue
            
            defaulters.append({
                'reg_no': student.get('reg_no'),
                'name': f"{student.get('personal_info', {}).get('first_name', '')} "
                        f"{student.get('personal_info', {}).get('last_name', '')}".strip(),
                'branch': student.get('academic', {}).get('branch'),
                'year': student.get('academic', {}).get('year'),
                'subject': record.get('subject_name'),
                'attendance_percentage': record.get('summary', {}).get('percentage')
            })
        
        return defaulters
    
    @staticmethod
    def get_attendance_trend(reg_no: str, months: int = 6) -> List[Dict]:
        """Get attendance trend for last N months"""
        attendance_records = AttendanceModel.get_attendance(reg_no)
        
        if not isinstance(attendance_records, list):
            attendance_records = [attendance_records] if attendance_records else []
        
        # Group by month
        monthly_data = {}
        cutoff_date = datetime.utcnow() - timedelta(days=30*months)
        
        for record in attendance_records:
            for rec in record.get('records', []):
                date = rec.get('date')
                if isinstance(date, datetime) and date >= cutoff_date:
                    month_key = date.strftime('%Y-%m')
                    
                    if month_key not in monthly_data:
                        monthly_data[month_key] = {'total': 0, 'present': 0}
                    
                    monthly_data[month_key]['total'] += 1
                    if rec.get('status') == 'present':
                        monthly_data[month_key]['present'] += 1
        
        # Calculate percentages
        trend = []
        for month in sorted(monthly_data.keys()):
            data = monthly_data[month]
            percentage = (data['present'] / data['total'] * 100) if data['total'] > 0 else 0
            trend.append({
                'month': month,
                'percentage': round(percentage, 2),
                'classes_conducted': data['total']
            })
        
        return trend


class PerformanceService:
    """Service for performance analysis"""
    
    @staticmethod
    def analyze_student_performance(reg_no: str) -> Dict:
        """Comprehensive performance analysis"""
        marks = MarksModel.get_marks(reg_no)
        
        if not marks:
            return {
                'status': 'no_data',
                'suggestions': ['No marks data available']
            }
        
        if not isinstance(marks, list):
            marks = [marks]
        
        # Sort by marks
        sorted_marks = sorted(marks, key=lambda x: x.get('total', {}).get('percentage', 0))
        
        weak_subjects = sorted_marks[:3] if len(sorted_marks) >= 3 else sorted_marks
        strong_subjects = sorted_marks[-3:] if len(sorted_marks) >= 3 else sorted_marks
        
        # Calculate metrics
        percentages = [m.get('total', {}).get('percentage', 0) for m in marks]
        average = sum(percentages) / len(percentages) if percentages else 0
        
        return {
            'average_percentage': round(average, 2),
            'strong_subjects': [
                {
                    'subject': s.get('subject_name'),
                    'percentage': s.get('total', {}).get('percentage'),
                    'grade': s.get('total', {}).get('grade')
                }
                for s in strong_subjects
            ],
            'weak_subjects': [
                {
                    'subject': s.get('subject_name'),
                    'percentage': s.get('total', {}).get('percentage'),
                    'grade': s.get('total', {}).get('grade')
                }
                for s in weak_subjects
            ],
            'improvement_suggestions': PerformanceService._generate_suggestions(
                average, weak_subjects, strong_subjects
            )
        }
    
    @staticmethod
    def _generate_suggestions(average: float, weak_subjects: List, strong_subjects: List) -> List[str]:
        """Generate personalized improvement suggestions"""
        suggestions = []
        
        if average >= 80:
            suggestions.append("🌟 Excellent performance! Keep maintaining this standard.")
            suggestions.append("Consider helping peers in subjects where you excel.")
        elif average >= 60:
            suggestions.append("📈 Good performance with room for improvement.")
            
            if weak_subjects:
                weak_names = [s.get('subject_name') for s in weak_subjects]
                suggestions.append(f"⚡ Focus on improving: {', '.join(weak_names)}")
                suggestions.append("📚 Attend extra classes and seek faculty guidance.")
        else:
            suggestions.append("⚠️ Performance needs significant improvement.")
            suggestions.append("🎯 Set up a regular study schedule.")
            suggestions.append("👨‍🏫 Meet your advisor to discuss improvement strategies.")
            suggestions.append("📖 Consider joining study groups or getting tutoring.")
        
        # Attendance suggestion
        suggestions.append("📌 Maintain attendance above 75% to avoid academic penalties.")
        
        return suggestions
    
    @staticmethod
    def predict_cgpa(reg_no: str, target_semester: int) -> Dict:
        """Predict CGPA for upcoming semester based on current trend"""
        cgpa_records = CGPAModel.get_cgpa_records(reg_no)
        
        if not cgpa_records:
            return {
                'predicted_cgpa': 0,
                'confidence': 'low',
                'message': 'Insufficient data for prediction'
            }
        
        # Simple linear trend prediction
        sgpas = [r.get('sgpa', 0) for r in cgpa_records]
        semesters = [r.get('semester', 0) for r in cgpa_records]
        
        if len(sgpas) < 2:
            predicted = sgpas[0] if sgpas else 0
        else:
            # Calculate trend
            trend = (sgpas[-1] - sgpas[0]) / (len(sgpas) - 1)
            predicted = sgpas[-1] + trend
            predicted = max(0, min(10, predicted))  # Clamp between 0-10
        
        return {
            'predicted_cgpa': round(predicted, 2),
            'current_trend': 'improving' if trend > 0 else 'declining' if trend < 0 else 'stable',
            'confidence': 'high' if len(sgpas) >= 4 else 'medium' if len(sgpas) >= 2 else 'low',
            'target_cgpa': 8.5,
            'gap_to_target': round(8.5 - predicted, 2) if predicted < 8.5 else 0
        }


class FeeService:
    """Service for fee-related operations"""
    
    @staticmethod
    def get_fee_summary(reg_no: str) -> Dict:
        """Get comprehensive fee summary"""
        fees_records = FeesModel.get_fees(reg_no)
        
        if not fees_records:
            return {
                'total_paid': 0,
                'total_pending': 0,
                'status': 'no_data'
            }
        
        if not isinstance(fees_records, list):
            fees_records = [fees_records]
        
        total_paid = sum(r.get('summary', {}).get('total_paid', 0) for r in fees_records)
        total_pending = sum(r.get('summary', {}).get('pending', 0) for r in fees_records)
        
        # Find pending semesters
        pending_semesters = [
            r.get('semester') 
            for r in fees_records 
            if r.get('summary', {}).get('status') in ['pending', 'partial', 'overdue']
        ]
        
        return {
            'total_paid': total_paid,
            'total_pending': total_pending,
            'formatted_total_paid': format_currency(total_paid),
            'formatted_total_pending': format_currency(total_pending),
            'pending_semesters': pending_semesters,
            'status': 'paid' if total_pending == 0 else 'pending',
            'scholarship_eligible': any(
                r.get('scholarship', {}).get('eligible', False) 
                for r in fees_records
            )
        }
    
    @staticmethod
    def get_defaulters_list(min_pending: float = 1000, days_overdue: int = 30) -> List[Dict]:
        """Get list of fee defaulters"""
        pending_fees = FeesModel.get_pending_fees()
        
        defaulters = []
        for fee in pending_fees:
            pending_amount = fee.get('summary', {}).get('pending', 0)
            
            if pending_amount >= min_pending:
                student = StudentModel.find_by_reg_no(fee.get('student_reg_no'))
                if student:
                    defaulters.append({
                        'reg_no': student.get('reg_no'),
                        'name': f"{student.get('personal_info', {}).get('first_name', '')} "
                                f"{student.get('personal_info', {}).get('last_name', '')}".strip(),
                        'branch': student.get('academic', {}).get('branch'),
                        'year': student.get('academic', {}).get('year'),
                        'semester': fee.get('semester'),
                        'pending_amount': pending_amount,
                        'formatted_amount': format_currency(pending_amount),
                        'due_date': fee.get('summary', {}).get('due_date'),
                        'parent_phone': student.get('family', {}).get('parent_phone')
                    })
        
        return sorted(defaulters, key=lambda x: x['pending_amount'], reverse=True)


class NotificationService:
    """Service for notification operations"""
    
    @staticmethod
    def create_and_send_notification(
        title: str,
        message: str,
        category: str,
        priority: str,
        target_type: str,
        target_roles: List[str],
        specific_users: List[str] = None
    ) -> str:
        """Create and send notification to target users"""
        notification_data = {
            'title': title,
            'message': message,
            'category': category,
            'priority': priority,
            'target': {
                'type': target_type,
                'roles': target_roles,
                'specific_users': specific_users or []
            },
            'posted_by': {
                'name': 'System',
                'role': 'admin'
            },
            'status': 'active'
        }
        
        notification_id = NotificationModel.create_notification(notification_data)
        return notification_id
    
    @staticmethod
    def get_unread_count(user_id: str, role: str, reg_no: str = None) -> int:
        """Get unread notification count"""
        # This would require implementing read tracking
        # For now, return count of active notifications
        notifications = NotificationModel.get_notifications(role=role, limit=100)
        return len([n for n in notifications if n.get('status') == 'active'])


class ReportService:
    """Service for generating reports"""
    
    @staticmethod
    def generate_student_report(reg_no: str) -> Dict:
        """Generate comprehensive student report"""
        student = StudentModel.find_by_reg_no(reg_no)
        if not student:
            return None
        
        academic_summary = AcademicService.get_student_academic_summary(reg_no)
        attendance_trend = AttendanceService.get_attendance_trend(reg_no)
        performance_analysis = PerformanceService.analyze_student_performance(reg_no)
        fee_summary = FeeService.get_fee_summary(reg_no)
        
        return {
            'student_info': academic_summary.get('student_info'),
            'academic_performance': academic_summary,
            'attendance_trend': attendance_trend,
            'performance_analysis': performance_analysis,
            'fee_summary': fee_summary,
            'generated_at': datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def generate_class_report(branch: str, year: int, semester: int) -> Dict:
        """Generate class-level report"""
        students = StudentModel.get_students_by_branch_year(branch, year)
        
        cgpa_list = []
        attendance_list = []
        backlogs_count = 0
        
        for student in students:
            reg_no = student.get('reg_no')
            
            cgpa = CGPAModel.get_current_cgpa(reg_no)
            cgpa_list.append(cgpa)
            
            attendance = AttendanceModel.get_attendance(reg_no, semester=semester)
            if isinstance(attendance, list) and attendance:
                avg_att = sum(a.get('summary', {}).get('percentage', 0) for a in attendance) / len(attendance)
                attendance_list.append(avg_att)
            
            backlogs = student.get('academic', {}).get('backlogs', 0)
            if backlogs > 0:
                backlogs_count += 1
        
        return {
            'branch': branch,
            'year': year,
            'semester': semester,
            'total_students': len(students),
            'average_cgpa': round(sum(cgpa_list) / len(cgpa_list), 2) if cgpa_list else 0,
            'highest_cgpa': max(cgpa_list) if cgpa_list else 0,
            'lowest_cgpa': min(cgpa_list) if cgpa_list else 0,
            'average_attendance': round(sum(attendance_list) / len(attendance_list), 2) if attendance_list else 0,
            'students_with_backlogs': backlogs_count,
            'students_below_75_attendance': len([a for a in attendance_list if a < 75]),
            'generated_at': datetime.utcnow().isoformat()
        }
