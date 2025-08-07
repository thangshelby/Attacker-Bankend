#!/usr/bin/env python3
"""
Test script for MongoDB storage functionality
"""

import asyncio
import json
from app.database.mongodb import mongodb_config

async def test_mongodb():
    """Test MongoDB connection and operations"""
    print("🧪 Testing MongoDB Connection and Storage")
    print("=" * 50)
    
    # Test 1: Connection
    print("\n1. Testing MongoDB connection...")
    connected = await mongodb_config.test_connection()
    if connected:
        print("✅ MongoDB connection successful")
    else:
        print("❌ MongoDB connection failed")
        return
    
    # Test 2: Store sample conversation
    print("\n2. Testing conversation storage...")
    sample_result = {
        "request_id": "test-12345",
        "final_result": {
            "decision": "approve",
            "reason": "Good academic record and financial stability"
        },
        "processing_time_seconds": 2.5,
        "request_metadata": {
            "loan_amount": 50000000,
            "loan_purpose": "Học phí",
            "gpa_normalized": 0.85,
            "university_tier": 1
        }
    }
    
    sample_request = {
        "age": 21,
        "gender": "Nam",
        "major_category": "STEM",
        "loan_amount_requested": 50000000
    }
    
    stored_id = await mongodb_config.store_conversation(sample_result, sample_request)
    if stored_id:
        print(f"✅ Conversation stored with ID: {stored_id}")
    else:
        print("❌ Failed to store conversation")
        return
    
    # Test 3: Retrieve conversations
    print("\n3. Testing conversation retrieval...")
    conversations = await mongodb_config.get_conversations(5)
    print(f"✅ Retrieved {len(conversations)} conversations")
    
    if conversations:
        latest = conversations[0]
        print(f"   Latest conversation: {latest.get('request_id')} - {latest.get('decision')}")
    
    # Test 4: Get statistics
    print("\n4. Testing statistics...")
    stats = await mongodb_config.get_statistics()
    if stats:
        print("✅ Statistics retrieved:")
        for key, value in stats.items():
            print(f"   {key}: {value}")
    else:
        print("❌ Failed to get statistics")
    
    print("\n" + "=" * 50)
    print("🏁 MongoDB test completed!")

if __name__ == "__main__":
    asyncio.run(test_mongodb())
