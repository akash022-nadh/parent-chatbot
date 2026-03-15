"""
Utility Helper Functions
"""

import random
import string
import re
from datetime import datetime, timedelta
from typing import Optional, Dict, Any


def generate_otp(length: int = 6) -> str:
    """Generate random OTP of specified length"""
    return ''.join(random.choices(string.digits, k=length))


def generate_password(length: int = 12) -> str:
    """Generate secure random password"""
    characters = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(random.choices(characters, k=length))


def generate_reg_no(prefix: str = "STU", year: int = None) -> str:
    """Generate unique registration number"""
    if year is None:
        year = datetime.now().year % 100
    
    random_part = ''.join(random.choices(string.digits, k=4))
    return f"{prefix}{year}{random_part}"


def generate_employee_id(department: str = "GEN") -> str:
    """Generate employee ID for faculty/staff"""
    year = datetime.now().year % 100
    random_part = ''.join(random.choices(string.digits, k=4))
    return f"{department}{year}{random_part}"


def validate_email(email: str) -> bool:
    """Validate email address format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone: str) -> bool:
    """Validate phone number (10 digits)"""
    pattern = r'^[6-9]\d{9}$'
    return re.match(pattern, phone) is not None


def validate_reg_no(reg_no: str) -> bool:
    """Validate registration number format"""
    pattern = r'^STU\d{6}$'
    return re.match(pattern, reg_no) is not None


def format_phone(phone: str) -> str:
    """Format phone number to standard format"""
    digits = re.sub(r'\D', '', phone)
    if len(digits) == 10:
        return digits
    elif len(digits) == 11 and digits[0] == '0':
        return digits[1:]
    elif len(digits) == 12 and digits[:2] == '91':
        return digits[2:]
    return digits


def calculate_percentage(obtained: float, total: float) -> float:
    """Calculate percentage safely"""
    if total == 0:
        return 0.0
    return round((obtained / total) * 100, 2)


def calculate_grade(marks: float, max_marks: float = 100) -> str:
    """Calculate grade based on marks"""
    percentage = calculate_percentage(marks, max_marks)
    
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


def calculate_grade_point(grade: str) -> int:
    """Calculate grade point from grade"""
    grade_points = {
        'A+': 10, 'A': 9, 'B': 8, 'C': 7,
        'D': 6, 'E': 5, 'F': 0
    }
    return grade_points.get(grade, 0)


def calculate_cgpa(semester_results: list) -> float:
    """Calculate cumulative CGPA from semester results"""
    if not semester_results:
        return 0.0
    
    total_credits = 0
    total_points = 0
    
    for result in semester_results:
        credits = result.get('credits_earned', 0)
        sgpa = result.get('sgpa', 0)
        total_credits += credits
        total_points += credits * sgpa
    
    if total_credits == 0:
        return 0.0
    
    return round(total_points / total_credits, 2)


def get_attendance_status(percentage: float) -> str:
    """Get attendance status based on percentage"""
    if percentage >= 85:
        return 'excellent'
    elif percentage >= 75:
        return 'good'
    elif percentage >= 65:
        return 'warning'
    else:
        return 'critical'


def format_currency(amount: float, currency: str = "INR") -> str:
    """Format amount as currency"""
    if currency == "INR":
        return f"₹{amount:,.2f}"
    else:
        return f"${amount:,.2f}"


def format_date(date_obj, format_str: str = "%d %b %Y") -> str:
    """Format date object to string"""
    if isinstance(date_obj, str):
        try:
            date_obj = datetime.fromisoformat(date_obj.replace('Z', '+00:00'))
        except:
            return date_obj
    
    if isinstance(date_obj, datetime):
        return date_obj.strftime(format_str)
    
    return str(date_obj)


def time_ago(dt: datetime) -> str:
    """Convert datetime to 'time ago' string"""
    now = datetime.utcnow()
    diff = now - dt
    
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif seconds < 604800:
        days = int(seconds / 86400)
        return f"{days} day{'s' if days > 1 else ''} ago"
    elif seconds < 2592000:
        weeks = int(seconds / 604800)
        return f"{weeks} week{'s' if weeks > 1 else ''} ago"
    else:
        return format_date(dt)


def truncate_text(text: str, length: int = 100, suffix: str = "...") -> str:
    """Truncate text to specified length"""
    if len(text) <= length:
        return text
    return text[:length].rsplit(' ', 1)[0] + suffix


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for safe storage"""
    # Remove unsafe characters
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')
    return filename


def paginate_results(data: list, page: int, per_page: int) -> Dict[str, Any]:
    """Paginate list of results"""
    total = len(data)
    pages = (total + per_page - 1) // per_page
    
    start = (page - 1) * per_page
    end = start + per_page
    
    return {
        'items': data[start:end],
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': pages,
        'has_next': page < pages,
        'has_prev': page > 1,
        'next_page': page + 1 if page < pages else None,
        'prev_page': page - 1 if page > 1 else None
    }


def send_sms(phone: str, message: str) -> bool:
    """Send SMS (placeholder - integrate with actual SMS gateway)"""
    # This is a placeholder function
    # In production, integrate with:
    # - Twilio
    # - AWS SNS
    # - Fast2SMS
    # - Msg91
    # - etc.
    
    try:
        # Log SMS for demo
        print(f"[SMS TO {phone}]: {message}")
        return True
    except Exception as e:
        print(f"SMS Error: {str(e)}")
        return False


def send_email(to_email: str, subject: str, body: str, html: bool = False) -> bool:
    """Send email (placeholder - integrate with actual email service)"""
    # This is a placeholder function
    # In production, integrate with:
    # - SMTP (Gmail, SendGrid, etc.)
    # - AWS SES
    # - Mailgun
    # - etc.
    
    try:
        # Log email for demo
        print(f"[EMAIL TO {to_email}]")
        print(f"Subject: {subject}")
        print(f"Body: {body[:200]}...")
        return True
    except Exception as e:
        print(f"Email Error: {str(e)}")
        return False


def generate_notification_title(category: str, action: str) -> str:
    """Generate notification title based on category and action"""
    templates = {
        'attendance': {
            'low': 'Low Attendance Alert',
            'updated': 'Attendance Updated',
            'warning': 'Attendance Warning'
        },
        'marks': {
            'uploaded': 'Marks Uploaded',
            'published': 'Results Published',
            'backlog': 'Backlog Alert'
        },
        'fees': {
            'due': 'Fee Payment Due',
            'reminder': 'Fee Payment Reminder',
            'overdue': 'Fee Payment Overdue'
        },
        'exam': {
            'scheduled': 'Exam Scheduled',
            'hall_ticket': 'Hall Ticket Available',
            'results': 'Exam Results Published'
        },
        'general': {
            'announcement': 'New Announcement',
            'holiday': 'Holiday Notice',
            'event': 'Upcoming Event'
        }
    }
    
    return templates.get(category, {}).get(action, 'New Notification')


def get_semester_name(semester: int) -> str:
    """Get semester name from number"""
    semesters = {
        1: 'First', 2: 'Second',
        3: 'Third', 4: 'Fourth',
        5: 'Fifth', 6: 'Sixth',
        7: 'Seventh', 8: 'Eighth'
    }
    return semesters.get(semester, f'Semester {semester}')


def get_branch_full_name(branch: str) -> str:
    """Get full branch name from code"""
    branches = {
        'CSE': 'Computer Science and Engineering',
        'ECE': 'Electronics and Communication Engineering',
        'EEE': 'Electrical and Electronics Engineering',
        'ME': 'Mechanical Engineering',
        'CE': 'Civil Engineering',
        'IT': 'Information Technology',
        'AI': 'Artificial Intelligence',
        'DS': 'Data Science',
        'CY': 'Cyber Security'
    }
    return branches.get(branch, branch)


def calculate_attendance_summary(records: list) -> Dict[str, Any]:
    """Calculate attendance summary from records"""
    total = len(records)
    if total == 0:
        return {
            'total_classes': 0,
            'attended': 0,
            'absent': 0,
            'late': 0,
            'percentage': 0.0,
            'status': 'no_data'
        }
    
    present = sum(1 for r in records if r.get('status') == 'present')
    absent = sum(1 for r in records if r.get('status') == 'absent')
    late = sum(1 for r in records if r.get('status') == 'late')
    
    # Count late as present for percentage
    effective_present = present + late
    percentage = calculate_percentage(effective_present, total)
    
    return {
        'total_classes': total,
        'attended': present,
        'absent': absent,
        'late': late,
        'percentage': percentage,
        'status': get_attendance_status(percentage)
    }


def mask_sensitive_data(data: str, mask_char: str = '*', visible_start: int = 4, visible_end: int = 4) -> str:
    """Mask sensitive data (phone, aadhar, etc.)"""
    if len(data) <= visible_start + visible_end:
        return data
    
    start = data[:visible_start]
    end = data[-visible_end:]
    middle = mask_char * (len(data) - visible_start - visible_end)
    
    return f"{start}{middle}{end}"


def safe_divide(numerator: float, denominator: float, default: float = 0.0) -> float:
    """Safely divide two numbers"""
    if denominator == 0:
        return default
    return numerator / denominator


def get_current_academic_year() -> str:
    """Get current academic year"""
    now = datetime.now()
    year = now.year
    
    # Academic year typically runs July-June
    if now.month >= 7:
        return f"{year}-{year + 1}"
    else:
        return f"{year - 1}-{year}"


def get_current_semester() -> int:
    """Get current semester based on month"""
    month = datetime.now().month
    
    # Odd semesters: July-Dec (1, 3, 5, 7)
    # Even semesters: Jan-June (2, 4, 6, 8)
    if month >= 7:
        return 1  # Start of odd semester
    else:
        return 2  # Start of even semester


def is_valid_academic_year(year_str: str) -> bool:
    """Validate academic year format"""
    pattern = r'^\d{4}-\d{4}$'
    if not re.match(pattern, year_str):
        return False
    
    try:
        start, end = map(int, year_str.split('-'))
        return end == start + 1
    except:
        return False
