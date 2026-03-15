#!/usr/bin/env python3
"""
Debug admin login - check database and bcrypt
"""

import sys
sys.path.insert(0, 'c:/Users/akash/OneDrive/Desktop/parent_chatbot')

from pymongo import MongoClient
from app import bcrypt
import os

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
DB_NAME = os.environ.get("DB_NAME", "school_chatbot")

print(f"Using database: {DB_NAME}")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# List all databases
print("\nAll databases:")
for db_name in client.list_database_names():
    print(f"  - {db_name}")

# Check users collection
print(f"\nUsers in '{DB_NAME}':")
users = list(db.users.find())
for u in users:
    print(f"  - {u.get('username')} ({u.get('role')})")
    print(f"    Hash: {u.get('password_hash', 'NO HASH')[:60]}...")

# Test admin login
admin = db.users.find_one({"username": "admin"})
if admin:
    print(f"\nTesting password 'admin123' against hash...")
    result = bcrypt.check_password_hash(admin['password_hash'], 'admin123')
    print(f"Result: {result}")
else:
    print("\n❌ Admin user not found!")

client.close()
