import boto3
import os

def lambda_handler(event, context):
    
    account_num = os.environ['account_number']
    environment = os.environ['environment_type']

    state_machine_arn = f"arn:aws:states:us-west-2:{account_num}:stateMachine:{environment}-eligibility-calculation-workflow"
    
    print(state_machine_arn)

    sfn_client = boto3.client('stepfunctions')

    try:
        # Start the execution of the state machine
        response = sfn_client.start_execution(
            stateMachineArn=state_machine_arn
        )
        return {
            'statusCode': 200,
            'body': f'State machine execution started. Execution ARN: {response["executionArn"]}'
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': f'Error starting state machine execution: {str(e)}'
        }

