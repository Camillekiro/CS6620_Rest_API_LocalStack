#!/bin/bash

echo "Starting Draft API Stack with Docker Compose"
echo "Press Ctrl + c to stop the app"

docker-compose up -d

echo "Waiting for LocalStack services to start"
sleep 5

echo "Installing python dependencies"
pip install -r requirements.txt

echo "Starting Flask app"
echo "Visit http://localhost:5000 for API"
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python app/application.py

echo "Stopping LocalStack services"
docker-compose down

echo "Draft API Stack Stopped"