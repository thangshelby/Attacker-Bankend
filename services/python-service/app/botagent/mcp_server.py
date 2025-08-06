"""
MCP Server for Student Data Retrieval
Provides tools to fetch academic and student profile information from MongoDB database using citizen_id
"""

import asyncio
import logging
from typing import Any, Dict, List, Optional
import os
from motor.motor_asyncio import AsyncIOMotorClient
from mcp.server.models import InitializationOptions
import mcp.types as types
from mcp.server import NotificationOptions, Server
from pydantic import AnyUrl
import mcp.server.stdio
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
env_path = Path(__file__).parent.parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("student-data-mcp-server")

# MongoDB Configuration
CONNECTION_STRING = os.getenv("CONNECTION_STRING", "mongodb+srv://thangnnd22414:S3HfhztmwyyYL2G3@cluster0.cnqmsmh.mongodb.net/Attacker_Database")
DATABASE_NAME = os.getenv("DATABASE_NAME", "Attacker_Database").strip()

class StudentDataMCPServer:
    def __init__(self):
        self.server = Server("student-data-server")
        self.client: Optional[AsyncIOMotorClient] = None
        self.db = None
        
    async def connect_database(self):
        """Connect to MongoDB database"""
        try:
            self.client = AsyncIOMotorClient(CONNECTION_STRING)
            self.db = self.client[DATABASE_NAME]
            # Test connection
            await self.client.admin.command('ping')
            logger.info(f"Successfully connected to MongoDB database: {DATABASE_NAME}")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    async def get_student_data(self, citizen_id: str) -> Dict[str, Any]:
        """
        Retrieve student data for a student by citizen_id
        
        Args:
            citizen_id: The citizen ID to search for
            
        Returns:
            Dictionary containing student information
        """
        try:
            # Query the students collection
            student_data = await self.db.students.find_one(
                {"citizen_id": citizen_id},
                {
                    "_id": 0,  # Exclude MongoDB _id
                    "citizen_id": 1,
                    "student_id": 1,
                    "university": 1,
                    "major_name": 1,
                    "year_of_study": 1,
                    "class_id": 1,
                    "faculty_name": 1,
                    "verified": 1,
                    "student_card_back": 1,
                    "student_card_front": 1,
                    "created_at": 1,
                    "updated_at": 1
                }
            )
            
            if student_data:
                # Process and enhance the data for better readability
                processed_data = {
                    "citizen_id": student_data.get("citizen_id", "N/A"),
                    "student_id": student_data.get("student_id", "N/A"),
                    "university_info": {
                        "university": student_data.get("university", "N/A"),
                        "faculty_name": student_data.get("faculty_name", "N/A"),
                        "major_name": student_data.get("major_name", "N/A"),
                        "class_id": student_data.get("class_id", "N/A")
                    },
                    "academic_status": {
                        "year_of_study": student_data.get("year_of_study", 1),
                        "verified": student_data.get("verified", False)
                    },
                    "documents": {
                        "student_card_front": student_data.get("student_card_front", "N/A"),
                        "student_card_back": student_data.get("student_card_back", "N/A")
                    },
                    "timestamps": {
                        "created_at": str(student_data.get("created_at", "N/A")),
                        "updated_at": str(student_data.get("updated_at", "N/A"))
                    }
                }
                
                logger.info(f"Successfully retrieved student data for citizen_id: {citizen_id}")
                return processed_data
            else:
                logger.warning(f"No student data found for citizen_id: {citizen_id}")
                return {"error": f"No student data found for citizen_id: {citizen_id}"}
                
        except Exception as e:
            logger.error(f"Error retrieving student data for {citizen_id}: {e}")
            return {"error": f"Database error: {str(e)}"}

    async def get_user_data(self, citizen_id: str) -> Dict[str, Any]:
        """
        Retrieve user data for a user by citizen_id
        
        Args:
            citizen_id: The citizen ID to search for
            
        Returns:
            Dictionary containing user information
        """
        try:
            # Query the users collection
            user_data = await self.db.users.find_one(
                {"citizen_id": citizen_id},
                {
                    "_id": 0,  # Exclude MongoDB _id
                    "citizen_id": 1,
                    "name": 1,
                    "email": 1,
                    "phone": 1,
                    "address": 1,
                    "date_of_birth": 1,
                    "created_at": 1,
                    "updated_at": 1,
                    "verified": 1,
                    "avatar": 1,
                    "role": 1
                }
            )
            
            if user_data:
                # Process and enhance the data for better readability
                processed_data = {
                    "citizen_id": user_data.get("citizen_id", "N/A"),
                    "name": user_data.get("name", "N/A"),
                    "personal_info": {
                        "email": user_data.get("email", "N/A"),
                        "phone": user_data.get("phone", "N/A"),
                        "address": user_data.get("address", "N/A"),
                        "date_of_birth": str(user_data.get("date_of_birth", "N/A"))
                    },
                    "account_info": {
                        "role": user_data.get("role", "user"),
                        "verified": user_data.get("verified", False),
                        "avatar": user_data.get("avatar", "N/A")
                    },
                    "timestamps": {
                        "created_at": str(user_data.get("created_at", "N/A")),
                        "updated_at": str(user_data.get("updated_at", "N/A"))
                    }
                }
                
                logger.info(f"Successfully retrieved user data for citizen_id: {citizen_id}")
                return processed_data
            else:
                logger.warning(f"No user data found for citizen_id: {citizen_id}")
                return {"error": f"No user data found for citizen_id: {citizen_id}"}
                
        except Exception as e:
            logger.error(f"Error retrieving user data for {citizen_id}: {e}")
            return {"error": f"Database error: {str(e)}"}

    async def get_academic_data(self, citizen_id: str) -> Dict[str, Any]:
        """
        Retrieve academic data for a student by citizen_id
        
        Args:
            citizen_id: The citizen ID to search for
            
        Returns:
            Dictionary containing academic information
        """
        try:
            # Query the academicmodels collection (based on test results)
            academic_data = await self.db.academics.find_one(
                {"citizen_id": citizen_id},
                {
                    "_id": 0,  # Exclude MongoDB _id
                    "student_id": 1,
                    "gpa": 1,
                    "current_gpa": 1,
                    "total_credits_earned": 1,
                    "failed_course_count": 1,
                    "achievement_award_count": 1,
                    "has_scholarship": 1,
                    "scholarship_count": 1,
                    "club": 1,
                    "extracurricular_activity_count": 1,
                    "has_leadership_role": 1,
                    "study_year": 1,
                    "term": 1,
                    "verified": 1,
                    "citizen_id": 1
                }
            )
            
            if academic_data:
                # Process and enhance the data for better readability
                processed_data = {
                    "citizen_id": academic_data.get("citizen_id", "N/A"),
                    "student_id": academic_data.get("student_id", "N/A"),
                    "academic_performance": {
                        "gpa": academic_data.get("gpa", 0.0),
                        "current_gpa": academic_data.get("current_gpa", 0.0),
                        "total_credits_earned": academic_data.get("total_credits_earned", 0),
                        "failed_course_count": academic_data.get("failed_course_count", 0)
                    },
                    "achievements": {
                        "achievement_award_count": academic_data.get("achievement_award_count", 0),
                        "has_scholarship": academic_data.get("has_scholarship", False),
                        "scholarship_count": academic_data.get("scholarship_count", 0)
                    },
                    "activities": {
                        "club": academic_data.get("club", "None"),
                        "extracurricular_activity_count": academic_data.get("extracurricular_activity_count", 0),
                        "has_leadership_role": academic_data.get("has_leadership_role", False)
                    },
                    "current_status": {
                        "study_year": academic_data.get("study_year", 1),
                        "term": academic_data.get("term", 1),
                        "verified": academic_data.get("verified", False)
                    }
                }
                
                logger.info(f"Successfully retrieved academic data for citizen_id: {citizen_id}")
                return processed_data
            else:
                logger.warning(f"No academic data found for citizen_id: {citizen_id}")
                return {"error": f"No academic data found for citizen_id: {citizen_id}"}
                
        except Exception as e:
            logger.error(f"Error retrieving academic data for {citizen_id}: {e}")
            return {"error": f"Database error: {str(e)}"}

    def setup_handlers(self):
        """Setup MCP server handlers"""
        
        @self.server.list_tools()
        async def handle_list_tools() -> list[types.Tool]:
            """List available tools"""
            return [
                types.Tool(
                    name="get_academic_data",
                    description="Retrieve academic information for a student by citizen ID",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "citizen_id": {
                                "type": "string",
                                "description": "The citizen ID of the student to look up academic data for"
                            }
                        },
                        "required": ["citizen_id"]
                    }
                ),
                types.Tool(
                    name="get_student_data",
                    description="Retrieve student profile information by citizen ID",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "citizen_id": {
                                "type": "string",
                                "description": "The citizen ID of the student to look up profile data for"
                            }
                        },
                        "required": ["citizen_id"]
                    }
                ),
                types.Tool(
                    name="get_user_data",
                    description="Retrieve user personal information by citizen ID",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "citizen_id": {
                                "type": "string",
                                "description": "The citizen ID of the user to look up personal data for"
                            }
                        },
                        "required": ["citizen_id"]
                    }
                )
            ]

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent]:
            """Handle tool calls"""
            if name == "get_academic_data":
                citizen_id = arguments.get("citizen_id")
                if not citizen_id:
                    return [types.TextContent(
                        type="text",
                        text="Error: citizen_id is required"
                    )]
                
                # Get academic data
                academic_data = await self.get_academic_data(citizen_id)
                
                if "error" in academic_data:
                    return [types.TextContent(
                        type="text",
                        text=f"Error: {academic_data['error']}"
                    )]
                
                # Format the response for better readability
                formatted_response = f"""
Academic Information for Student ID: {academic_data['student_id']} (Citizen ID: {academic_data['citizen_id']})

📊 Academic Performance:
• GPA: {academic_data['academic_performance']['gpa']}/4.0
• Current GPA: {academic_data['academic_performance']['current_gpa']}/4.0
• Total Credits Earned: {academic_data['academic_performance']['total_credits_earned']}
• Failed Courses: {academic_data['academic_performance']['failed_course_count']}

🏆 Achievements & Scholarships:
• Awards/Achievements: {academic_data['achievements']['achievement_award_count']}
• Has Scholarship: {'Yes' if academic_data['achievements']['has_scholarship'] else 'No'}
• Number of Scholarships: {academic_data['achievements']['scholarship_count']}

🎯 Activities & Leadership:
• Club Membership: {academic_data['activities']['club']}
• Extracurricular Activities: {academic_data['activities']['extracurricular_activity_count']}
• Leadership Role: {'Yes' if academic_data['activities']['has_leadership_role'] else 'No'}

📚 Current Status:
• Study Year: {academic_data['current_status']['study_year']}
• Current Term: {academic_data['current_status']['term']}
• Verification Status: {'Verified' if academic_data['current_status']['verified'] else 'Not Verified'}
                """.strip()
                
                return [types.TextContent(
                    type="text",
                    text=formatted_response
                )]
            
            elif name == "get_student_data":
                citizen_id = arguments.get("citizen_id")
                if not citizen_id:
                    return [types.TextContent(
                        type="text",
                        text="Error: citizen_id is required"
                    )]
                
                # Get student data
                student_data = await self.get_student_data(citizen_id)
                
                if "error" in student_data:
                    return [types.TextContent(
                        type="text",
                        text=f"Error: {student_data['error']}"
                    )]
                
                # Format the response for better readability
                formatted_response = f"""
Student Profile for Citizen ID: {student_data['citizen_id']}

👤 Basic Information:
• Student ID: {student_data['student_id']}
• Citizen ID: {student_data['citizen_id']}

🏫 University Information:
• University: {student_data['university_info']['university'].upper()}
• Faculty: {student_data['university_info']['faculty_name']}
• Major: {student_data['university_info']['major_name']}
• Class ID: {student_data['university_info']['class_id']}

📚 Academic Status:
• Year of Study: {student_data['academic_status']['year_of_study']}
• Verification Status: {'Verified' if student_data['academic_status']['verified'] else 'Not Verified'}

📄 Documents:
• Student Card Front: {student_data['documents']['student_card_front'][:80] + '...' if len(student_data['documents']['student_card_front']) > 80 else student_data['documents']['student_card_front']}
• Student Card Back: {student_data['documents']['student_card_back'][:80] + '...' if len(student_data['documents']['student_card_back']) > 80 else student_data['documents']['student_card_back']}

📅 Timestamps:
• Created: {student_data['timestamps']['created_at']}
• Last Updated: {student_data['timestamps']['updated_at']}
                """.strip()
                
                return [types.TextContent(
                    type="text",
                    text=formatted_response
                )]
            
            elif name == "get_user_data":
                citizen_id = arguments.get("citizen_id")
                if not citizen_id:
                    return [types.TextContent(
                        type="text",
                        text="Error: citizen_id is required"
                    )]
                
                # Get user data
                user_data = await self.get_user_data(citizen_id)
                
                if "error" in user_data:
                    return [types.TextContent(
                        type="text",
                        text=f"Error: {user_data['error']}"
                    )]
                
                # Format the response for better readability
                formatted_response = f"""
User Profile for Citizen ID: {user_data['citizen_id']}

👤 Personal Information:
• Full Name: {user_data['name']}
• Citizen ID: {user_data['citizen_id']}

📧 Contact Information:
• Email: {user_data['personal_info']['email']}
• Phone: {user_data['personal_info']['phone']}
• Address: {user_data['personal_info']['address']}
• Date of Birth: {user_data['personal_info']['date_of_birth']}

🔐 Account Information:
• Role: {user_data['account_info']['role'].title()}
• Verification Status: {'Verified' if user_data['account_info']['verified'] else 'Not Verified'}
• Avatar: {user_data['account_info']['avatar'][:50] + '...' if len(str(user_data['account_info']['avatar'])) > 50 else user_data['account_info']['avatar']}

📅 Account History:
• Account Created: {user_data['timestamps']['created_at']}
• Last Updated: {user_data['timestamps']['updated_at']}
                """.strip()
                
                return [types.TextContent(
                    type="text",
                    text=formatted_response
                )]
            
            else:
                return [types.TextContent(
                    type="text",
                    text=f"Unknown tool: {name}"
                )]

    async def run(self):
        """Run the MCP server"""
        try:
            # Connect to database
            await self.connect_database()
            
            # Setup handlers
            self.setup_handlers()
            
            # Run server
            async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
                logger.info("Student Data MCP Server started successfully")
                await self.server.run(
                    read_stream,
                    write_stream,
                    InitializationOptions(
                        server_name="student-data-server",
                        server_version="1.0.0",
                        capabilities=self.server.get_capabilities(
                            notification_options=NotificationOptions(),
                            experimental_capabilities={},
                        )
                    )
                )
        except Exception as e:
            logger.error(f"Error running MCP server: {e}")
            raise
        finally:
            if self.client:
                self.client.close()
                logger.info("MongoDB connection closed")

def main():
    """Main entry point"""
    server = StudentDataMCPServer()
    asyncio.run(server.run())

if __name__ == "__main__":
    main()
