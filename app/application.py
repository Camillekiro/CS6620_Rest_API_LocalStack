from flask import Flask, request, Blueprint
from flask_sqlalchemy import SQLAlchemy
import boto3
import json
from instance.aws_ddb_setup import initialize_dynamodb
from instance.aws_s3_setup import initialize_s3

#high level config variables
S3_BUCKET_NAME='draft-bucket'
DDB_TABLE_NAME='drafts'

#https://discuss.localstack.cloud/t/set-up-s3-bucket-using-docker-compose/646.html
s3_client = boto3.client(
    "s3",
    endpoint_url="http://localhost:4566",
    aws_access_key_id="test",
    aws_secret_access_key="test",
    region_name="us-east-1"
)

ddb_client = boto3.client(
    "dynamodb",
    endpoint_url="http://localhost:4566",
    aws_access_key_id="test",
    aws_secret_access_key="test",
    region_name="us-east-1"
)

db = SQLAlchemy()
app = Flask(__name__)
# configurations for sqlite db
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///data.db"
app.config["SQLALCHEMY_TRACK_MODIFICATION"] = False
db.init_app(app)


class Draft(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    draft_pick_number = db.Column(db.String(255), nullable=False)
    pro_team_name = db.Column(db.String(255), nullable=False)
    player_name = db.Column(db.String(255), unique=True, nullable=False)
    amateur_team_name = db.Column(db.String(255))

    def __repr__(self):
        return f"{self.draft_pick_number} - {self.pro_team_name} - {self.player_name} - {self.amateur_team_name}"

#create API version blueprints
v1 = Blueprint('v1', __name__, url_prefix='/api/v1')
@v1.route('/')
def index():
    return "Hello World!"


@v1.route('/drafts')
def get_drafts():
    drafts = Draft.query.all()
    sqlite_output = []
    for d in drafts:
        draft_data = {
            "pick_number": d.draft_pick_number,
            "pro_team": d.pro_team_name,
            "player_name": d.player_name,
            "amateur_team": d.amateur_team_name
        }
        sqlite_output.append(draft_data)
    # dynamoDB
    # https://stackoverflow.com/questions/10450962/how-can-i-fetch-all-items-from-a-dynamodb-table-without-specifying-the-primary-k
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb/client/scan.html
    dynamodb_output = []
    try:
        ddb_draft_response = ddb_client.scan(TableName=DDB_TABLE_NAME)
        items = ddb_draft_response['Items']
        for item in items:
            draft_data={
                "id": item['id']['N'],
                "pick_number": item['pick_number']['S'],
                "pro_team": item['pro_team']['S'],
                "player_name": item['player_name']['S'],
                "amateur_team": item['amateur_team']['S']
            }
            dynamodb_output.append(draft_data)
            print(f"Successfull retrieved records from DynamoDB table: {DDB_TABLE_NAME}")
    except Exception as e:
        print(f"Error retrieving DynamoDB records: {e}")

    # s3
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/list_objects_v2.html
    s3_output = []
    try:
        s3_draft_response = s3_client.list_objects_v2(Bucket=S3_BUCKET_NAME)
        if 'Contents' in s3_draft_response:
            for object in s3_draft_response['Contents']:
                file_response = s3_client.get_object(Bucket=S3_BUCKET_NAME)
                draft_data = json.loads(file_response['Body'].read())
                s3_output.append(draft_data)
    except Exception as e:
        print(f"Error retrieving s3 Contents: {e}")
    return {
        "sqlite_draft_data": sqlite_output,
        "dynamo_db_draft_data": dynamodb_output,
        "s3_draft_data": s3_output
        }


@v1.route('/drafts/<id>')
def get_draft_record(id):
    results = {}
    try:
        draft_rec = db.get_or_404(Draft, id)
        results["sqlite"] = {
            "id": draft_rec.id,
            "pick_number": draft_rec.draft_pick_number,
            "pro_team": draft_rec.pro_team_name,
            "player_name": draft_rec.player_name,
            "amateur_team": draft_rec.amateur_team_name
        }
    except Exception as e:
        print(f"Error retrieving record from sqlite db: {e}")
        results["sqlite"]={"error": "Record not found"}
    
    # dynamo db
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb/client/get_item.html
    try:
        ddb_response = ddb_client.get_item(TableName=DDB_TABLE_NAME, Key={'id': {'N': str(id)}})
        if 'Item' in ddb_response:
            item = ddb_response['Item']
            results["dynamodb"] = {
                "id": item['id']['N'],
                "pick_number": item['pick_number']['S'],
                "pro_team": item['pro_team']['S'],
                "player_name": item['player_name']['S'],
                "amateur_team": item['amateur_team']['S']
            }
        else:
            results["dynamodb"] = {"error": "Record not found"}
    except Exception as e:
        print(f"Error retrieving record from dynamodb:{e}")
        results["dynamodb"] = {"error": "Record not found"}

    # s3
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/get_object.html
    try:
        s3_response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=f'draft_{id}.json')
        results["s3"] = json.loads(s3_response['Body'].read())
    except Exception as e:
        print(f"Error retrieving record from s3:{e}")
        results["s3"] = {"error": "Record not found"}
    return results


@v1.route('/drafts', methods=['POST'])
def add_draft_record():
    # dupe check
    dupe_player = Draft.query.filter_by(player_name=request.json["player_name"]).first()
    if dupe_player:
        return {"error": "Player already exists in draft db"}, 409
    draft_rec = Draft(draft_pick_number=request.json["pick_number"], 
                      pro_team_name=request.json["pro_team"], 
                      player_name=request.json["player_name"], 
                      amateur_team_name=request.json["amateur_team"])
    db.session.add(draft_rec)
    db.session.commit()
    # store the auto incrementing pk generated from sqlalchemy
    draft_id = draft_rec.id
    
    # dynamo db
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb/client/put_item.html
    try:
        ddb_client.put_item(
            TableName=DDB_TABLE_NAME,
            Item={
                'id': {'N': str(draft_id)},
                'pick_number': {'S': request.json["pick_number"]},
                'pro_team': {'S': request.json["pro_team"]},
                'player_name': {'S': request.json["player_name"]},
                'amateur_team': {'S': request.json["amateur_team"]}
            }
        )
    except Exception as e:
        print(f"DynamoDB put error: {e}")

    # s3
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/put_object.html
    try:
        s3_data = {
            "id": draft_id,
            "pick_number": request.json["pick_number"],
            "pro_team": request.json["pro_team"],
            "player_name": request.json["player_name"],
            "amateur_team": request.json["amateur_team"]
        }
        s3_client.put_object(
            Bucket=S3_BUCKET_NAME,
            Key=f'draft_{draft_id}.json',
            Body=json.dumps(s3_data)
        )
    except Exception as e:
        print(f"S3 put error: {e}")

    return {"id": draft_rec.id}, 201


@v1.route('/drafts/<id>', methods=['DELETE'])
def delete_draft_record(id):
    # existence validation
    draft_rec = db.get_or_404(Draft, id)
    # s3
    try:
        s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=f'draft_{id}.json')
    except s3_client.exceptions.NoSuchKey:
        return {"message": "s3 object not found"}, 404

    # dynamodb
    try:
        ddb_response = ddb_client.get_item(TableName=DDB_TABLE_NAME, Key={'id': {'N': str(id)}})
        if 'Item' not in ddb_response:
            return {"message": "dynamodb item not found"}, 404
    except Exception as e:
        print(f"Error during dynamodb get operation:{e}")
        return {"message": "Error during dynamodb get operation"}, 500
    
    # delete from all 3 storage systems after validating existence
    db.session.delete(draft_rec)
    db.session.commit()
    # s3
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/delete_object.html
    try:
        s3_client.delete_object(Bucket=S3_BUCKET_NAME, Key=f'draft_{id}.json')
    except Exception as e:
        print(f"Error occured during S3 object deletion: {e}")
        return {"message": "Error occured during s3 delete operation"}, 500

    # ddb
    # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb/client/delete_item.html

    try:
        ddb_client.delete_item(TableName=DDB_TABLE_NAME, Key={'id': {'N': str(id)}})
    except Exception as e:
        print(f"Error occured during DynamoDB item deletion: {e}")
        return {"message": "Error occured during DynamoDB delete operation"}, 500

    return {"message": "Successful deleted record from all storage systems!"}, 200


@v1.route('/drafts/<id>', methods=['PUT'])
def update_draft_record(id):
    # existence validation
    draft_rec = db.get_or_404(Draft, id)
    if not request.json:
        return {"error": "No JSON data provided"}, 400
    # s3
    try:
        s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=f'draft_{id}.json')
    except s3_client.exceptions.NoSuchKey:
        return {"message": "s3 object not found"}, 404

    # dynamodb
    try:
        ddb_response = ddb_client.get_item(TableName=DDB_TABLE_NAME, Key={'id': {'N': str(id)}})
        if 'Item' not in ddb_response:
            return {"message": "dynamodb item not found"}, 404
    except Exception as e:
        print(f"Error during dynamodb get operation:{e}")
        return {"message": "Error during dynamodb get operation"}, 500
    # update all 3 storage systems
    try:
        draft_rec.draft_pick_number = request.json["pick_number"] 
        draft_rec.pro_team_name = request.json["pro_team"]
        draft_rec.player_name = request.json["player_name"]
        draft_rec.amateur_team_name = request.json["amateur_team"]
        db.session.commit()

        try:
            s3_data = {
                "id": int(id),
                "pick_number": request.json["pick_number"],
                "pro_team": request.json["pro_team"],
                "player_name": request.json["player_name"],
                "amateur_team": request.json["amateur_team"]
            }
            s3_client.put_object(
                Bucket=S3_BUCKET_NAME,
                Key=f'draft_{id}.json',
                Body=json.dumps(s3_data)
            )
        except Exception as e:
            print(f"Error occurred during S3 object update: {e}")
            return {"message": "Error occured during S3 update operation"}, 500
        
        try:
            ddb_client.put_item(
                TableName=DDB_TABLE_NAME,
                Item={
                    "id": {'N': str(id)},
                    "pick_number": {'S': request.json["pick_number"]},
                    "pro_team": {'S': request.json["pro_team"]},
                    "player_name": {'S': request.json["player_name"]},
                    "amateur_team": {'S': request.json["amateur_team"]}
                }
            )
        except Exception as e:
            print(f"Error occurred during DynamoDB item update: {e}")
            return {"message": "Error occured during DynamoDB update operation"}, 500
            
        return {"message": "Draft record updated succesfully on all storage systems!"}, 200
    except KeyError as e:
        return {"error": f"missing requried field: {e}"}, 400
    except Exception as e:
        db.session.rollback()
        return {"error": "Failed to update record"}, 500

#register the blueprint
app.register_blueprint(v1)
#root route for API info
@app.route('/')
def root():
    return{
        "message": "Draft API",
        "versions": {
            "v1": "/api/v1/"
        },
        "current_version": "1.0"
    }

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        initialize_s3(s3_client=s3_client, bucket_name=S3_BUCKET_NAME)
        initialize_dynamodb(dynamodb_client=ddb_client, table_name=DDB_TABLE_NAME)

    app.run(debug=True)