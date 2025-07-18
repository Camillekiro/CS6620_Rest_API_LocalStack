#!/bin/bash

echo "Building test Docker image"
docker build -f Dockerfile.tests -t flask-tests:latest .

echo "Running tests"
docker run --rm flask-tests:latest

#to capture exit code
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then 
    echo "All tests passed!"
else
    echo "Tests failed!"
fi

#exit with the same code as the tests
exit $EXIT_CODE