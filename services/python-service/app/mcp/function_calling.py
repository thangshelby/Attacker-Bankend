"""
MCP Server for RAG Bot - Function Calling with MongoDB Data
Lấy dữ liệu từ MongoDB để bồi context cho chatbot
"""

import asyncio
import json
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from dataclasses import dataclass
import motor.motor_asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class UserContext:
    """User context data structure"""
    user_info: Dict[str, Any]
    student_info: Optional[Dict[str, Any]] = None
    loan_profiles: List[Dict[str, Any]] = None
    academic_info: Optional[Dict[str, Any]] = None
    mas_conversations: List[Dict[str, Any]] = None

class MCPDatabaseConnector:
    """MongoDB connector for MCP server"""
    
    def __init__(self):
        self.connection_string = os.getenv("CONNECTION_STRING")
        self.database_name = os.getenv("DATABASE_NAME", "Attacker_Database")
        self.client = None
        self.db = None
        
    async def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = motor.motor_asyncio.AsyncIOMotorClient(self.connection_string)
            self.db = self.client[self.database_name]
            logger.info("Connected to MongoDB successfully")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    async def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()

class MCPFunctionCalling:
    """MCP Function Calling implementation for RAG Bot"""
    
    def __init__(self):
        self.db_connector = MCPDatabaseConnector()
        self.available_functions = {
            "get_user_profile": self.get_user_profile,
            "get_student_info": self.get_student_info,
            "get_user_loans": self.get_user_loans,
            "get_academic_info": self.get_academic_info,
            "get_mas_conversations": self.get_mas_conversations,
            "get_comprehensive_user_context": self.get_comprehensive_user_context,
            "search_students_by_university": self.search_students_by_university,
            "get_loan_statistics": self.get_loan_statistics
        }
    
    async def initialize(self):
        """Initialize MCP server"""
        await self.db_connector.connect()
        logger.info("MCP Function Calling initialized")
    
    async def get_user_profile(self, citizen_id: str = None, email: str = None) -> Dict[str, Any]:
        """
        Lấy thông tin profile người dùng từ collection users
        
        Args:
            citizen_id: CMND/CCCD của người dùng
            email: Email của người dùng
            
        Returns:
            Thông tin chi tiết người dùng
        """
        try:
            query = {}
            if citizen_id:
                query["citizen_id"] = citizen_id
            elif email:
                query["email"] = email
            else:
                return {"error": "Cần cung cấp citizen_id hoặc email"}
            
            user = await self.db_connector.db.users.find_one(query)
            
            if user:
                # Convert ObjectId to string
                user["_id"] = str(user["_id"])
                
                return {
                    "success": True,
                    "data": {
                        "name": user.get("name", "N/A"),
                        "citizen_id": user.get("citizen_id", "N/A"),
                        "email": user.get("email", "N/A"),
                        "phone": user.get("phone", "N/A"),
                        "address": user.get("address", "N/A"),
                        "kyc_status": user.get("kyc_status", "Pending"),
                        "role": user.get("role", "User"),
                        "gender": user.get("gender", "N/A"),
                        "birth": str(user.get("birth", "N/A")),
                        "created_at": str(user.get("created_at", "N/A"))
                    }
                }
            else:
                return {"error": "Không tìm thấy người dùng"}
                
        except Exception as e:
            logger.error(f"Error getting user profile: {e}")
            return {"error": f"Lỗi khi lấy thông tin người dùng: {str(e)}"}
    
    async def get_student_info(self, citizen_id: str) -> Dict[str, Any]:
        """
        Lấy thông tin sinh viên từ collection students
        
        Args:
            citizen_id: CMND/CCCD của sinh viên
            
        Returns:
            Thông tin sinh viên
        """
        try:
            student = await self.db_connector.db.students.find_one({"citizen_id": citizen_id})
            
            if student:
                student["_id"] = str(student["_id"])
                return {
                    "success": True,
                    "data": {
                        "student_id": student.get("student_id", "N/A"),
                        "citizen_id": student.get("citizen_id", "N/A"),
                        "university": student.get("university", "N/A"),
                        "major": student.get("major", "N/A"),
                        "year": student.get("year", "N/A"),
                        "gpa": student.get("gpa", "N/A"),
                        "status": student.get("status", "N/A"),
                        "graduation_date": str(student.get("graduation_date", "N/A"))
                    }
                }
            else:
                return {"error": "Không tìm thấy thông tin sinh viên"}
                
        except Exception as e:
            logger.error(f"Error getting student info: {e}")
            return {"error": f"Lỗi khi lấy thông tin sinh viên: {str(e)}"}
    
    async def get_user_loans(self, citizen_id: str) -> Dict[str, Any]:
        """
        Lấy danh sách khoản vay từ collection loanprofiles
        
        Args:
            citizen_id: CMND/CCCD của người dùng
            
        Returns:
            Danh sách khoản vay
        """
        try:
            loans = await self.db_connector.db.loanprofiles.find(
                {"citizen_id": citizen_id}
            ).sort("created_at", -1).to_list(length=None)
            
            loan_data = []
            for loan in loans:
                loan["_id"] = str(loan["_id"])
                loan_data.append({
                    "loan_id": str(loan.get("_id")),
                    "amount": loan.get("amount", 0),
                    "purpose": loan.get("purpose", "N/A"),
                    "status": loan.get("status", "N/A"),
                    "interest_rate": loan.get("interest_rate", 0),
                    "term_months": loan.get("term_months", 0),
                    "created_at": str(loan.get("created_at", "N/A")),
                    "approval_status": loan.get("approval_status", "Pending")
                })
            
            return {
                "success": True,
                "data": {
                    "total_loans": len(loan_data),
                    "loans": loan_data
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting user loans: {e}")
            return {"error": f"Lỗi khi lấy thông tin khoản vay: {str(e)}"}
    
    async def get_academic_info(self, citizen_id: str) -> Dict[str, Any]:
        """
        Lấy thông tin học tập từ collection academics
        
        Args:
            citizen_id: CMND/CCCD của sinh viên
            
        Returns:
            Thông tin học tập
        """
        try:
            academics = await self.db_connector.db.academics.find(
                {"citizen_id": citizen_id}
            ).to_list(length=None)
            
            academic_data = []
            for academic in academics:
                academic["_id"] = str(academic["_id"])
                academic_data.append({
                    "semester": academic.get("semester", "N/A"),
                    "year": academic.get("year", "N/A"),
                    "gpa": academic.get("gpa", 0),
                    "credits": academic.get("credits", 0),
                    "subjects": academic.get("subjects", []),
                    "achievements": academic.get("achievements", [])
                })
            
            return {
                "success": True,
                "data": {
                    "total_records": len(academic_data),
                    "academics": academic_data
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting academic info: {e}")
            return {"error": f"Lỗi khi lấy thông tin học tập: {str(e)}"}
    
    async def get_mas_conversations(self, citizen_id: str = None, loan_id: str = None) -> Dict[str, Any]:
        """
        Lấy các cuộc trò chuyện MAS từ collection masconversations
        
        Args:
            citizen_id: CMND/CCCD của người dùng
            loan_id: ID của khoản vay
            
        Returns:
            Danh sách cuộc trò chuyện MAS
        """
        try:
            query = {}
            if citizen_id:
                query["citizen_id"] = citizen_id
            if loan_id:
                query["loan_id"] = loan_id
            
            conversations = await self.db_connector.db.masconversations.find(query).to_list(length=None)
            
            conversation_data = []
            for conv in conversations:
                conv["_id"] = str(conv["_id"])
                conversation_data.append({
                    "conversation_id": str(conv.get("_id")),
                    "loan_id": conv.get("loan_id", "N/A"),
                    "citizen_id": conv.get("citizen_id", "N/A"),
                    "final_decision": conv.get("final_decision", "N/A"),
                    "decision_reason": conv.get("decision_reason", "N/A"),
                    "agents_involved": conv.get("agents_involved", []),
                    "conversation_summary": conv.get("conversation_summary", "N/A"),
                    "created_at": str(conv.get("created_at", "N/A"))
                })
            
            return {
                "success": True,
                "data": {
                    "total_conversations": len(conversation_data),
                    "conversations": conversation_data
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting MAS conversations: {e}")
            return {"error": f"Lỗi khi lấy cuộc trò chuyện MAS: {str(e)}"}
    
    async def search_students_by_university(self, university: str = "UEL") -> Dict[str, Any]:
        """
        Tìm kiếm sinh viên theo trường đại học
        
        Args:
            university: Tên trường đại học
            
        Returns:
            Danh sách sinh viên
        """
        try:
            students = await self.db_connector.db.students.find(
                {"university": university}
            ).limit(50).to_list(length=None)
            
            student_data = []
            for student in students:
                student["_id"] = str(student["_id"])
                student_data.append({
                    "student_id": student.get("student_id", "N/A"),
                    "citizen_id": student.get("citizen_id", "N/A"),
                    "university": student.get("university", "N/A"),
                    "major": student.get("major", "N/A"),
                    "year": student.get("year", "N/A"),
                    "gpa": student.get("gpa", "N/A")
                })
            
            return {
                "success": True,
                "data": {
                    "university": university,
                    "total_students": len(student_data),
                    "students": student_data
                }
            }
            
        except Exception as e:
            logger.error(f"Error searching students: {e}")
            return {"error": f"Lỗi khi tìm kiếm sinh viên: {str(e)}"}
    
    async def get_loan_statistics(self, university: str = None) -> Dict[str, Any]:
        """
        Lấy thống kê khoản vay
        
        Args:
            university: Tên trường đại học (tùy chọn)
            
        Returns:
            Thống kê khoản vay
        """
        try:
            # Aggregate loan statistics
            pipeline = []
            
            if university:
                # Join with students collection if university filter needed
                pipeline.extend([
                    {
                        "$lookup": {
                            "from": "students",
                            "localField": "citizen_id", 
                            "foreignField": "citizen_id",
                            "as": "student_info"
                        }
                    },
                    {"$unwind": "$student_info"},
                    {"$match": {"student_info.university": university}}
                ])
            
            pipeline.extend([
                {
                    "$group": {
                        "_id": "$status",
                        "count": {"$sum": 1},
                        "total_amount": {"$sum": "$amount"},
                        "avg_amount": {"$avg": "$amount"}
                    }
                }
            ])
            
            stats = await self.db_connector.db.loanprofiles.aggregate(pipeline).to_list(length=None)
            
            return {
                "success": True,
                "data": {
                    "university": university if university else "All",
                    "statistics": stats
                }
            }
            
        except Exception as e:
            logger.error(f"Error getting loan statistics: {e}")
            return {"error": f"Lỗi khi lấy thống kê khoản vay: {str(e)}"}
    
    async def get_comprehensive_user_context(self, citizen_id: str) -> Dict[str, Any]:
        """
        Lấy toàn bộ context của người dùng cho chatbot
        
        Args:
            citizen_id: CMND/CCCD của người dùng
            
        Returns:
            Context đầy đủ của người dùng
        """
        try:
            # Get all user data in parallel
            user_profile_task = self.get_user_profile(citizen_id=citizen_id)
            student_info_task = self.get_student_info(citizen_id)
            user_loans_task = self.get_user_loans(citizen_id)
            academic_info_task = self.get_academic_info(citizen_id)
            mas_conversations_task = self.get_mas_conversations(citizen_id=citizen_id)
            
            user_profile, student_info, user_loans, academic_info, mas_conversations = await asyncio.gather(
                user_profile_task, 
                student_info_task,
                user_loans_task, 
                academic_info_task,
                mas_conversations_task,
                return_exceptions=True
            )
            
            # Create comprehensive context
            context = {
                "citizen_id": citizen_id,
                "user_profile": user_profile if not isinstance(user_profile, Exception) else None,
                "student_info": student_info if not isinstance(student_info, Exception) else None,
                "loans": user_loans if not isinstance(user_loans, Exception) else None,
                "academics": academic_info if not isinstance(academic_info, Exception) else None,
                "mas_conversations": mas_conversations if not isinstance(mas_conversations, Exception) else None,
                "generated_at": datetime.now().isoformat()
            }
            
            return {
                "success": True,
                "data": context
            }
            
        except Exception as e:
            logger.error(f"Error getting comprehensive context: {e}")
            return {"error": f"Lỗi khi lấy context người dùng: {str(e)}"}
    
    async def call_function(self, function_name: str, **kwargs) -> Dict[str, Any]:
        """
        Execute MCP function call
        
        Args:
            function_name: Tên function cần gọi
            **kwargs: Tham số function
            
        Returns:
            Kết quả thực thi function
        """
        if function_name not in self.available_functions:
            return {
                "error": f"Function '{function_name}' not available. Available functions: {list(self.available_functions.keys())}"
            }
        
        try:
            function = self.available_functions[function_name]
            result = await function(**kwargs)
            return result
        except Exception as e:
            logger.error(f"Error calling function {function_name}: {e}")
            return {"error": f"Lỗi khi thực thi function {function_name}: {str(e)}"}
    
    def get_function_schemas(self) -> Dict[str, Dict]:
        """
        Lấy schema của các functions để LLM hiểu cách sử dụng
        
        Returns:
            Dictionary chứa schema của tất cả functions
        """
        return {
            "get_user_profile": {
                "description": "Lấy thông tin profile người dùng từ database",
                "parameters": {
                    "citizen_id": {"type": "string", "description": "CMND/CCCD của người dùng"},
                    "email": {"type": "string", "description": "Email của người dùng"}
                },
                "required": []
            },
            "get_student_info": {
                "description": "Lấy thông tin sinh viên từ database", 
                "parameters": {
                    "citizen_id": {"type": "string", "description": "CMND/CCCD của sinh viên"}
                },
                "required": ["citizen_id"]
            },
            "get_user_loans": {
                "description": "Lấy danh sách khoản vay của người dùng",
                "parameters": {
                    "citizen_id": {"type": "string", "description": "CMND/CCCD của người dùng"}
                },
                "required": ["citizen_id"]
            },
            "get_academic_info": {
                "description": "Lấy thông tin học tập của sinh viên",
                "parameters": {
                    "citizen_id": {"type": "string", "description": "CMND/CCCD của sinh viên"}
                },
                "required": ["citizen_id"]
            },
            "get_mas_conversations": {
                "description": "Lấy các cuộc trò chuyện MAS analysis",
                "parameters": {
                    "citizen_id": {"type": "string", "description": "CMND/CCCD của người dùng"},
                    "loan_id": {"type": "string", "description": "ID của khoản vay"}
                },
                "required": []
            },
            "search_students_by_university": {
                "description": "Tìm kiếm sinh viên theo trường đại học",
                "parameters": {
                    "university": {"type": "string", "description": "Tên trường đại học", "default": "UEL"}
                },
                "required": []
            },
            "get_loan_statistics": {
                "description": "Lấy thống kê khoản vay",
                "parameters": {
                    "university": {"type": "string", "description": "Tên trường đại học (tùy chọn)"}
                },
                "required": []
            },
            "get_comprehensive_user_context": {
                "description": "Lấy toàn bộ context của người dùng cho chatbot",
                "parameters": {
                    "citizen_id": {"type": "string", "description": "CMND/CCCD của người dùng"}
                },
                "required": ["citizen_id"]
            }
        }

# Global MCP instance
mcp_server = None

async def get_mcp_server():
    """Get or create MCP server instance"""
    global mcp_server
    if mcp_server is None:
        mcp_server = MCPFunctionCalling()
        await mcp_server.initialize()
    return mcp_server

# Export for use in other modules
__all__ = ['MCPFunctionCalling', 'get_mcp_server', 'UserContext']
