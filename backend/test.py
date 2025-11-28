"""
Diagnostic Test Script for Taper Plan Endpoint
Run this to identify the exact cause of the 500 error
"""

import sys
import os
import traceback
import pandas as pd
from pathlib import Path


# Test 10: Test API Endpoint with HTTP Request
print("TEST 10: Test API Endpoint (HTTP)")
print("-" * 80)

try:
    import requests
    import time
    
    print("Checking if API server is running...")
    
    try:
        # Try to connect to running server
        response = requests.get("http://localhost:8000/health", timeout=2)
        
        if response.status_code == 200:
            print("✓ API server is running!")
            print(f"  Response: {response.json()}")
            
            # Test taper plan endpoint
            print("\nTesting /get-taper-plan endpoint...")
            test_payload = {
                "drug_name": "Omeprazole",
                "current_dose": "20mg",
                "duration_on_medication": "long_term",
                "patient_age": 70,
                "comorbidities": []
            }
            
            response = requests.post(
                "http://localhost:8000/get-taper-plan",
                json=test_payload,
                timeout=5
            )
            
            if response.status_code == 200:
                print(f"✓ Taper plan endpoint working!")
                data = response.json()
                print(f"  Generated plan for: {data['drug_name']}")
                print(f"  Steps: {len(data['steps'])}")
            else:
                print(f"✗ Taper plan endpoint failed: {response.status_code}")
                print(f"  Error: {response.text[:200]}")
        else:
            print(f"✗ API server returned: {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("⚠ API server is NOT running")
        print("  Start it with: uvicorn app.main:app --reload")
        print("  Then run this test again")
    
    print()
    
except Exception as e:
    print(f"✗ Endpoint test error: {e}")
    traceback.print_exc()
    print()

