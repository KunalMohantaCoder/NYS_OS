#!/usr/bin/env python3
"""
Interactive NyxOS AI Assistant Tester
Allows you to test various Assistant commands
"""

import requests
import json

API_URL = "http://localhost:8000/assistant"

def send_command(command):
    """Send a command to the Assistant and display the response."""
    try:
        payload = {"message": command}
        response = requests.post(API_URL, json=payload)
        result = response.json()
        
        print("\n" + "="*60)
        print(f"Command: {command}")
        print("="*60)
        print(f"Intent: {result.get('intent', 'unknown')}")
        print(f"Success: {result.get('success', False)}")
        print(f"Message: {result.get('message', 'No message')}")
        if result.get('data'):
            print(f"Data: {json.dumps(result.get('data'), indent=2)}")
        print("="*60 + "\n")
        
        return result
    except Exception as e:
        print(f"Error: {e}\n")
        return None

def main():
    """Interactive Assistant tester."""
    print("\n" + "="*60)
    print("NyxOS AI Assistant - Interactive Tester")
    print("="*60)
    print("\nAvailable commands:")
    print("  File Operations:")
    print("    - 'create a file named filename.txt'")
    print("    - 'read the file filename.txt'")
    print("    - 'list all files'")
    print("    - 'delete filename.txt'")
    print("\n  Folder Operations:")
    print("    - 'create a folder named foldername'")
    print("\n  Calendar:")
    print("    - 'add event tomorrow at 2pm'")
    print("    - 'show my schedule'")
    print("\n  System:")
    print("    - 'what time is it'")
    print("    - 'execute dir' (list directory)")
    print("\nType 'quit' or 'exit' to stop\n")
    
    while True:
        try:
            command = input("Enter command: ").strip()
            
            if not command:
                continue
                
            if command.lower() in ['quit', 'exit', 'q']:
                print("Goodbye!")
                break
            
            send_command(command)
            
        except KeyboardInterrupt:
            print("\n\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}\n")

if __name__ == "__main__":
    main()
