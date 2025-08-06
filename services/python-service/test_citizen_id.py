"""
Quick test for citizen_id integration with chatbot
"""
import requests
import json

def test_chatbot_with_citizen_id():
    """Test chatbot with and without citizen_id"""
    
    base_url = "http://localhost:8000/api/v1/chat"
    
    test_cases = [
        {
            "name": "General question (no citizen_id)",
            "payload": {
                "message": "Xin chào!"
            }
        },
        {
            "name": "Database question (with citizen_id)",
            "payload": {
                "message": "Điểm GPA của tôi là bao nhiều?",
                "citizen_id": "075204000105"
            }
        },
        {
            "name": "Database question (no citizen_id - should require login)",
            "payload": {
                "message": "Tôi có học bổng không?"
            }
        },
        {
            "name": "RAG question (general info)",
            "payload": {
                "message": "Quy trình vay vốn như thế nào?"
            }
        }
    ]
    
    print("🤖 Testing Chatbot with citizen_id integration...")
    print("=" * 60)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test {i}: {test_case['name']}")
        print(f"💬 Message: {test_case['payload']['message']}")
        print(f"👤 Citizen ID: {test_case['payload'].get('citizen_id', 'None')}")
        
        try:
            response = requests.post(
                base_url,
                json=test_case['payload'],
                headers={"Content-Type": "application/json"},
                timeout=30
            )
            
            print(f"🔄 Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Response: {data.get('answer', 'No answer')[:100]}...")
                print(f"⏱️ Time: {data.get('processing_time', 'unknown')}s")
                print(f"📊 Source: {data.get('source', 'unknown')}")
                
                # Check for MCP data
                if 'data' in data:
                    print(f"🎓 Database Data: Retrieved")
                    
                # Check if database source
                if 'database' in data.get('source', ''):
                    print(f"💾 Source: Database query")
                elif 'login_required' in data.get('source', ''):
                    print(f"🔐 Requires: Login needed")
                
            else:
                print(f"❌ Error: {response.text}")
                
        except Exception as e:
            print(f"💥 Exception: {e}")
        
        print("-" * 40)
    
    print("\n✅ Test completed!")

if __name__ == "__main__":
    test_chatbot_with_citizen_id()
