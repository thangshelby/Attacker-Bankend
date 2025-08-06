import grpc
from app.grpc.generated import chatbot_pb2_grpc
from app.grpc.generated import chatbot_pb2
from app.botagent.main_bot import get_rag_bot
import asyncio
import time

class ChatbotServiceServicer(chatbot_pb2_grpc.ChatbotServiceServicer):
    """Implementation of ChatbotService"""
    
    def __init__(self):
        self.bot = None
    
    def _get_bot(self):
        """Lazy initialization of bot"""
        if self.bot is None:
            self.bot = get_rag_bot()
        return self.bot
    
    def Chat(self, request, context):
        """Handle chat request"""
        start_time = time.time()
        
        try:
            # Get bot instance
            bot = self._get_bot()
            
            # Create async event loop for the bot chat method
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                # Call the async chat method
                result = loop.run_until_complete(
                    bot.chat(message=request.message)
                )
            finally:
                loop.close()
            
            processing_time = time.time() - start_time
            
            # Create successful response
            response = chatbot_pb2.ChatResponse()
            response.question = request.message
            response.answer = result.get("response", "Không có câu trả lời")
            response.sources = result.get("sources", [])
            response.processing_time = processing_time
            response.success = True
            response.error = ""
            
            print(f"✅ gRPC Chat successful: {request.message[:50]}... -> {response.answer[:50]}...")
            
            return response
            
        except Exception as e:
            processing_time = time.time() - start_time
            error_msg = f"Chat error: {str(e)}"
            
            print(f"❌ gRPC Chat error: {error_msg}")
            
            # Create error response
            response = chatbot_pb2.ChatResponse()
            response.question = request.message
            response.answer = f"Xin lỗi, tôi gặp lỗi: {str(e)}"
            response.sources = []
            response.processing_time = processing_time
            response.success = False
            response.error = error_msg
            
            return response