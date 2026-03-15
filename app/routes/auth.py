"""
Authentication Routes
Handles login, logout, registration, and password management
"""

from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import (
    create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, unset_jwt_cookies
)
from datetime import datetime, timedelta
import re
import random
from app.models import UserModel, StudentModel, FacultyModel
from app.utils.decorators import validate_json
from app.utils.helpers import generate_otp, send_sms, send_email

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['POST'])
@validate_json(['username', 'password'])
def login():
    """Login endpoint for all user roles"""
    data = request.get_json()
    username = data.get('username', '').strip().lower()
    password = data.get('password', '')
    role = data.get('role', '')  # Optional: for additional verification
    
    # Find user
    user = UserModel.find_by_username(username)
    
    if not user:
        return jsonify({
            'success': False,
            'message': 'Invalid username or password'
        }), 401
    
    # Check if account is active
    if not user.get('is_active', True):
        return jsonify({
            'success': False,
            'message': 'Account is deactivated. Contact admin.'
        }), 403
    
    # Verify password using bcrypt from app extensions
    from flask_bcrypt import check_password_hash
    if not check_password_hash(user['password_hash'], password):
        return jsonify({
            'success': False,
            'message': 'Invalid username or password'
        }), 401
    
    # Optional role verification
    if role and user.get('role') != role:
        return jsonify({
            'success': False,
            'message': f'Invalid role. User is not a {role}'
        }), 403
    
    # Update last login
    UserModel.update_last_login(str(user['_id']))
    
    # Create tokens
    access_token = create_access_token(
        identity=str(user['_id']),
        expires_delta=timedelta(hours=24),
        additional_claims={
            'role': user.get('role'),
            'username': user.get('username'),
            'name': f"{user.get('profile', {}).get('first_name', '')} {user.get('profile', {}).get('last_name', '')}".strip()
        }
    )
    
    refresh_token = create_refresh_token(
        identity=str(user['_id']),
        expires_delta=timedelta(days=30)
    )
    
    # Prepare response data based on role
    user_data = {
        'id': str(user['_id']),
        'username': user.get('username'),
        'email': user.get('email'),
        'role': user.get('role'),
        'name': f"{user.get('profile', {}).get('first_name', '')} {user.get('profile', {}).get('last_name', '')}".strip(),
        'is_verified': user.get('is_verified', False)
    }
    
    # Add role-specific data
    role_specific = user.get('role_specific', {})
    if user.get('role') == 'parent':
        user_data['student_reg_no'] = role_specific.get('student_reg_no')
        user_data['relationship'] = role_specific.get('relationship')
    elif user.get('role') == 'student':
        user_data['student_reg_no'] = role_specific.get('student_reg_no')
    elif user.get('role') == 'faculty':
        user_data['employee_id'] = role_specific.get('employee_id')
        user_data['department'] = role_specific.get('department')
    
    return jsonify({
        'success': True,
        'message': 'Login successful',
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user_data
    }), 200


@auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh_token():
    """Refresh access token"""
    current_user_id = get_jwt_identity()
    user = UserModel.find_by_id(current_user_id)
    
    if not user or not user.get('is_active', True):
        return jsonify({
            'success': False,
            'message': 'User not found or inactive'
        }), 401
    
    access_token = create_access_token(
        identity=current_user_id,
        expires_delta=timedelta(hours=24),
        additional_claims={
            'role': user.get('role'),
            'username': user.get('username')
        }
    )
    
    return jsonify({
        'success': True,
        'access_token': access_token
    }), 200


@auth_bp.route('/logout', methods=['POST'])
@jwt_required()
def logout():
    """Logout endpoint"""
    response = jsonify({
        'success': True,
        'message': 'Logout successful'
    })
    unset_jwt_cookies(response)
    return response, 200


@auth_bp.route('/verify-reg', methods=['POST'])
@validate_json(['reg_no'])
def verify_registration():
    """Verify student registration number before login"""
    data = request.get_json()
    reg_no = data.get('reg_no', '').strip().upper()
    
    # Check if student exists
    student = StudentModel.find_by_reg_no(reg_no)
    
    if not student:
        return jsonify({
            'success': False,
            'message': 'Student not found. Please check your registration number.'
        }), 404
    
    # Check if student has a linked parent account
    parent_user = None
    parent_phone = student.get('family', {}).get('parent_phone', '')
    
    if parent_phone:
        # Check for existing parent user
        users = UserModel.find_by_role('parent', skip=0, limit=1000)
        for user in users:
            if user.get('role_specific', {}).get('student_reg_no') == reg_no:
                parent_user = user
                break
    
    return jsonify({
        'success': True,
        'message': 'Student found',
        'student': {
            'reg_no': student.get('reg_no'),
            'name': f"{student.get('personal_info', {}).get('first_name', '')} {student.get('personal_info', {}).get('last_name', '')}".strip(),
            'branch': student.get('academic', {}).get('branch'),
            'year': student.get('academic', {}).get('year'),
            'parent_phone': parent_phone
        },
        'parent_registered': parent_user is not None
    }), 200


@auth_bp.route('/send-otp', methods=['POST'])
@validate_json(['reg_no', 'phone'])
def send_otp():
    """Send OTP to parent's registered phone"""
    data = request.get_json()
    reg_no = data.get('reg_no', '').strip().upper()
    phone = data.get('phone', '').strip()
    
    # Verify student exists
    student = StudentModel.find_by_reg_no(reg_no)
    if not student:
        return jsonify({
            'success': False,
            'message': 'Student not found'
        }), 404
    
    # Verify phone matches registered parent phone
    registered_phone = student.get('family', {}).get('parent_phone', '')
    if phone != registered_phone:
        return jsonify({
            'success': False,
            'message': 'Phone number does not match registered parent phone'
        }), 403
    
    # Generate OTP
    otp_code = generate_otp()
    
    # Store OTP (associated with registration number)
    # In production, this would be stored securely with expiry
    otp_key = f"otp_{reg_no}"
    
    # Send OTP via SMS
    # In development/demo mode, return OTP in response
    # In production, this would send actual SMS
    message = f"Your EduParent verification code is: {otp_code}. Valid for 5 minutes. Do not share with anyone."
    
    # Store in user model if parent user exists
    parent_users = UserModel.find_by_role('parent', skip=0, limit=1000)
    for user in parent_users:
        if user.get('role_specific', {}).get('student_reg_no') == reg_no:
            UserModel.store_otp(user.get('username'), otp_code)
            break
    
    return jsonify({
        'success': True,
        'message': 'OTP sent successfully',
        'demo_otp': otp_code,  # Only for demo/testing
        'expiry_minutes': 5
    }), 200


@auth_bp.route('/verify-otp', methods=['POST'])
@validate_json(['reg_no', 'phone', 'otp'])
def verify_otp_endpoint():
    """Verify OTP and complete login"""
    data = request.get_json()
    reg_no = data.get('reg_no', '').strip().upper()
    phone = data.get('phone', '').strip()
    otp = data.get('otp', '').strip()
    
    # Find parent user by student registration number
    parent_user = None
    users = UserModel.find_by_role('parent', skip=0, limit=1000)
    for user in users:
        if user.get('role_specific', {}).get('student_reg_no') == reg_no:
            parent_user = user
            break
    
    if not parent_user:
        return jsonify({
            'success': False,
            'message': 'Parent account not found. Please contact admin.'
        }), 404
    
    # Verify OTP
    is_valid, message = UserModel.verify_otp(parent_user.get('username'), otp)
    
    if not is_valid:
        return jsonify({
            'success': False,
            'message': message
        }), 401
    
    # Create tokens for automatic login
    access_token = create_access_token(
        identity=str(parent_user['_id']),
        expires_delta=timedelta(hours=24),
        additional_claims={
            'role': parent_user.get('role'),
            'username': parent_user.get('username')
        }
    )
    
    refresh_token = create_refresh_token(
        identity=str(parent_user['_id']),
        expires_delta=timedelta(days=30)
    )
    
    return jsonify({
        'success': True,
        'message': 'OTP verified successfully',
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': {
            'id': str(parent_user['_id']),
            'username': parent_user.get('username'),
            'role': parent_user.get('role'),
            'name': f"{parent_user.get('profile', {}).get('first_name', '')} {parent_user.get('profile', {}).get('last_name', '')}".strip(),
            'student_reg_no': parent_user.get('role_specific', {}).get('student_reg_no')
        }
    }), 200


@auth_bp.route('/change-password', methods=['POST'])
@jwt_required()
def change_password():
    """Change password"""
    data = request.get_json()
    current_password = data.get('current_password', '')
    new_password = data.get('new_password', '')
    
    # Validate new password
    if len(new_password) < 8:
        return jsonify({
            'success': False,
            'message': 'Password must be at least 8 characters long'
        }), 400
    
    # Get current user
    current_user_id = get_jwt_identity()
    user = UserModel.find_by_id(current_user_id)
    
    if not user:
        return jsonify({
            'success': False,
            'message': 'User not found'
        }), 404
    
    # Verify current password using bcrypt from app extensions
    from flask_bcrypt import check_password_hash, generate_password_hash
    if not check_password_hash(user['password_hash'], current_password):
        return jsonify({
            'success': False,
            'message': 'Current password is incorrect'
        }), 401
    
    # Hash new password
    new_password_hash = generate_password_hash(new_password).decode('utf-8')
    
    # Update password
    UserModel.update_user(current_user_id, {'password_hash': new_password_hash})
    
    return jsonify({
        'success': True,
        'message': 'Password changed successfully'
    }), 200


@auth_bp.route('/forgot-password', methods=['POST'])
@validate_json(['email'])
def forgot_password():
    """Request password reset"""
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    
    # Find user by email
    user = UserModel.find_by_email(email)
    
    if not user:
        # Don't reveal if email exists
        return jsonify({
            'success': True,
            'message': 'If your email is registered, you will receive a password reset link'
        }), 200
    
    # Generate reset token
    reset_token = create_access_token(
        identity=str(user['_id']),
        expires_delta=timedelta(hours=1),
        additional_claims={'type': 'password_reset'}
    )
    
    # Send reset email
    reset_url = f"https://yourdomain.com/reset-password?token={reset_token}"
    
    email_body = f"""
    Hello {user.get('profile', {}).get('first_name', 'User')},
    
    You requested a password reset for your EduParent account.
    
    Click the link below to reset your password:
    {reset_url}
    
    This link will expire in 1 hour.
    
    If you didn't request this, please ignore this email.
    
    Regards,
    EduParent Team
    """
    
    # In production, send actual email
    # send_email(user.get('email'), 'Password Reset Request', email_body)
    
    return jsonify({
        'success': True,
        'message': 'If your email is registered, you will receive a password reset link',
        'demo_reset_token': reset_token  # Only for demo
    }), 200


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    """Reset password with token"""
    data = request.get_json()
    token = data.get('token', '')
    new_password = data.get('new_password', '')
    
    # Validate new password
    if len(new_password) < 8:
        return jsonify({
            'success': False,
            'message': 'Password must be at least 8 characters long'
        }), 400
    
    try:
        # Decode token
        from flask_jwt_extended import decode_token
        decoded = decode_token(token)
        
        # Verify token type
        if decoded.get('type') != 'password_reset':
            raise ValueError('Invalid token type')
        
        user_id = decoded.get('sub')
        
        # Hash new password using bcrypt from app extensions
        from flask_bcrypt import generate_password_hash
        new_password_hash = generate_password_hash(new_password).decode('utf-8')
        
        # Update password
        UserModel.update_user(user_id, {'password_hash': new_password_hash})
        
        return jsonify({
            'success': True,
            'message': 'Password reset successfully'
        }), 200
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Invalid or expired token'
        }), 401


@auth_bp.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get current user profile"""
    current_user_id = get_jwt_identity()
    user = UserModel.find_by_id(current_user_id)
    
    if not user:
        return jsonify({
            'success': False,
            'message': 'User not found'
        }), 404
    
    profile = {
        'id': str(user['_id']),
        'username': user.get('username'),
        'email': user.get('email'),
        'role': user.get('role'),
        'profile': user.get('profile', {}),
        'is_verified': user.get('is_verified', False),
        'created_at': user.get('created_at'),
        'last_login': user.get('last_login')
    }
    
    # Add role-specific data
    role_specific = user.get('role_specific', {})
    if user.get('role') == 'parent':
        student = StudentModel.find_by_reg_no(role_specific.get('student_reg_no', ''))
        if student:
            profile['linked_student'] = {
                'reg_no': student.get('reg_no'),
                'name': f"{student.get('personal_info', {}).get('first_name', '')} {student.get('personal_info', {}).get('last_name', '')}".strip(),
                'branch': student.get('academic', {}).get('branch'),
                'year': student.get('academic', {}).get('year')
            }
    
    return jsonify({
        'success': True,
        'profile': profile
    }), 200


@auth_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile"""
    current_user_id = get_jwt_identity()
    data = request.get_json()
    
    # Allow updating only certain fields
    allowed_fields = ['first_name', 'last_name', 'phone', 'address', 'profile_image']
    profile_update = {}
    
    for field in allowed_fields:
        if field in data:
            profile_update[field] = data[field]
    
    if profile_update:
        UserModel.update_user(current_user_id, {'profile': profile_update})
    
    return jsonify({
        'success': True,
        'message': 'Profile updated successfully'
    }), 200


@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user (student, parent, faculty, or admin)"""
    data = request.get_json()
    
    # Required fields
    username = data.get('username', '').strip().lower()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    role = data.get('role', '')
    profile = data.get('profile', {})
    role_specific = data.get('role_specific', {})
    
    # Validate required fields
    if not username or not email or not password or not role:
        return jsonify({
            'success': False,
            'message': 'Username, email, password, and role are required'
        }), 400
    
    # Validate role
    valid_roles = ['student', 'parent', 'faculty', 'admin']
    if role not in valid_roles:
        return jsonify({
            'success': False,
            'message': f'Invalid role. Must be one of: {", ".join(valid_roles)}'
        }), 400
    
    # Validate password length
    if len(password) < 8:
        return jsonify({
            'success': False,
            'message': 'Password must be at least 8 characters long'
        }), 400
    
    # Validate email format
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return jsonify({
            'success': False,
            'message': 'Invalid email format'
        }), 400
    
    # Check if username already exists
    existing_user = UserModel.find_by_username(username)
    if existing_user:
        return jsonify({
            'success': False,
            'message': 'Username already exists. Please choose a different username.'
        }), 409
    
    # Check if email already exists
    existing_email = UserModel.find_by_email(email)
    if existing_email:
        return jsonify({
            'success': False,
            'message': 'Email already registered. Please use a different email or login.'
        }), 409
    
    # Role-specific validation
    if role == 'parent':
        student_reg_no = role_specific.get('student_reg_no')
        if not student_reg_no:
            return jsonify({
                'success': False,
                'message': 'Student registration number is required for parent registration'
            }), 400
        
        # Verify student exists
        student = StudentModel.find_by_reg_no(student_reg_no)
        if not student:
            return jsonify({
                'success': False,
                'message': 'Student not found. Please check the registration number.'
            }), 404
        
        # Check if parent already registered for this student
        existing_parents = UserModel.find_by_role('parent', skip=0, limit=1000)
        for p in existing_parents:
            if p.get('role_specific', {}).get('student_reg_no') == student_reg_no:
                return jsonify({
                    'success': False,
                    'message': 'A parent account is already linked to this student.'
                }), 409
    
    elif role == 'faculty':
        employee_id = role_specific.get('employee_id')
        if not employee_id:
            return jsonify({
                'success': False,
                'message': 'Employee ID is required for faculty registration'
            }), 400
        
        # Check if employee ID already exists
        existing_faculty = UserModel.find_by_role('faculty', skip=0, limit=1000)
        for f in existing_faculty:
            if f.get('role_specific', {}).get('employee_id') == employee_id:
                return jsonify({
                    'success': False,
                    'message': 'Employee ID already registered.'
                }), 409
    
    elif role == 'admin':
        # Admin registration requires a special code
        admin_code = data.get('admin_code', '')
        valid_admin_code = current_app.config.get('ADMIN_REGISTRATION_CODE', 'ADMIN2024')
        
        if admin_code != valid_admin_code:
            return jsonify({
                'success': False,
                'message': 'Invalid admin registration code. Contact system administrator.'
            }), 403
    
    # Hash password
    from flask_bcrypt import generate_password_hash
    password_hash = generate_password_hash(password).decode('utf-8')
    
    # Create user document
    user_doc = {
        'username': username,
        'email': email,
        'password_hash': password_hash,
        'role': role,
        'is_active': True,
        'is_verified': role == 'parent',  # Auto-verify parents for demo
        'profile': {
            'first_name': profile.get('first_name', ''),
            'last_name': profile.get('last_name', ''),
            'phone': profile.get('phone', '')
        },
        'role_specific': role_specific,
        'created_at': datetime.utcnow()
    }
    
    # Insert user
    try:
        user_id = UserModel.create_user(user_doc)
        
        return jsonify({
            'success': True,
            'message': 'Account created successfully! You can now login.',
            'user': {
                'id': str(user_id),
                'username': username,
                'email': email,
                'role': role
            }
        }), 201
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Registration failed: {str(e)}'
        }), 500
