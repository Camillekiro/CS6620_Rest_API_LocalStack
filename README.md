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

## Citations
https://docs.docker.com/compose/intro/compose-application-model/#key-commands
https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb/client/create_table.html
https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/create_bucket.html
https://discuss.localstack.cloud/t/set-up-s3-bucket-using-docker-compose/646.html
https://stackoverflow.com/questions/10450962/how-can-i-fetch-all-items-from-a-dynamodb-table-without-specifying-the-primary-k
https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb/client/scan.html
https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/list_objects_v2.html
https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb/client/get_item.html
https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/get_object.html
https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb/client/put_item.html
https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/put_object.html
https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/delete_object.html
https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb/client/delete_item.html
https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions
https://docs.github.com/en/actions/how-tos/writing-workflows/choosing-when-your-workflow-runs/triggering-a-workflow?versionId=free-pro-team%40latest&productId=actions
Shell scripts run-stack and run-tests were written with assistance from Claude A.I.
API versioning derived from the previous assignment and was developed with assistance from Claude A.I.
Read me example usage section was developed with assistance from Claude A.I.