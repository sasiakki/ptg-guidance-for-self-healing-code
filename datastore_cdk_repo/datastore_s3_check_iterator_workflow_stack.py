from constructs import Construct
from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_glue as _glue,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as tasks,
    aws_iam,
    Duration as duration,
    aws_stepfunctions as stepfunctions
)
from bin.get_caller_identity import AccountNumberGetter

class DSCheckIteratorWorkflowStack(Stack):

    def __init__(self, scope: Construct, id: str, environment: str, account_num: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Get the IAM role by name
        lambda_role = aws_iam.Role.from_role_name(
                self,"LambdaRole", 
                'role-d-lambda-execute'
        )
        glue_role = aws_iam.Role.from_role_name(
            self,"GlueRole", 
            'role-p-glue-data-pipelines'
        )

        # Creating lambda's functions & Glue jobs 
        lambda_check_files = _lambda.Function(
            self, 'lambda_check_files',
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset('datastore-s3-check-iterator/lambda/lambda-check-files/'),
            handler='lambda_function.lambda_handler_all',
            function_name=environment+'-lambda_check_files',
            role=lambda_role,
            timeout=duration.minutes(1),
            environment={
                    'account_number': account_num,
                    'environment_type': environment}
        )

        #Defining all task for lamba's and glue
        lambda_task_1 = tasks.LambdaInvoke(self, "lambda-check-files",
            lambda_function=lambda_check_files,
            # Lambda's result is in the attribute `Payload`
            output_path="$.Payload"
        )

        machine_definition = lambda_task_1
        
        sfn.StateMachine(self, "datastore-s3-check-iterator",
            definition=machine_definition,
            state_machine_name=environment+"-datastore-s3-check-iterator"
        )
