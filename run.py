#!/usr/bin/env python3
"""
Student Academic Monitoring System (SAMS)
Main entry point for the application
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app import create_app, db
from models import UserModel, StudentModel, FacultyModel
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

def create_app_instance():
    """Create Flask application instance"""
    env = os.getenv('FLASK_ENV', 'development')
    app = create_app(env)
    return app


def init_database():
    """Initialize database with sample data"""
    print("Initializing database...")
    
    try:
        # Connect to database
        database = db.connect()
        
        # Check if we have any users
        user_count = database.users.count_documents({})
        
        if user_count == 0:
            print("Creating sample users...")
            
            # Create admin user
            admin_password = bcrypt.generate_password_hash('admin123').decode('utf-8')
            UserModel.create_user({
                'username': 'admin',
                'email': 'admin@college.edu',
                'password_hash': admin_password,
                'role': 'admin',
                'profile': {
                    'first_name': 'System',
                    'last_name': 'Administrator',
                    'phone': '9000000000'
                },
                'role_specific': {
                    'admin_level': 'super',
                    'permissions': ['all']
                },
                'is_verified': True
            })
            
            # Create sample faculty
            faculty_password = bcrypt.generate_password_hash('faculty123').decode('utf-8')
            UserModel.create_user({
                'username': 'faculty001',
                'email': 'faculty@college.edu',
                'password_hash': faculty_password,
                'role': 'faculty',
                'profile': {
                    'first_name': 'Dr. R.',
                    'last_name': 'Sharma',
                    'phone': '9001111111'
                },
                'role_specific': {
                    'employee_id': 'FAC001',
                    'department': 'CSE',
                    'designation': 'Professor'
                },
                'is_verified': True
            })
            
            # Create sample student
            student_password = bcrypt.generate_password_hash('student123').decode('utf-8')
            UserModel.create_user({
                'username': 'student001',
                'email': 'student@college.edu',
                'password_hash': student_password,
                'role': 'student',
                'profile': {
                    'first_name': 'Arjun',
                    'last_name': 'Mehta',
                    'phone': '9876543210'
                },
                'role_specific': {
                    'student_reg_no': 'STU001'
                },
                'is_verified': True
            })
            
            # Create sample parent
            parent_password = bcrypt.generate_password_hash('parent123').decode('utf-8')
            UserModel.create_user({
                'username': 'parent001',
                'email': 'parent@email.com',
                'password_hash': parent_password,
                'role': 'parent',
                'profile': {
                    'first_name': 'Suresh',
                    'last_name': 'Mehta',
                    'phone': '9876543211'
                },
                'role_specific': {
                    'student_reg_no': 'STU001',
                    'relationship': 'Father'
                },
                'is_verified': True
            })
            
            # Create sample student record
            StudentModel.create_student({
                'reg_no': 'STU001',
                'roll_no': '22CS101',
                'personal_info': {
                    'first_name': 'Arjun',
                    'last_name': 'Mehta',
                    'date_of_birth': '2003-05-15',
                    'gender': 'Male',
                    'blood_group': 'B+',
                    'email': 'arjun@student.college.edu',
                    'phone': '9876543210'
                },
                'academic': {
                    'branch': 'CSE',
                    'year': 3,
                    'semester': 6,
                    'section': 'A',
                    'cgpa': 8.2,
                    'backlogs': 0,
                    'course_status': 'Active'
                },
                'family': {
                    'father_name': 'Suresh Mehta',
                    'mother_name': 'Lata Mehta',
                    'parent_phone': '9876543211',
                    'parent_email': 'parent@email.com'
                },
                'advisor': {
                    'name': 'Dr. R. Sharma',
                    'email': 'r.sharma@college.edu',
                    'phone': '9001111111'
                }
            })
            
            # Create sample faculty record
            FacultyModel.create_faculty({
                'employee_id': 'FAC001',
                'personal_info': {
                    'first_name': 'Dr. R.',
                    'last_name': 'Sharma',
                    'email': 'r.sharma@college.edu',
                    'phone': '9001111111',
                    'gender': 'Male',
                    'qualification': 'Ph.D. in Computer Science',
                    'experience_years': 15
                },
                'contact': {
                    'email': 'r.sharma@college.edu',
                    'phone': '9001111111',
                    'cabin': 'Block A, Room 101',
                    'office_hours': 'Mon-Fri 2PM-4PM'
                },
                'department': 'CSE',
                'designation': 'Professor & HOD',
                'subjects': [
                    {'code': 'CS301', 'name': 'DBMS', 'semester': [5, 6]},
                    {'code': 'CS401', 'name': 'Advanced DBMS', 'semester': [7]}
                ],
                'is_advisor': True,
                'joining_date': '2010-07-01'
            })
            
            print("✓ Sample data created successfully!")
            print("\nDefault login credentials:")
            print("  Admin:    admin / admin123")
            print("  Faculty:  faculty001 / faculty123")
            print("  Student:  student001 / student123")
            print("  Parent:   parent001 / parent123")
            
        else:
            print(f"✓ Database already initialized with {user_count} users")
            
    except Exception as e:
        print(f"✗ Error initializing database: {str(e)}")
        import traceback
        traceback.print_exc()


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Student Academic Monitoring System')
    parser.add_argument('--init-db', action='store_true', help='Initialize database with sample data')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')
    
    args = parser.parse_args()
    
    if args.init_db:
        init_database()
        return
    
    # Create and run app
    app = create_app_instance()
    
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║     Student Academic Monitoring System (SAMS)               ║
║                                                              ║
║  🌐 Server: http://{args.host}:{args.port}                            ║
║  📚 API Docs: http://{args.host}:{args.port}/api/docs                 ║
║                                                              ║
║  User Roles:                                                 ║
║    • Admin:    admin/admin123                               ║
║    • Faculty:  faculty001/faculty123                        ║
║    • Parent:   parent001/parent123                          ║
║    • Student:  student001/student123                        ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    app.run(
        host=args.host,
        port=args.port,
        debug=args.debug or os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    )


if __name__ == '__main__':
    main()
