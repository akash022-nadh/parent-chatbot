#!/usr/bin/env python3
"""
Fix admin user password - direct database update
"""

import sys
sys.path.append('app')

from pymongo import MongoClient
from flask_bcrypt import Bcrypt
import os

# MongoDB connection
MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.environ.get("DB_NAME", "school_chatbot")

bcrypt = Bcrypt()

def fix_admin():
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    
    # Generate new hash
    password = 'admin123'
    password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
    
    print(f"Generated hash for '{password}': {password_hash}")
    
    # Check if admin exists
    admin = db.users.find_one({"username": "admin"})
    
    if admin:
        print(f"Found admin user: {admin.get('username')}")
        print(f"Current hash: {admin.get('password_hash')}")
        
        # Update password
        result = db.users.update_one(
            {"username": "admin"},
            {"$set": {"password_hash": password_hash}}
        )
        
        print(f"Updated {result.modified_count} document(s)")
        
        # Verify update
        updated = db.users.find_one({"username": "admin"})
        print(f"New hash: {updated.get('password_hash')}")
        
        # Test verification
        from flask_bcrypt import check_password_hash
        verify = check_password_hash(updated['password_hash'], 'admin123')
        print(f"Password verification test: {verify}")
    else:
        print("Admin user not found! Creating new admin...")
        from datetime import datetime
        
        admin_user = {
            "username": "admin",
            "email": "admin@college.edu",
            "password_hash": password_hash,
            "role": "admin",
            "is_active": True,
            "is_verified": True,
            "profile": {
                "first_name": "System",
                "last_name": "Administrator",
                "phone": "9000000000"
            },
            "created_at": datetime.utcnow()
        }
        
        db.users.insert_one(admin_user)
        print("Admin user created successfully!")
    
    client.close()
    print("\n✅ Admin password fixed!")
    print("You can now login with:")
    print("  Username: admin")
    print("  Password: admin123")

if __name__ == "__main__":
    fix_admin()
