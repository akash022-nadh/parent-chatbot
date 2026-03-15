#!/usr/bin/env python3
"""
Test admin login directly
"""

import sys
sys.path.insert(0, 'c:/Users/akash/OneDrive/Desktop/parent_chatbot')

from app import bcrypt
from app.models import UserModel

# Test password verification
test_password = 'admin123'

# Get admin user
user = UserModel.find_by_username('admin')
if user:
    print(f"Found user: {user.get('username')}")
    print(f"Role: {user.get('role')}")
    print(f"Password hash: {user.get('password_hash')}")
    
    # Test bcrypt verification
    stored_hash = user.get('password_hash')
    result = bcrypt.check_password_hash(stored_hash, test_password)
    print(f"\nPassword verification result: {result}")
    
    if not result:
        print("\n⚠️ Password mismatch! Generating new hash...")
        new_hash = bcrypt.generate_password_hash(test_password).decode('utf-8')
        print(f"New hash: {new_hash}")
        
        # Update in database
        from pymongo import MongoClient
        import os
        client = MongoClient(os.environ.get("MONGO_URI", "mongodb://localhost:27017/"))
        db = client[os.environ.get("DB_NAME", "school_chatbot")]
        db.users.update_one({"username": "admin"}, {"$set": {"password_hash": new_hash}})
        print("✅ Admin password updated in database!")
        
        # Verify again
        updated = db.users.find_one({"username": "admin"})
        verify = bcrypt.check_password_hash(updated['password_hash'], test_password)
        print(f"Verification after update: {verify}")
        client.close()
else:
    print("❌ Admin user not found!")
