#!/usr/bin/env python3
"""
Test login API directly
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000"

print("Testing Admin Login...")
print("=" * 50)

# Test admin login
data = {
    "username": "admin",
    "password": "admin123",
    "role": "admin"
}

try:
    resp = requests.post(f"{BASE_URL}/api/auth/login", 
                        json=data, 
                        headers={"Content-Type": "application/json"},
                        timeout=5)
    print(f"Status Code: {resp.status_code}")
    print(f"Response: {json.dumps(resp.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 50)
print("Testing Faculty Login...")

# Test faculty login
data = {
    "username": "faculty001",
    "password": "faculty123",
    "role": "faculty"
}

try:
    resp = requests.post(f"{BASE_URL}/api/auth/login", 
                        json=data, 
                        headers={"Content-Type": "application/json"},
                        timeout=5)
    print(f"Status Code: {resp.status_code}")
    print(f"Response: {json.dumps(resp.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 50)
print("Testing Student Login...")

# Test student login
data = {
    "username": "student001",
    "password": "student123",
    "role": "student"
}

try:
    resp = requests.post(f"{BASE_URL}/api/auth/login", 
                        json=data, 
                        headers={"Content-Type": "application/json"},
                        timeout=5)
    print(f"Status Code: {resp.status_code}")
    print(f"Response: {json.dumps(resp.json(), indent=2)}")
except Exception as e:
    print(f"Error: {e}")
