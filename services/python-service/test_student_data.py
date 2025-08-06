"""
Test script for Student Data MCP Server
Tests academic, student profile, and user data retrieval
"""

import asyncio
from app.botagent.mcp_server import StudentDataMCPServer

async def test_student_mcp_server():
    """Test the Student MCP Server functionality"""
    
    # Create server instance
    server = StudentDataMCPServer()
    
    # Test citizen ID
    test_citizen_id = "075204000105"
    
    try:
        # Connect to database
        await server.connect_database()
        print("✅ Successfully connected to database")
        
        # Test academic data retrieval
        print(f"\n🔍 Testing academic data retrieval for citizen_id: {test_citizen_id}")
        academic_result = await server.get_academic_data(test_citizen_id)
        
        if "error" in academic_result:
            print(f"❌ Academic data error: {academic_result['error']}")
        else:
            print("✅ Academic data retrieved successfully:")
            print(f"   Student ID: {academic_result.get('student_id', 'N/A')}")
            print(f"   GPA: {academic_result.get('academic_performance', {}).get('gpa', 'N/A')}")
            print(f"   Current GPA: {academic_result.get('academic_performance', {}).get('current_gpa', 'N/A')}")
            print(f"   Verification Status: {academic_result.get('current_status', {}).get('verified', 'N/A')}")
        
        # Test student profile data retrieval
        print(f"\n🔍 Testing student profile data retrieval for citizen_id: {test_citizen_id}")
        student_result = await server.get_student_data(test_citizen_id)
        
        if "error" in student_result:
            print(f"❌ Student data error: {student_result['error']}")
        else:
            print("✅ Student data retrieved successfully:")
            print(f"   Student ID: {student_result.get('student_id', 'N/A')}")
            print(f"   University: {student_result.get('university_info', {}).get('university', 'N/A')}")
            print(f"   Major: {student_result.get('university_info', {}).get('major_name', 'N/A')}")
            print(f"   Faculty: {student_result.get('university_info', {}).get('faculty_name', 'N/A')}")
            print(f"   Year of Study: {student_result.get('academic_status', {}).get('year_of_study', 'N/A')}")
            print(f"   Class ID: {student_result.get('university_info', {}).get('class_id', 'N/A')}")
            print(f"   Verification Status: {student_result.get('academic_status', {}).get('verified', 'N/A')}")
        
        # Test user data retrieval
        print(f"\n🔍 Testing user data retrieval for citizen_id: {test_citizen_id}")
        user_result = await server.get_user_data(test_citizen_id)
        
        if "error" in user_result:
            print(f"❌ User data error: {user_result['error']}")
        else:
            print("✅ User data retrieved successfully:")
            print(f"   Name: {user_result.get('name', 'N/A')}")
            print(f"   Email: {user_result.get('personal_info', {}).get('email', 'N/A')}")
            print(f"   Phone: {user_result.get('personal_info', {}).get('phone', 'N/A')}")
            print(f"   Role: {user_result.get('account_info', {}).get('role', 'N/A')}")
            print(f"   Verification Status: {user_result.get('account_info', {}).get('verified', 'N/A')}")
    
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Close database connection
        if server.client:
            server.client.close()
            print("\n🔒 Database connection closed")

if __name__ == "__main__":
    print("🧪 Testing Student Data MCP Server (Academic, Student Profile, User Data)...")
    print("=" * 70)
    
    asyncio.run(test_student_mcp_server())
    
    print("=" * 70)
    print("✅ Test completed!")
