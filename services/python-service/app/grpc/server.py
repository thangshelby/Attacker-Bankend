import grpc
from concurrent import futures

from app.core.service import say_hello
from app.grpc.generated import base_pb2, base_pb2_grpc

class BaseService(base_pb2_grpc.BaseServiceServicer):
    def SayHello (self,request,context):
        name = request.name
        response= f"Good Bye {name}"
        return base_pb2.HelloReply(message=f"Hello {name}") 
    def SayGoodBye(self,request,context):
        name = request.name
        response= f"Good Bye {name}"

        return base_pb2.ByeReply(message=f"Good Bye {name}")  

def serve():

    print("Python is running on port 50051")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    base_pb2_grpc.add_BaseServiceServicer_to_server(BaseService(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    server.wait_for_termination()
