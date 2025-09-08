#!/usr/bin/env python3
"""
Script để start cả FastAPI và gRPC servers cùng lúc
"""

import subprocess
import threading
import time
import signal
import sys
import os

def start_fastapi():
    """Start FastAPI server"""
    print("🌐 Starting FastAPI server on port 8000...")
    return subprocess.Popen([
        sys.executable, "-m", "uvicorn", 
        "main_fastapi:app", 
        "--host", "0.0.0.0", 
        "--port", "8000",
        "--reload"
    ])

def start_grpc():
    """Start gRPC server"""  
    print("📡 Starting gRPC server on port 50051...")
    # Resolve full path to main_grpc.py to ensure it's found regardless of cwd
    script_dir = os.path.dirname(os.path.abspath(__file__))
    grpc_script = os.path.join(script_dir, "main_grpc.py")
    return subprocess.Popen([
        sys.executable, grpc_script
    ])

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n🛑 Shutting down servers...")
    
    # Terminate processes
    if 'fastapi_process' in globals():
        fastapi_process.terminate()
    if 'grpc_process' in globals():
        grpc_process.terminate()
    
    # Wait for clean shutdown
    time.sleep(2)
    sys.exit(0)

if __name__ == "__main__":
    # Register signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("🚀 Starting Python Chatbot Services...")
    print("=" * 50)
    
    # Start both servers
    fastapi_process = start_fastapi()
    time.sleep(2)  # Give FastAPI time to start
    
    grpc_process = start_grpc()
    time.sleep(2)  # Give gRPC time to start
    
    print("=" * 50)
    print("✅ Services started successfully!")
    print("🌐 FastAPI: http://localhost:8000")
    print("📡 gRPC: localhost:50051")
    print("📖 API Docs: http://localhost:8000/docs")
    print("\nPress Ctrl+C to stop all services...")
    print("=" * 50)
    
    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
            
            # Check if processes are still running
            if fastapi_process.poll() is not None:
                print("❌ FastAPI process died, restarting...")
                fastapi_process = start_fastapi()
                
            if grpc_process.poll() is not None:
                print("❌ gRPC process died, restarting...")
                grpc_process = start_grpc()
                
    except KeyboardInterrupt:
        signal_handler(signal.SIGINT, None)