"""
Chatbot Routes
Endpoints for the Parent Verification Chatbot
"""

from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models import UserModel, StudentModel
from app.utils.decorators import any_role_required, check_student_access
import sys
import os

# Add parent directory to path to import chatbot
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

chatbot_bp = Blueprint('chatbot', __name__)


@chatbot_bp.route('/message', methods=['POST'])
@any_role_required
def chat_message(current_user):
    """Process chatbot message"""
    data = request.get_json()
    message = data.get('message', '').strip()
    
    if not message:
        return jsonify({
            'success': False,
            'message': 'Message is required'
        }), 400
    
    # Get student registration number based on user role
    reg_no = None
    if current_user.get('role') == 'parent':
        reg_no = current_user.get('role_specific', {}).get('student_reg_no')
    elif current_user.get('role') == 'student':
        reg_no = current_user.get('role_specific', {}).get('student_reg_no')
    elif current_user.get('role') in ['admin', 'faculty']:
        reg_no = data.get('reg_no')  # Admin/Faculty can specify any student
    
    if not reg_no:
        return jsonify({
            'success': False,
            'message': 'Student registration number not found'
        }), 400
    
    # Import chatbot here to avoid circular imports
    try:
        from chatbot import handle_chat, detect_intent, get_help_menu
        
        # Detect intent
        intent = detect_intent(message)
        
        # Get response from chatbot
        response = handle_chat(intent, reg_no)
        
        # Handle logout
        if response == "LOGOUT":
            return jsonify({
                'success': True,
                'intent': 'logout',
                'response': 'You have been logged out.',
                'action': 'logout'
            }), 200
        
        return jsonify({
            'success': True,
            'intent': intent,
            'message': message,
            'response': response,
            'reg_no': reg_no
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Chatbot error: {str(e)}'
        }), 500


@chatbot_bp.route('/quick-action', methods=['POST'])
@any_role_required
def quick_action(current_user):
    """Handle quick action button clicks"""
    data = request.get_json()
    action = data.get('action')
    
    # Map quick actions to intents
    action_map = {
        'show_attendance': 'attendance',
        'show_marks': 'marks',
        'show_cgpa': 'cgpa',
        'show_backlogs': 'backlogs',
        'show_fees': 'fees',
        'show_notifications': 'notifications',
        'show_faculty': 'faculty',
        'show_insights': 'insights',
        'show_course_status': 'course_status',
        'show_calendar': 'calendar',
        'show_scholarship': 'scholarship',
        'low_attendance': 'low_attendance',
        'repeated_subjects': 'repeated_subjects',
        'incomplete_subjects': 'incomplete_subjects',
        'show_exams': 'exams',
        'show_assignments': 'assignments',
        'academic_office': 'academic_office'
    }
    
    intent = action_map.get(action, 'unknown')
    
    # Get student registration number
    reg_no = None
    if current_user.get('role') == 'parent':
        reg_no = current_user.get('role_specific', {}).get('student_reg_no')
    elif current_user.get('role') == 'student':
        reg_no = current_user.get('role_specific', {}).get('student_reg_no')
    elif current_user.get('role') in ['admin', 'faculty']:
        reg_no = data.get('reg_no')
    
    if not reg_no:
        return jsonify({
            'success': False,
            'message': 'Student registration number not found'
        }), 400
    
    try:
        from chatbot import handle_chat
        
        # Get response from chatbot
        response = handle_chat(intent, reg_no)
        
        return jsonify({
            'success': True,
            'intent': intent,
            'action': action,
            'response': response,
            'reg_no': reg_no
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Chatbot error: {str(e)}'
        }), 500


@chatbot_bp.route('/help', methods=['GET'])
def get_help():
    """Get chatbot help menu"""
    try:
        from chatbot import get_help_menu
        help_menu = get_help_menu()
        
        return jsonify({
            'success': True,
            'help': help_menu
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500


@chatbot_bp.route('/intents', methods=['GET'])
def get_intents():
    """Get list of supported intents"""
    intents = {
        'attendance': {
            'description': 'View attendance information',
            'keywords': ['attendance', 'present', 'absent']
        },
        'marks': {
            'description': 'View subject-wise marks',
            'keywords': ['marks', 'score', 'grades']
        },
        'cgpa': {
            'description': 'View CGPA information',
            'keywords': ['cgpa', 'gpa', 'grade point']
        },
        'backlogs': {
            'description': 'View backlog subjects',
            'keywords': ['backlog', 'arrear', 'fail']
        },
        'fees': {
            'description': 'View fee status',
            'keywords': ['fee', 'payment', 'pending']
        },
        'notifications': {
            'description': 'View notifications',
            'keywords': ['notification', 'alert', 'announcement']
        },
        'faculty': {
            'description': 'View faculty contacts',
            'keywords': ['faculty', 'teacher', 'contact']
        },
        'insights': {
            'description': 'Get performance insights',
            'keywords': ['insight', 'analysis', 'performance']
        },
        'course_status': {
            'description': 'View course completion status',
            'keywords': ['course status', 'completion']
        },
        'calendar': {
            'description': 'View academic calendar',
            'keywords': ['calendar', 'schedule', 'events']
        },
        'scholarship': {
            'description': 'View scholarship status',
            'keywords': ['scholarship', 'merit', 'financial aid']
        },
        'low_attendance': {
            'description': 'View low attendance alert',
            'keywords': ['low attendance', 'attendance alert']
        },
        'repeated_subjects': {
            'description': 'View repeated subjects',
            'keywords': ['repeated subject', 'multiple attempts']
        },
        'incomplete_subjects': {
            'description': 'View incomplete subjects',
            'keywords': ['incomplete subject', 'pending']
        },
        'exams': {
            'description': 'View upcoming exams',
            'keywords': ['exam', 'test', 'upcoming exam']
        },
        'assignments': {
            'description': 'View assignments',
            'keywords': ['assignment', 'homework', 'project']
        },
        'academic_office': {
            'description': 'View academic office contacts',
            'keywords': ['academic office', 'administration']
        },
        'help': {
            'description': 'Show help menu',
            'keywords': ['help', 'menu', 'options']
        },
        'logout': {
            'description': 'Logout from system',
            'keywords': ['logout', 'exit', 'bye']
        }
    }
    
    return jsonify({
        'success': True,
        'intents': intents,
        'count': len(intents)
    }), 200
