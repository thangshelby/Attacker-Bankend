import grpc
from concurrent import futures

from app.grpc.generated import chatbot_pb2_grpc
from app.grpc.chatbot_service import ChatbotServiceServicer

def serve():
    print("🚀 Python gRPC Server starting on port 50051")
    print("📡 Services: ChatbotService")
    
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # Add chatbot service
    chatbot_pb2_grpc.add_ChatbotServiceServicer_to_server(ChatbotServiceServicer(), server)
    
    server.add_insecure_port("[::]:50051")
    server.start()
    
    print("✅ gRPC Chatbot Server is ready on port 50051!")
    print("🤖 Available service: ChatbotService.Chat")
    server.wait_for_termination()
