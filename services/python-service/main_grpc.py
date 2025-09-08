#!/usr/bin/env python3
import os
import sys
import time
generated = False

# Path to the .proto file in the sibling express-service
script_dir = os.path.dirname(os.path.abspath(__file__))
proto_path = os.path.abspath(os.path.join(script_dir, '..', 'express-service', 'base.proto'))

# Generate Python bindings from .proto if not already present
out_dir = script_dir
pb2_file = os.path.join(out_dir, 'base_pb2.py')
grpc_pb2_file = os.path.join(out_dir, 'base_pb2_grpc.py')

if not (os.path.exists(pb2_file) and os.path.exists(grpc_pb2_file)):
    print("🔧 Generating gRPC code from base.proto...")
    from grpc_tools import protoc
    protoc.main([
        '',
        f'-I{os.path.dirname(proto_path)}',
        f'--python_out={out_dir}',
        f'--grpc_python_out={out_dir}',
        proto_path,
    ])
    generated = True

import grpc
from concurrent import futures
import base_pb2
import base_pb2_grpc

# Implement the BaseService
class BaseServiceHandler(base_pb2_grpc.BaseServiceServicer):
    def SayHello(self, request, context):
        return base_pb2.HelloReply(message=f"Hello, {request.name}")

    def SayGoodBye(self, request, context):
        return base_pb2.ByeReply(message=f"Goodbye, {request.name}")

    def Predict(self, request, context):
        # Echo back the features as prediction
        return base_pb2.PredictRes(prediction=list(request.features))


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    base_pb2_grpc.add_BaseServiceServicer_to_server(BaseServiceHandler(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("📡 gRPC server started on port 50051...")
    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == '__main__':
    serve()
