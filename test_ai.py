#!/usr/bin/env python3
"""
Simple test script for the AI service.
"""
import sys
import json

# Try to import requests, with fallback for urllib
try:
    import requests
    USE_REQUESTS = True
except ImportError as e:
    print(f"Warning: requests not available ({e})")
    print("Falling back to urllib...")
    USE_REQUESTS = False
    try:
        import urllib.request
        import urllib.parse
        import urllib.error
    except ImportError:
        print("Error: Neither requests nor urllib available")
        sys.exit(1)

API_BASE = "http://localhost:8000"

def test_health():
    """Test health endpoint."""
    print("Testing health endpoint...")
    try:
        if USE_REQUESTS:
            response = requests.get(f"{API_BASE}/health")
            print(f"  Status: {response.status_code}")
            print(f"  Response: {response.json()}")
            return response.status_code == 200
        else:
            req = urllib.request.Request(f"{API_BASE}/health")
            with urllib.request.urlopen(req, timeout=5) as response:
                status = response.getcode()
                data = json.loads(response.read().decode())
                print(f"  Status: {status}")
                print(f"  Response: {data}")
                return status == 200
    except Exception as e:
        print(f"  Error: {e}")
        return False

def test_chat(message):
    """Test chat endpoint."""
    print(f"\nTesting chat with: '{message}'")
    try:
        payload = json.dumps({"message": message, "temperature": 1.0}).encode('utf-8')
        
        if USE_REQUESTS:
            response = requests.post(
                f"{API_BASE}/chat",
                json={"message": message, "temperature": 1.0}
            )
            print(f"  Status: {response.status_code}")
            data = response.json()
            print(f"  Response: {data.get('response', 'No response')}")
            return response.status_code == 200
        else:
            req = urllib.request.Request(
                f"{API_BASE}/chat",
                data=payload,
                headers={'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req, timeout=30) as response:
                status = response.getcode()
                data = json.loads(response.read().decode())
                print(f"  Status: {status}")
                print(f"  Response: {data.get('response', 'No response')}")
                return status == 200
    except Exception as e:
        print(f"  Error: {e}")
        return False

def test_assistant(message):
    """Test assistant endpoint."""
    print(f"\nTesting assistant with: '{message}'")
    try:
        payload = json.dumps({"message": message}).encode('utf-8')
        
        if USE_REQUESTS:
            response = requests.post(
                f"{API_BASE}/assistant",
                json={"message": message}
            )
            print(f"  Status: {response.status_code}")
            data = response.json()
        else:
            req = urllib.request.Request(
                f"{API_BASE}/assistant",
                data=payload,
                headers={'Content-Type': 'application/json'}
            )
            with urllib.request.urlopen(req, timeout=30) as response:
                status = response.getcode()
                data = json.loads(response.read().decode())
                print(f"  Status: {status}")
        
        print(f"  Intent: {data.get('intent', 'unknown')}")
        print(f"  Message: {data.get('message', 'No message')}")
        if data.get('data'):
            print(f"  Data: {data.get('data')}")
        return True
    except Exception as e:
        print(f"  Error: {e}")
        return False

def main():
    print("=" * 60)
    print("NyxOS AI Service Test")
    print("=" * 60)
    
    # Test health
    if not test_health():
        print("\n[X] Health check failed. Is the AI service running?")
        print("   Start it with: python -m api.server")
        return
    
    print("\n[OK] Health check passed!")
    
    # Test chat
    test_chat("Hello, how are you?")
    test_chat("What can you do?")
    
    # Test assistant
    test_assistant("list files")
    test_assistant("what time is it")
    test_assistant("create a file called test.txt")
    
    print("\n" + "=" * 60)
    print("Tests completed!")
    print("=" * 60)

if __name__ == "__main__":
    main()

