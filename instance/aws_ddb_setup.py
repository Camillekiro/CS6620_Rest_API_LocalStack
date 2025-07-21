import boto3

def initialize_dynamodb(dynamodb_client: boto3.client, table_name: str) -> None:
    try:
        #https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/dynamodb/client/create_table.html
        dynamodb_client.create_table(
            AttributeDefinitions=[
                {
                    'AttributeName': 'id',
                    'AttributeType': 'N'
                },
            ],
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'id',
                    'KeyType': 'HASH'
                },
            ],
            BillingMode='PAY_PER_REQUEST'
        )
        print(f"Table {table_name} created successfully!")
    except Exception as e:
        print(f"Error creating DynamoDB table: {e}")