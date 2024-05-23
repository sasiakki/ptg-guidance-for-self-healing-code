from datetime import datetime, timedelta
import boto3
from heapq import nlargest
import os
environment_type = os.environ["environment_type"]

def lambda_handler(event, context):

    glue_client = boto3.client('glue')

    job_name = f'{environment_type}-glue-transcript-corrections-s3-to-raw'

    get_job_runs_responses = glue_client.get_job_runs(JobName=job_name)[
        'JobRuns']

    succeeded_runs_list = []
    if len(get_job_runs_responses) > 0:
        for get_job_runs_response in get_job_runs_responses:
            if get_job_runs_response['JobRunState'] == 'SUCCEEDED':
                succeeded_runs_list.append(
                    get_job_runs_response['CompletedOn'])

        # Capture the last successful runtime 
        last_run_time = nlargest(1, succeeded_runs_list).pop().strftime("%Y-%m-%d-%H-%M")
        today = (datetime.now() - timedelta(minutes=15)).strftime("%Y-%m-%d-%H-%M")

        if last_run_time > today:
            return {'statusCode': 200, 'result': True }
        else:
            return {'statusCode': 200, 'result': False }

    else:
        return {'statusCode': 200, 'result': False }