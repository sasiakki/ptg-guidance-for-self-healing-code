import json
import boto3
import os


def lambda_handler(event, context):
    # Specify the path to search in the S3 bucket.
    filename_to_check = "Caregiverdata"
    # Get S3 bucket objects with the prefix specified.
    path_to_check = "Inbound/raw/qualtrics/caregiver_intake/"

    environment_type = os.environ['environment_type']
    
    # Retrieve secrets from AWS Secrets Manager.
    secrets_manager_client = boto3.client('secretsmanager')
    try:
        s3_response = secrets_manager_client.get_secret_value(
            SecretId="{}/b2bds/s3".format(environment_type))
    except Exception as e:
        print(f"Failed to retrieve Secrets Manager secret: {e}")
        return {'statusCode': 500, 'error': 'Failed to retrieve Secrets Manager secret.', 'result': False}
    # Load secret string response into JSON.
    try:
        s3_secrets = json.loads(s3_response['SecretString'])
    except Exception as e:
        print(f"Failed to parse Secrets Manager secret: {e}")
        return {'statusCode': 500, 'error': 'Failed to parse Secrets Manager secret.', 'result': False}
    # Get S3 bucket from secrets.
    try:
        s3_bucket_name = s3_secrets['datafeeds']

    except Exception as e:
        print(
            f"Failed to get S3 bucket information from Secrets Manager secret: {e}")
        return {'statusCode': 500, 'error': 'Failed to get S3 bucket information from Secrets Manager secret.', 'result': False}
    # Access S3 resource.
    s3_resource = boto3.resource('s3')
    # Get S3 bucket objects with the prefix specified.
    try:
        s3_objects = list(s3_resource.Bucket(
            s3_bucket_name).objects.filter(Prefix=path_to_check))
    except Exception as e:
        print(f"Failed to get S3 objects with prefix '{path_to_check}': {e}")
        return {'statusCode': 500, 'error': f"Failed to get S3 objects with prefix '{path_to_check}'.", 'result': False}
    # Check all objects in the S3 bucket for the specified path.
    found_path = False
    for s3_object in s3_objects:
        if filename_to_check in str(s3_object):
            found_path = True
            break
    if found_path:
        return {'statusCode': 200, 'result': True}
    else:
        return {'statusCode': 200, 'result': False}
