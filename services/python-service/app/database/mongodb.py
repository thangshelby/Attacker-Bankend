"""
MongoDB configuration and utilities for MAS conversation storage
"""

import os
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import json
from typing import Dict, Any, Optional

class MongoDBConfig:
    """MongoDB configuration class"""
    
    def __init__(self):
        # Get MongoDB URL from environment or use default
        self.mongodb_url = os.getenv("CONNECTION_STRING", "mongodb+srv://thangnnd22414:S3HfhztmwyyYL2G3@cluster0.cnqmsmh.mongodb.net/Attacker_Database")
        self.database_name = os.getenv("DATABASE_NAME", "Attacker_Database")
        self.collection_name = "masconversations"
        
        # Initialize client
        self.client = AsyncIOMotorClient(self.mongodb_url)
        self.database = self.client[self.database_name]
        self.collection = self.database[self.collection_name]
    
    async def test_connection(self) -> bool:
        """Test MongoDB connection"""
        try:
            await self.client.admin.command('ping')
            return True
        except Exception as e:
            print(f"MongoDB connection failed: {e}")
            return False
    
    async def store_conversation(self, result: Dict[Any, Any], request_data: Dict[Any, Any]) -> Optional[str]:
        """
        Store MAS conversation result to MongoDB
        
        Args:
            result: The MAS workflow result
            request_data: The original request data
            
        Returns:
            str: The inserted document ID, or None if failed
        """
        try:
            # Prepare document
            document = {
                "loan_id": request_data.get("loan_contract_id", ""),
                "request_id": result.get("request_id", ""),
                "request_data": request_data,
                "result_stringify": json.dumps(result, ensure_ascii=False, indent=2),
                "decision": result.get("final_result", {}).get("decision", "unknown"),
                "processing_time": result.get("processing_time_seconds", 0),
                "timestamp": datetime.utcnow(),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Insert document
            insert_result = await self.collection.insert_one(document)
            
            print(f"✅ Stored conversation: {insert_result.inserted_id}")
            return str(insert_result.inserted_id)
            
        except Exception as e:
            print(f"❌ MongoDB storage error: {e}")
            return None
    
    async def get_conversations(self, limit: int = 10) -> list:
        """Get recent conversations"""
        try:
            conversations = []
            cursor = self.collection.find().sort("timestamp", -1).limit(limit)
            
            async for doc in cursor:
                doc["_id"] = str(doc["_id"])
                conversations.append(doc)
            
            return conversations
            
        except Exception as e:
            print(f"❌ Error retrieving conversations: {e}")
            return []
    
    async def get_conversation_by_id(self, request_id: str) -> Optional[Dict]:
        """Get conversation by request_id"""
        try:
            doc = await self.collection.find_one({"request_id": request_id})
            if doc:
                doc["_id"] = str(doc["_id"])
            return doc
        except Exception as e:
            print(f"❌ Error retrieving conversation {request_id}: {e}")
            return None
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get conversation statistics"""
        try:
            total_count = await self.collection.count_documents({})
            approved_count = await self.collection.count_documents({"decision": "approve"})
            rejected_count = await self.collection.count_documents({"decision": "reject"})
            
            # Get average processing time
            pipeline = [
                {"$group": {"_id": None, "avg_processing_time": {"$avg": "$processing_time"}}}
            ]
            avg_result = await self.collection.aggregate(pipeline).to_list(1)
            avg_processing_time = avg_result[0]["avg_processing_time"] if avg_result else 0
            
            return {
                "total_conversations": total_count,
                "approved": approved_count,
                "rejected": rejected_count,
                "approval_rate": round(approved_count / total_count * 100, 2) if total_count > 0 else 0,
                "avg_processing_time": round(avg_processing_time, 2)
            }
            
        except Exception as e:
            print(f"❌ Error getting statistics: {e}")
            return {}

# Global instance
mongodb_config = MongoDBConfig()
