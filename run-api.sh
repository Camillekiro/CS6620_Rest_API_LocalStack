#!/bin/bash

echo "Building API Docker image"
docker build -f Dockerfile.api -t flask-api:latest .

echo "Stopping existing API container..."
docker stop flask-api-container 2>/dev/null || true
docker rm flask-api-container 2>/dev/null || true

echo "Starting API container"
docker run -d \
    --name flask-api-container \
    -p 5001:5000 \
    flask-api:latest

echo "API is running at http://localhost:5001"
echo "To stop API, run: docker stop flask-api-container"
