#!/bin/bash

echo "Starting LocalStack service"
docker-compose -f docker-compose.test.yml up -d

echo "Waiting for services to start up"
sleep 10

echo "Running tests"
python -m pytest tests/ -v
EXIT_CODE=$?

docker-compose -f docker-compose.test.yml down

if [ $EXIT_CODE -eq 0 ]; then 
    echo "Tests passed!"
else
    echo "Tests failed!"
fi

exit $EXIT_CODE