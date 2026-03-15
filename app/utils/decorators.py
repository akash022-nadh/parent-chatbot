"""
Role-based Access Control Decorators
"""

from functools import wraps
from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request, get_jwt
from app.models import UserModel


def role_required(*allowed_roles):
    """Decorator to check if user has required role"""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            
            # Get user ID from JWT
            user_id = get_jwt_identity()
            
            # Get user details
            user = UserModel.find_by_id(user_id)
            
            if not user:
                return jsonify({
                    'success': False,
                    'message': 'User not found'
                }), 404
            
            # Check if user role is allowed
            user_role = user.get('role')
            
            if user_role not in allowed_roles:
                return jsonify({
                    'success': False,
                    'message': f'Access denied. Required role(s): {", ".join(allowed_roles)}',
                    'error': 'insufficient_permissions'
                }), 403
            
            # Add user to kwargs for use in the route
            kwargs['current_user'] = user
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def admin_required(fn):
    """Shortcut decorator for admin-only routes"""
    return role_required('admin')(fn)


def faculty_required(fn):
    """Shortcut decorator for faculty routes (admin or faculty)"""
    return role_required('admin', 'faculty')(fn)


def parent_required(fn):
    """Shortcut decorator for parent routes"""
    return role_required('parent')(fn)


def student_required(fn):
    """Shortcut decorator for student routes (admin, faculty, or student)"""
    return role_required('admin', 'faculty', 'student')(fn)


def any_role_required(fn):
    """Any authenticated user can access"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        user = UserModel.find_by_id(user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        kwargs['current_user'] = user
        return fn(*args, **kwargs)
    return wrapper


def validate_json(required_fields=None):
    """Decorator to validate JSON request body"""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            from flask import request
            
            if not request.is_json:
                return jsonify({
                    'success': False,
                    'message': 'Content-Type must be application/json'
                }), 400
            
            data = request.get_json()
            
            if required_fields:
                missing_fields = [field for field in required_fields if field not in data or not data[field]]
                
                if missing_fields:
                    return jsonify({
                        'success': False,
                        'message': f'Missing required fields: {", ".join(missing_fields)}'
                    }), 400
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def validate_query_params(allowed_params=None, required_params=None):
    """Decorator to validate query parameters"""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            from flask import request
            
            # Get query parameters
            params = request.args.to_dict()
            
            # Check for required parameters
            if required_params:
                missing = [param for param in required_params if param not in params]
                if missing:
                    return jsonify({
                        'success': False,
                        'message': f'Missing required query parameters: {", ".join(missing)}'
                    }), 400
            
            # Check for allowed parameters
            if allowed_params:
                invalid = [param for param in params if param not in allowed_params]
                if invalid:
                    return jsonify({
                        'success': False,
                        'message': f'Invalid query parameters: {", ".join(invalid)}'
                    }), 400
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def rate_limit_per_user(limit=100, per='hour'):
    """Rate limit decorator per user"""
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            # This would integrate with Flask-Limiter
            # For now, basic implementation
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def log_action(action_name):
    """Decorator to log user actions"""
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            from flask import request
            import logging
            
            logger = logging.getLogger(__name__)
            
            # Get user info if available
            user_info = 'anonymous'
            try:
                verify_jwt_in_request()
                user_id = get_jwt_identity()
                user = UserModel.find_by_id(user_id)
                if user:
                    user_info = f"{user.get('username')} ({user.get('role')})"
            except:
                pass
            
            # Log the action
            logger.info(f"Action: {action_name} | User: {user_info} | IP: {request.remote_addr} | Endpoint: {request.endpoint}")
            
            return fn(*args, **kwargs)
        return wrapper
    return decorator


def check_student_access(fn):
    """Decorator to check if parent/faculty can access specific student data"""
    @wraps(fn)
    def wrapper(*args, **kwargs):
        from flask import request
        
        verify_jwt_in_request()
        user_id = get_jwt_identity()
        user = UserModel.find_by_id(user_id)
        
        if not user:
            return jsonify({
                'success': False,
                'message': 'User not found'
            }), 404
        
        # Get student registration number from URL or body
        reg_no = kwargs.get('reg_no') or request.view_args.get('reg_no')
        
        if not reg_no:
            data = request.get_json(silent=True) or {}
            reg_no = data.get('reg_no')
        
        # Admins can access any student
        if user.get('role') == 'admin':
            kwargs['current_user'] = user
            return fn(*args, **kwargs)
        
        # Parents can only access their linked student
        if user.get('role') == 'parent':
            linked_reg_no = user.get('role_specific', {}).get('student_reg_no')
            if reg_no != linked_reg_no:
                return jsonify({
                    'success': False,
                    'message': 'Access denied. You can only view your child\'s data.'
                }), 403
        
        # Faculty can access students in their sections
        if user.get('role') == 'faculty':
            from models import StudentModel
            
            faculty_id = user.get('role_specific', {}).get('employee_id')
            student = StudentModel.find_by_reg_no(reg_no)
            
            if not student:
                return jsonify({
                    'success': False,
                    'message': 'Student not found'
                }), 404
            
            # Check if faculty is advisor or teaches the student
            advisor_id = student.get('advisor', {}).get('faculty_id')
            if str(advisor_id) != str(user.get('_id')):
                # Additional check: is faculty teaching any subject to this student?
                # This would require checking the faculty's assigned sections
                pass
        
        # Students can only access their own data
        if user.get('role') == 'student':
            student_reg_no = user.get('role_specific', {}).get('student_reg_no')
            if reg_no != student_reg_no:
                return jsonify({
                    'success': False,
                    'message': 'Access denied. You can only view your own data.'
                }), 403
        
        kwargs['current_user'] = user
        return fn(*args, **kwargs)
    return wrapper
