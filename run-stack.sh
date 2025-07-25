#!/bin/bash

echo "Starting Draft API Stack with Docker Compose"
echo "Press Ctrl + c to stop the app"

docker-compose -f docker-compose.yml up --build

echo "Draft API Stack Stopped."