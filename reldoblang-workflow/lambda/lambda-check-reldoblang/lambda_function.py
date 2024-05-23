import json
import urllib.parse
import boto3
import os

print('Loading function')

s3 = boto3.client('s3')

def lambda_handler(event, context):
    
    checkpath = '01250_RelDOBLang_ADSAToTP'
    account_number = os.environ['account_number']
    if account_number == '259367569391':
        environment_type = 'prod'
    else:
        environment_type = 'dev'
    
    # Accessing the Secrets Manager from boto3 lib s
    secretsmangerclient = boto3.client('secretsmanager') 
    # Accessing the secrets value for S3 Bucket 
    s3response = secretsmangerclient.get_secret_value( SecretId=environment_type+'/b2bds/s3' ) 
    s3_secrets = json.loads(s3response['SecretString']) 
    S3_BUCKET = s3_secrets['datafeeds']
    
    s3_resource = boto3.resource('s3')

    objects = list(s3_resource.Bucket(S3_BUCKET).objects.filter(Prefix='Inbound/raw/reldob/'))
    for i in objects: 
        if checkpath in str(i):
            return {'statusCode': 200,
            'result': True
        } 
    return {'statusCode': 200,
            'result': False
        }
