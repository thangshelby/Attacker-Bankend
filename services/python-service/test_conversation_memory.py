"""
Test conversation memory and context awareness
"""
import asyncio
from app.botagent.main_bot import get_rag_bot

async def test_conversation_memory():
    """Test conversation memory functionality"""
    
    # Test citizen ID
    test_citizen_id = "075204000105"
    
    try:
        # Get RAG bot instance
        bot = get_rag_bot()
        print("✅ RAG Bot loaded successfully")
        
        # Clear previous memory
        bot.clear_memory()
        
        # Test conversation flow with memory
        conversation_flow = [
            {"message": "Xin chào", "citizen_id": test_citizen_id, "expected_context": "greeting"},
            {"message": "GPA của tôi là bao nhiều", "citizen_id": test_citizen_id, "expected_context": "academic_data"},
            {"message": "Còn điểm tín chỉ thì sao", "citizen_id": test_citizen_id, "expected_context": "follow_up"},
            {"message": "Tôi có thể vay bao nhiều", "citizen_id": test_citizen_id, "expected_context": "loan_inquiry"},
            {"message": "Quy trình như thế nào", "citizen_id": test_citizen_id, "expected_context": "process_follow_up"},
        ]
        
        print(f"\n🧪 Testing Conversation Memory & Context Awareness...")
        print("=" * 80)
        
        for i, step in enumerate(conversation_flow):
            message = step["message"]
            citizen_id = step["citizen_id"]
            expected_context = step["expected_context"]
            
            print(f"\n{i+1}. Message: \"{message}\"")
            print(f"   Expected Context: {expected_context}")
            
            # Get conversation summary before
            memory_before = bot.get_conversation_summary()
            print(f"   Memory Before: {memory_before['message_count']} messages")
            
            # Send message
            response = await bot.chat(message, citizen_id)
            
            # Get conversation summary after
            memory_after = bot.get_conversation_summary()
            print(f"   Memory After: {memory_after['message_count']} messages")
            print(f"   Response Source: {response['source']}")
            print(f"   Memory Tokens: {response.get('memory_tokens', 0)}")
            print(f"   Response: {response['response'][:100]}...")
            
            # Check if memory is growing
            if i > 0:
                is_memory_growing = memory_after['message_count'] > memory_before['message_count']
                print(f"   ✅ Memory Growing" if is_memory_growing else f"   ❌ Memory Not Growing")
        
        # Test memory summary
        print(f"\n📊 Final Memory Summary:")
        final_summary = bot.get_conversation_summary()
        print(f"   Total Messages: {final_summary['message_count']}")
        print(f"   User Messages: {final_summary['user_messages']}")
        print(f"   Assistant Messages: {final_summary['assistant_messages']}")
        print(f"   Recent Topics: {final_summary.get('recent_topics', [])}")
        
        # Test memory clear
        print(f"\n🧹 Testing Memory Clear...")
        bot.clear_memory()
        cleared_summary = bot.get_conversation_summary()
        print(f"   Messages After Clear: {cleared_summary['message_count']}")
        print(f"   ✅ Memory Cleared" if cleared_summary['message_count'] == 0 else f"   ❌ Memory Not Cleared")
        
        # Test enhanced stats
        print(f"\n📈 Enhanced Bot Statistics:")
        stats = bot.get_stats()
        print(f"   Memory System: {stats.get('memory_system', 'Unknown')}")
        print(f"   Personal Context: {stats['features']['personal_context']}")
        print(f"   Function Calling: {stats['features']['function_calling']}")
        print(f"   Conversation Memory: {stats['features']['conversation_memory']}")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🧪 Testing Conversation Memory & Context Awareness...")
    print("=" * 80)
    
    asyncio.run(test_conversation_memory())
    
    print("=" * 80)
    print("✅ Test completed!")
