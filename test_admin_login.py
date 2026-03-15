#!/usr/bin/env python3
"""
Test admin login API directly
"""

import requests
import json

BASE_URL = "http://127.0.0.1:5000"

print("Testing Admin Login API...")
print("=" * 50)

# Test admin login
data = {
    "username": "admin",
    "password": "admin123",
    "role": "admin"
}

try:
    print(f"Sending request to: {BASE_URL}/api/auth/login")
    print(f"Data: {json.dumps(data, indent=2)}")
    
    resp = requests.post(f"{BASE_URL}/api/auth/login", 
                        json=data, 
                        headers={"Content-Type": "application/json"},
                        timeout=5)
    
    print(f"\nStatus Code: {resp.status_code}")
    print(f"Response Headers: {dict(resp.headers)}")
    print(f"Response Body: {json.dumps(resp.json(), indent=2)}")
    
except requests.exceptions.ConnectionError as e:
    print(f"❌ Connection Error: {e}")
    print("Server might not be running or wrong port")
except requests.exceptions.Timeout as e:
    print(f"❌ Timeout Error: {e}")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 50)
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
