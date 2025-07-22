import pytest
import json
import sys
import os

#add app dir to the python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

from app.application import app, db, Draft

@pytest.fixture
def client():
    """Create a test client and set up test db"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:' #in memory db for tests
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
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


def test_get_all_drafts(client):
    response = client.get('/api/v1/drafts')
    assert response.status_code == 200


def test_get_single_draft_record(client, sample_draft_data):
    data = sample_draft_data
    post_response = client.post('/api/v1/drafts',
                                data=json.dumps(data),
                                content_type='application/json')
    draft_id = json.loads(post_response.data)['id']
    response = client.get(f'/api/v1/drafts/{draft_id}')
    assert response.status_code == 200

    record = json.loads(response.data)
    assert data['player_name'] == record['sqlite']['player_name']


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
    name = data['player_name']
    assert name == "John Calgary"