#!/usr/bin/env python3
"""
gRPC Server cho Python Chatbot Service
Chạy cùng với FastAPI server để provide cả REST và gRPC interfaces
"""

from app.grpc.server import serve

if __name__ == "__main__":
    print("🚀 Starting gRPC Chatbot Server...")
    serve()