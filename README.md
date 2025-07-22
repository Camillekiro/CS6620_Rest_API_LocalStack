# REST API For Sports Draft Data

## Description
A Flask REST API for managing draft records with Docker containerization and CI/CD pipeline.

## Prerequisites
    - Docker Desktop running
    - Python 3.11+

## Running the API

```bash
#make scripts executable
chmod +x run-api.sh run-tests.sh

#start API container
./run-api.sh
```
**The API runs at:** `http://localhost:5000`
Note: The CI/CD pipeline uses port 5001

## Running Tests

```bash
#run tests in Docker container
./run-tests.sh
```

## Stop API
```bash
docker stop flask-api-container
```

## API Endpoints
**Base URL:** `http://localhost:5000/api/v1`

| Method | Endpoint | Description|
|--------|----------|------------|
| GET | `/drafts` | Get all drafts |
| GET | `/drafts/{id}` | Get a single draft record |
| POST | `/drafts` | Create new draft record |
| PUT | `/drafts/{id}` | Update draft record |
| DELETE | `/drafts/{id}` | Delete draft record |

## Example Usage
```bash
#create a draft
curl -X POST http://localhost:5000/api/v1/drafts \
  -H "Content-Type: application/json" \
  -d '{"pick_number": "(1)", "pro_team": "Team A", "player_name": "John Doe", "amateur_team": "Northeastern University"}'
#get all drafts (add an id to get a specific record, example ...drafts/1)
curl http://localhost:5000/api/v1/drafts
#update a draft (replace ID 1 with the actual draft ID)
curl -X PUT http://localhost:5000/api/v1/drafts/1 \
  -H "Content-Type: application/json" \
  -d '{"pick_number": "(1)", "pro_team": "Updated Team", "player_name": "John Doe", "amateur_team": "Updated College"}'
#delete a draft record (replace ID 1 with the actual draft ID)
curl -X DELETE http://localhost:5000/api/v1/drafts/1
```

## CI/CD Pipeline

The Github Actions workflow automatically:
    - Runs pn push to the main branch
    - Runs on pull requests
    - Can be triggered manually from Actions tab
    - Builds Docker containers
    - Runs tests with proper exit codes
    - Deploys on successfull tests

## Manual Trigger
    1. Go to the Actions tab in Github
    2. Select the "Run workflow" drop down
    3. Select the green "Run workflow" button

## Testing
# Local Testing
```bash
#test with Python directly
python -m pytest tests/ -v

#test with Docker
./run-tests.sh
```

## Docker Commands 
# API Container
```bash
#build and run API
docker build -f Dockerfile.api -t flask-api .
docker run -d --name flask-api-container -p 5000:5000 flask-api

#stop API
docker stop flask-api-container
```
# Test Container
```bash
#build and run tests
docker build -f Dockerfile.tests -t flask-tests .
docker run --rm flask-tests
```