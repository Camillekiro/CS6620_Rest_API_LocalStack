# REST API For Sports Draft Data

## Description
A Flask REST API with GET, POST, PUT, DELETE endpoints. Stores data in SQLite, DynamoDB, and S3. Uses LocalStack for AWS mock and Docker Compose for orchestration.

## Prerequisites
    - Docker Desktop running
    - Docker Compose

## Running the API

```bash
# make scripts executable
chmod +x run-stack.sh run-tests.sh

# start the application
./run-stack.sh
```
**The API runs on:** `http://127.0.0.1:5000`

## Running Tests

```bash
# run all tests
./run-tests.sh
```

## API Endpoints
**Base URL:** `http://127.0.0.1:5000/api/v1`

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
curl -X POST http://127.0.0.1:5000/api/v1/drafts \
  -H "Content-Type: application/json" \
  -d '{"pick_number": "(1)", "pro_team": "Team A", "player_name": "John Doe", "amateur_team": "Northeastern University"}'
#get all drafts (add an id to get a specific record, example ...drafts/1)
curl http://127.0.0.1:5000/api/v1/drafts
#update a draft (replace ID 1 with the actual draft ID)
curl -X PUT http://127.0.0.1:5000/api/v1/drafts/1 \
  -H "Content-Type: application/json" \
  -d '{"pick_number": "(1)", "pro_team": "Updated Team", "player_name": "John Doe", "amateur_team": "Updated College"}'
#delete a draft record (replace ID 1 with the actual draft ID)
curl -X DELETE http://127.0.0.1:5000/api/v1/drafts/1
```