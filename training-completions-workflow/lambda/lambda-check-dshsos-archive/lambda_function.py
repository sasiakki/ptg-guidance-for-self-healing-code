#Remove Qualtrics DSHS O&S Feed from E2E Process
#https://seiu775bg.atlassian.net/browse/DT-551
'''
import json
from datetime import datetime, timedelta
import urllib.parse
import boto3
import time


print('Loading function')
s3 = boto3.client('s3')


client = boto3.client('glue')

response = client.get_job_runs(
    JobName='glue-dshs-os-completion-s3-to-raw',
)

res = response['JobRuns']


lastrun = res[0]
lastrunstatus = lastrun['JobRunState']
lastruntime = lastrun['CompletedOn']
lastruntime = lastruntime.strftime("%Y-%m-%d-%H-%M")
today = datetime.now() - timedelta(minutes=15)
today = today.strftime("%Y-%m-%d-%H-%M")

def lambda_handler(event, context):
    if lastrunstatus == 'SUCCEEDED' and lastruntime > today :
        return {'statusCode': 200,
        'result': True
    }
    else:
        return {'statusCode': 200,
                'result': False
            }
'''