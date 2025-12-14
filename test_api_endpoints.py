#!/usr/bin/env python3
"""
API Endpoint Testing Script
Tests all main endpoints of the NyxOS AI Engine API
"""

import requests
import json
import time

API_BASE = "http://localhost:8000"

def test_health():
    """Test the health endpoint."""
    print("\n" + "="*60)
    print("TEST 1: Health Endpoint")
    print("="*60)
    try:
        response = requests.get(f"{API_BASE}/health")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_chat():
    """Test the chat endpoint."""
    print("\n" + "="*60)
    print("TEST 2: Chat Endpoint")
    print("="*60)
    try:
        payload = {
            "message": "Hello, how are you?",
            "use_context": True,
            "temperature": 1.0
        }
        response = requests.post(f"{API_BASE}/chat", json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Request: {json.dumps(payload, indent=2)}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_assistant():
    """Test the assistant endpoint."""
    print("\n" + "="*60)
    print("TEST 3: Assistant Endpoint")
    print("="*60)
    try:
        payload = {
            "message": "Create a file named test.txt"
        }
        response = requests.post(f"{API_BASE}/assistant", json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Request: {json.dumps(payload, indent=2)}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_context_clear():
    """Test the context clear endpoint."""
    print("\n" + "="*60)
    print("TEST 4: Context Clear Endpoint")
    print("="*60)
    try:
        response = requests.post(f"{API_BASE}/context/clear")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_context_history():
    """Test the context history endpoint."""
    print("\n" + "="*60)
    print("TEST 5: Context History Endpoint")
    print("="*60)
    try:
        response = requests.get(f"{API_BASE}/context/history")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("NyxOS AI Engine - API Endpoint Tests")
    print("="*60)
    print(f"Testing endpoints at: {API_BASE}")
    
    # Wait a moment for server to start if it's just starting
    time.sleep(2)
    
    results = []
    
    # Run tests
    results.append(("Health Check", test_health()))
    results.append(("Chat Endpoint", test_chat()))
    results.append(("Assistant Endpoint", test_assistant()))
    results.append(("Context Clear", test_context_clear()))
    results.append(("Context History", test_context_history()))
    
    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{name}: {status}")
    
    total = len(results)
    passed = sum(1 for _, p in results if p)
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your AI Engine is working perfectly!")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Check the errors above.")
    
    print("="*60)

if __name__ == "__main__":
    main()
