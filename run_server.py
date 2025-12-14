#!/usr/bin/env python3
"""
Simple script to run the API server.
"""
import sys
import os

# Add current directory to path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)
os.chdir(script_dir)  # Change to script directory so relative paths work

if __name__ == "__main__":
    from api.server import app
    import uvicorn
    
    print(f"Starting NyxOS AI Engine API Server...")
    print(f"Working directory: {os.getcwd()}")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
