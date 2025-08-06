"""
Test personalized greeting with user name retrieval
"""
import asyncio
from app.botagent.main_bot import get_rag_bot

async def test_personalized_greeting():
    """Test personalized greeting functionality"""
    
    # Test citizen ID
    test_citizen_id = "075204000105"
    
    try:
        # Get RAG bot instance
        bot = get_rag_bot()
        print("✅ RAG Bot loaded successfully")
        
        # Test greeting without citizen_id (should be direct answer)
        print(f"\n🔍 Testing greeting WITHOUT citizen_id...")
        response_no_id = await bot.chat("Xin chào", citizen_id=None)
        print(f"Response: {response_no_id['response']}")
        print(f"Source: {response_no_id['source']}")
        
        # Test greeting with citizen_id (should get user name from database)
        print(f"\n🔍 Testing greeting WITH citizen_id: {test_citizen_id}")
        response_with_id = await bot.chat("Xin chào", citizen_id=test_citizen_id)
        print(f"Response: {response_with_id['response']}")
        print(f"Source: {response_with_id['source']}")
        
        # Test different greetings
        greetings = ["Hello", "Chào bạn", "Hi", "Hey"]
        
        for greeting in greetings:
            print(f"\n🔍 Testing '{greeting}' with citizen_id...")
            response = await bot.chat(greeting, citizen_id=test_citizen_id)
            print(f"Response: {response['response']}")
            print(f"Source: {response['source']}")
        
        # Test non-greeting message with citizen_id (should still work for academic data)
        print(f"\n🔍 Testing academic question with citizen_id...")
        response_academic = await bot.chat("Điểm GPA của tôi là bao nhiều?", citizen_id=test_citizen_id)
        print(f"Response: {response_academic['response']}")
        print(f"Source: {response_academic['source']}")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🧪 Testing Personalized Greeting with User Name Retrieval...")
    print("=" * 70)
    
    asyncio.run(test_personalized_greeting())
    
    print("=" * 70)
    print("✅ Test completed!")
