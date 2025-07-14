container-up:
	docker compose up -d
container-down:
	docker compose down
build:
	docker compose down
	docker compose up --build -d
	docker image prune -f 
logs:
	docker compose logs -f
gen-protobuf-python-service:
	. services/python-service/virtual_env/bin/activate && \
	python -m grpc_tools.protoc \
	-I=./protos \
	--python_out=./services/python-service/app/grpc/generated \
	--grpc_python_out=./services/python-service/app/grpc/generated \
	./protos/base.proto
