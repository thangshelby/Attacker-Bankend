FROM python:3.12.11-alpine3.22
WORKDIR /app

COPY . .
RUN apk add --no-cache gcc g++ musl-dev
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENV PYTHONPATH=/app

CMD ["python", "main_grpc.py"]