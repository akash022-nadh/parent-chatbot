#!/usr/bin/env python3
"""
Test all login APIs to debug issues
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_login(username, password, role, description):
    print(f"\n{'='*60}")
    print(f"Testing {description}")
    print(f"URL: {BASE_URL}/api/auth/login")
    print(f"Credentials: {username} / {password} / {role}")
    
    data = {
        "username": username,
        "password": password,
        "role": role
    }
    
    try:
        resp = requests.post(f"{BASE_URL}/api/auth/login", 
                           json=data, 
                           headers={"Content-Type": "application/json"},
                           timeout=5)
        
        print(f"Status Code: {resp.status_code}")
        print(f"Response: {json.dumps(resp.json(), indent=2)}")
        
        if resp.status_code == 200 and resp.json().get('success'):
            print(f"✅ {description} - SUCCESS")
        else:
            print(f"❌ {description} - FAILED")
            
    except requests.exceptions.ConnectionError:
        print(f"❌ {description} - CONNECTION ERROR")
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")

print("Testing All Login APIs...")
print("="*60)

# Test admin login
test_login("admin", "admin123", "admin", "Admin Login")

# Test student login
test_login("student001", "student123", "student", "Student Login")

# Test faculty login
test_login("faculty001", "faculty123", "faculty", "Faculty Login")

print(f"\n{'='*60}")
print("Testing basic server connectivity...")
try:
    resp = requests.get(f"{BASE_URL}/", timeout=5)
    print(f"Home page Status: {resp.status_code}")
    if resp.status_code == 200:
        print("✅ Server is responding")
    else:
        print(f"⚠️ Server responding with status {resp.status_code}")
except Exception as e:
    print(f"❌ Server not reachable: {e}")
