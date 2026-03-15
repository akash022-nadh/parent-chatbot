#!/usr/bin/env python3
"""
Create admin user with proper Flask context
"""

import sys
sys.path.insert(0, 'c:/Users/akash/OneDrive/Desktop/parent_chatbot')

from app import bcrypt
from pymongo import MongoClient
from datetime import datetime
import os

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.environ.get("DB_NAME", "school_chatbot")

def create_users():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    
    # Drop users collection
    db.users.drop()
    
    # Create users with properly hashed passwords using Flask bcrypt
    users = [
        {
            "username": "admin",
            "email": "admin@college.edu",
            "password_hash": bcrypt.generate_password_hash('admin123').decode('utf-8'),
            "role": "admin",
            "is_active": True,
            "is_verified": True,
            "profile": {
                "first_name": "System",
                "last_name": "Administrator",
                "phone": "9000000000"
            },
            "created_at": datetime.utcnow()
        },
        {
            "username": "faculty001",
            "email": "faculty@college.edu",
            "password_hash": bcrypt.generate_password_hash('faculty123').decode('utf-8'),
            "role": "faculty",
            "is_active": True,
            "is_verified": True,
            "profile": {
                "first_name": "Dr. R.",
                "last_name": "Sharma",
                "phone": "9001111111"
            },
            "role_specific": {
                "employee_id": "FAC001",
                "department": "CSE",
                "designation": "Professor"
            },
            "created_at": datetime.utcnow()
        },
        {
            "username": "student001",
            "email": "student@college.edu",
            "password_hash": bcrypt.generate_password_hash('student123').decode('utf-8'),
            "role": "student",
            "is_active": True,
            "is_verified": True,
            "profile": {
                "first_name": "Arjun",
                "last_name": "Mehta",
                "phone": "9876543210"
            },
            "role_specific": {
                "student_reg_no": "STU001"
            },
            "created_at": datetime.utcnow()
        },
        {
            "username": "parent001",
            "email": "parent@email.com",
            "password_hash": bcrypt.generate_password_hash('parent123').decode('utf-8'),
            "role": "parent",
            "is_active": True,
            "is_verified": True,
            "profile": {
                "first_name": "Suresh",
                "last_name": "Mehta",
                "phone": "9876543211"
            },
            "role_specific": {
                "student_reg_no": "STU001",
                "relationship": "Father"
            },
            "created_at": datetime.utcnow()
        }
    ]
    
    db.users.insert_many(users)
    
    # Verify admin was created
    admin = db.users.find_one({"username": "admin"})
    if admin:
        print(f"✅ Admin user created: {admin['username']}")
        print(f"   Password hash: {admin['password_hash'][:50]}...")
        
        # Test password verification
        verify = bcrypt.check_password_hash(admin['password_hash'], 'admin123')
        print(f"   Password verification: {verify}")
    else:
        print("❌ Failed to create admin user!")
    
    client.close()
    print("\n✅ All users created successfully!")
    print("\nLogin credentials:")
    print("  Admin:    admin / admin123")
    print("  Faculty:  faculty001 / faculty123")
    print("  Student:  student001 / student123")
    print("  Parent:   parent001 / parent123")

if __name__ == "__main__":
    create_users()
