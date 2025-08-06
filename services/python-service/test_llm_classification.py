"""
Test LLM-based classification logic
"""
import asyncio
from app.botagent.main_bot import get_rag_bot

async def test_llm_classification():
    """Test LLM-based classification vs rule-based"""
    
    # Test citizen ID
    test_citizen_id = "075204000105"
    
    try:
        # Get RAG bot instance
        bot = get_rag_bot()
        print("✅ RAG Bot loaded successfully")
        
        test_cases = [
            # Greeting tests
            {"message": "Xin chào", "citizen_id": None, "expected": "direct_answer"},
            {"message": "Xin chào", "citizen_id": test_citizen_id, "expected": "call_data_db"},
            {"message": "Hello", "citizen_id": test_citizen_id, "expected": "call_data_db"},
            
            # Academic questions
            {"message": "GPA của tôi là bao nhiều", "citizen_id": test_citizen_id, "expected": "call_data_db"},
            {"message": "điểm số của tôi như thế nào", "citizen_id": test_citizen_id, "expected": "call_data_db"},
            {"message": "tôi có học bổng không", "citizen_id": test_citizen_id, "expected": "call_data_db"},
            
            # General questions
            {"message": "Vay vốn sinh viên là gì", "citizen_id": None, "expected": "direct_answer"},
            {"message": "Quy trình vay vốn như thế nào", "citizen_id": None, "expected": "rag_search"},
            {"message": "Lãi suất vay sinh viên", "citizen_id": None, "expected": "rag_search"},
            
            # Personal questions
            {"message": "Tôi có thể vay bao nhiều tiền", "citizen_id": test_citizen_id, "expected": "personal"},
        ]
        
        print(f"\n🧪 Testing LLM-based classification...")
        print("=" * 70)
        
        for i, test_case in enumerate(test_cases):
            message = test_case["message"]
            citizen_id = test_case["citizen_id"]
            expected = test_case["expected"]
            
            print(f"\n{i+1}. Message: \"{message}\"")
            print(f"   Citizen ID: {citizen_id if citizen_id else 'None'}")
            print(f"   Expected: {expected}")
            
            # Test classification
            classification = await bot._classify_question(message, citizen_id)
            print(f"   LLM Result: {classification}")
            
            # Test actual response
            response = await bot.chat(message, citizen_id)
            print(f"   Response Source: {response['source']}")
            print(f"   Response: {response['response'][:80]}...")
            
            # Check if correct
            is_correct = classification == expected
            print(f"   ✅ CORRECT" if is_correct else f"   ❌ WRONG (expected {expected})")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🧪 Testing LLM-based Classification Logic...")
    print("=" * 70)
    
    asyncio.run(test_llm_classification())
    
    print("=" * 70)
    print("✅ Test completed!")
