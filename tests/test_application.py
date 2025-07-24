import pytest
import json
import sys
import os

#add app dir to the python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from app.application import app, db, Draft, s3_client, ddb_client, S3_BUCKET_NAME, DDB_TABLE_NAME
from instance.aws_s3_setup import initialize_s3
from instance.aws_ddb_setup import initialize_dynamodb


@pytest.fixture
def client():
    """Create a test client and set up test db"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' #in memory db for tests
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            # initialize AWS resources
            initialize_s3(s3_client=s3_client, bucket_name=S3_BUCKET_NAME)
            initialize_dynamodb(dynamodb_client=ddb_client, table_name=DDB_TABLE_NAME)
            yield client
            db.drop_all()


@pytest.fixture
def sample_draft_data():
    return {
        "pick_number": "(77)",
        "pro_team": "Boston Celtics",
        "player_name": "John Doe",
        "amateur_team": "Duke"
    }


@pytest.fixture
def duplicate_draft_data():
    return {
        "pick_number": "(77)",
        "pro_team": "Boston Celtics",
        "player_name": "John Doe",
        "amateur_team": "Duke"
    }


def test_get_no_param(client):
    response = client.get(f'/api/v1/drafts')
    assert response.status_code == 200
    data = json.loads(response.data)

    assert 'sqlite_draft_data' in data
    assert 'dynamo_db_draft_data' in data
    assert 's3_draft_data' in data

    # all storage systems should have a list with lenght of 0
    assert len(data['sqlite_draft_data']) == 0
    assert len(data['dynamo_db_draft_data']) == 0
    assert len(data['s3_draft_data']) == 0


def test_get_all_drafts(client):
    response = client.get('/api/v1/drafts')
    assert response.status_code == 200
    # validate that all 3 storage systems are present
    data = json.loads(response.data)
    assert 'sqlite_draft_data' in data
    assert 'dynamo_db_draft_data' in data
    assert 's3_draft_data' in data


def test_get_single_draft_record(client, sample_draft_data):
    data = sample_draft_data
    post_response = client.post('/api/v1/drafts',
                                data=json.dumps(data),
                                content_type='application/json')
    draft_id = json.loads(post_response.data)['id']
    response = client.get(f'/api/v1/drafts/{draft_id}')
    assert response.status_code == 200

    record = json.loads(response.data)
    # validate that the record was stored in all 3 storage systems
    assert 'sqlite' in record
    assert 'dynamodb' in record
    assert 's3' in record
        
    # validate values in sqlite db
    if 'error' not in record['sqlite']:
        assert data['pick_number'] == record['sqlite']['pick_number']
        assert data['pro_team'] == record['sqlite']['pro_team']
        assert data['player_name'] == record['sqlite']['player_name']
        assert data['amateur_team'] == record['sqlite']['amateur_team']

    # validate the values in s3 and dynamodb
    if 'error' not in record['s3']:
        assert data['pick_number'] == record['s3']['pick_number']
        assert data['pro_team'] == record['s3']['pro_team']
        assert data['player_name'] == record['s3']['player_name']
        assert data['amateur_team'] == record['s3']['amateur_team']    

    if 'error' not in record['dynamodb']:
        assert data['pick_number'] == record['dynamodb']['pick_number']
        assert data['pro_team'] == record['dynamodb']['pro_team']
        assert data['player_name'] == record['dynamodb']['player_name']
        assert data['amateur_team'] == record['dynamodb']['amateur_team']    


def test_get_no_results(client):
    response = client.get(f'/api/v1/drafts/555')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'error' in data['sqlite']
    assert 'error' in data['s3']
    assert 'error' in data['dynamodb']


def test_get_incorrect_param(client):
    response = client.get(f'/api/v1/drafts/get_me')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert 'error' in data['sqlite']
    assert 'error' in data['s3']
    assert 'error' in data['dynamodb']

def test_create_draft(client, sample_draft_data):
    data = sample_draft_data
    response = client.post('/api/v1/drafts', 
                           data=json.dumps(sample_draft_data),
                           content_type='application/json')    
    assert response.status_code == 201
    data = json.loads(response.data)
    assert 'id' in data


def test_delete_draft_record(client, sample_draft_data):
    post_response = client.post('/api/v1/drafts',
                                data=json.dumps(sample_draft_data),
                                content_type='application/json')
    draft_id = json.loads(post_response.data)['id']
    response = client.delete(f'/api/v1/drafts/{draft_id}',
                             data=json.dumps(sample_draft_data),
                             content_type='application/json')
    assert response.status_code == 200


def test_update_draft_record(client, sample_draft_data):
    post_response = client.post('/api/v1/drafts',
                       data=json.dumps(sample_draft_data),
                       content_type='application/json')
    draft_id = json.loads(post_response.data)['id']
    updates = {
        "pick_number": "(77)",
        "pro_team": "Boston Celtics",
        "player_name": "John Calgary",
        "amateur_team": "Duke"
    }
    put_response = client.put(f'/api/v1/drafts/{draft_id}',
                              data=json.dumps(updates),
                              content_type='application/json')
    assert put_response.status_code == 200
    get_response = client.get(f'/api/v1/drafts/{draft_id}',
                              data=json.dumps(updates),
                              content_type='application/json')
    data = json.loads(get_response.data)
    name = data['sqlite']['player_name']
    assert name == "John Calgary"