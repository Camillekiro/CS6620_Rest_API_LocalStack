import boto3

def initialize_s3(s3_client: boto3.client, bucket_name: str) -> None:
    try:
        #https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3/client/create_bucket.html
        s3_client.create_bucket(Bucket=bucket_name)
        print(f"successfully created s3 bucket: {bucket_name}")
    except Exception as e:
        print(f"Error creating s3 bucket: {e}")