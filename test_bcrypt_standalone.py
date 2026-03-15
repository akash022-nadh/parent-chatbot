#!/usr/bin/env python3
"""
Test bcrypt exactly as auth.py uses it
"""

import sys
sys.path.insert(0, 'c:/Users/akash/OneDrive/Desktop/parent_chatbot')

from pymongo import MongoClient
from flask_bcrypt import check_password_hash, generate_password_hash
import os

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.environ.get("DB_NAME", "school_chatbot")

print(f"Using database: {DB_NAME}")
print(f"Testing with standalone check_password_hash (like auth.py uses)")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# Test admin login
admin = db.users.find_one({"username": "admin"})
if admin:
    print(f"\nAdmin found: {admin['username']}")
    print(f"Hash: {admin['password_hash'][:50]}...")
    
    # Test with standalone function (like auth.py)
    result = check_password_hash(admin['password_hash'], 'admin123')
    print(f"Standalone check_password_hash result: {result}")
    
    # Generate a new hash with standalone function
    new_hash = generate_password_hash('admin123').decode('utf-8')
    print(f"New hash generated: {new_hash[:50]}...")
    
    # Verify the new hash
    result2 = check_password_hash(new_hash, 'admin123')
    print(f"Verify new hash: {result2}")
    
    # Update admin with new hash
    db.users.update_one(
        {"username": "admin"},
        {"$set": {"password_hash": new_hash}}
    )
    print("Updated admin password hash in database")
else:
    print("Admin not found!")

client.close()
