#!/usr/bin/env python3
"""Test login endpoint to verify credentials."""
import requests
import json

BASE_URL = 'http://localhost:8000'

# Test 1: GET login page
print("=" * 60)
print("Test 1: GET /login")
try:
    r = requests.get(f'{BASE_URL}/login', timeout=5)
    print(f"Status: {r.status_code}")
    print(f"Contains login form: {'form' in r.text.lower()}")
except Exception as e:
    print(f"Error: {e}")

# Test 2: POST with correct JSON credentials
print("\n" + "=" * 60)
print("Test 2: POST /login with correct JSON credentials")
try:
    r = requests.post(f'{BASE_URL}/login', 
        json={'username': 'leblanc', 'password': 'the pale woman'},
        timeout=5)
    print(f"Status: {r.status_code}")
    print(f"Response: {r.text[:200]}")
    if r.status_code == 200:
        print("✓ LOGIN SUCCESSFUL")
except Exception as e:
    print(f"Error: {e}")

# Test 3: POST with wrong credentials
print("\n" + "=" * 60)
print("Test 3: POST /login with wrong credentials")
try:
    r = requests.post(f'{BASE_URL}/login',
        json={'username': 'test', 'password': 'wrong'},
        timeout=5)
    print(f"Status: {r.status_code}")
    if r.status_code == 401:
        print("✓ CORRECTLY REJECTED WRONG CREDENTIALS")
except Exception as e:
    print(f"Error: {e}")

# Test 4: Check if auth cookie is set
print("\n" + "=" * 60)
print("Test 4: Check auth cookie after successful login")
try:
    session = requests.Session()
    r = session.post(f'{BASE_URL}/login',
        json={'username': 'leblanc', 'password': 'the pale woman'},
        timeout=5)
    print(f"Login Status: {r.status_code}")
    print(f"Cookies: {session.cookies.get_dict()}")
    
    # Try to access main page
    r2 = session.get(f'{BASE_URL}/', timeout=5)
    print(f"Main page Status: {r2.status_code}")
    if r2.status_code == 200 and 'Trading Monitor' in r2.text:
        print("✓ AUTH COOKIE WORKS - CAN ACCESS MAIN PAGE")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 60)
print("Tests complete!")
