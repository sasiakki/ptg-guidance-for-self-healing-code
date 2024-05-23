from constructs import Construct
from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_glue as _glue,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as tasks,
    aws_iam,
    aws_glue_alpha as _glue_alpha,
    Duration as duration
)
import boto3
from bin.get_caller_identity import AccountNumberGetter
from .glue_connection import GlueConnection
from bin.ec2_utils import EC2Utils


class LambdaLayer(Construct):
    def __init__(self, scope: Construct, id: str):
        super().__init__(scope, id)

        # Create an instance of AccountNumberGetter
        account_number = AccountNumberGetter()

        # Call the get_account_number method
        account_num = account_number.get_account_number()


        # Add layer using an ARN
        arn_layer_arn = (
            f"arn:aws:lambda:us-west-2:{account_num}:layer:eligibility-dependencies:1"
        )
        arn_layer = _lambda.LayerVersion.from_layer_version_arn(
            self, "eligibility-dependencies", arn_layer_arn
        )
        # Store the layers in a list
        self.layers = [arn_layer]

class TranscriptRetractionsWorkflowStack(Stack):

    def __init__(self,scope: Construct,id: str,environment: str, account_num: str, **kwargs) -> None:
        super().__init__(scope,id,**kwargs)
        
        

        # Get the IAM role by name
        lambda_role = aws_iam.Role.from_role_name(
            self, "LambdaRole", "role-d-lambda-execute"
        )

        glue_role = aws_iam.Role.from_role_name(
            self, "GlueRole", "role-p-glue-data-pipelines"
        )


        

        state_machine_arn = f"arn:aws:states:us-west-2:{account_num}:stateMachine:{environment}-eligibility-calculation-workflow"
        start_execution_policy = aws_iam.PolicyStatement(
        effect=aws_iam.Effect.ALLOW,
        actions=["states:StartExecution"],
        resources=[state_machine_arn]
        )
        
        
        if environment == 'dev':
            # Get the IAM role by name
            lambda_role.add_to_principal_policy(start_execution_policy)
            glue_connection = GlueConnection(self, 'glue_connection', 'rdsconnect')
        else:
            # Get the IAM role by name
            lambda_role.add_to_principal_policy(start_execution_policy)
            glue_connection = GlueConnection(self, 'glue_connection', 'connection-uw2-p-seiubg-prod-b2bds')

        job = _glue_alpha.Job(self, "glue-transcript-noshow-s3-to-raw",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('transcripts-retraction-workflow/glue/glue-transcript-noshow-s3-to-raw.py')
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                            "--account_number": account_num,
                            "--environment_type": environment
            },  
            role=glue_role,
            job_name=environment+'-glue-transcript-noshow-s3-to-raw'
        )

        job = _glue_alpha.Job(self, "glue-transcript-noshow-raw-to-staging",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('transcripts-retraction-workflow/glue/glue-transcript-noshow-raw-to-staging.py')
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                            "--account_number": account_num,
                            "--environment_type": environment
            },  
            role=glue_role,
            job_name=environment+'-glue-transcript-noshow-raw-to-staging'
        )

        job = _glue_alpha.Job(self, "glue-process-transcript-retraction",
            executable=_glue_alpha.JobExecutable.python_shell(
                glue_version=_glue_alpha.GlueVersion.V1_0,
                python_version=_glue_alpha.PythonVersion.THREE_NINE,
                script=_glue_alpha.Code.from_asset('transcripts-retraction-workflow/glue/glue-process-transcript-retraction.py')
            ),
            role=glue_role,
            connections = [glue_connection.get_connection()],
            default_arguments={
                "--account_number": account_num,
                "--environment_type": environment
            },  
            job_name=environment+'-glue-process-transcript-retraction'

        )

        lambda_invoke_eligibility = _lambda.Function(
            self, 'lambda-invoke-eligibility',
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset('transcripts-retraction-workflow/lambda/lambda-invoke-eligibility-calculation-statemachine/'),
            handler='lambda_function.lambda_handler',
            function_name=environment+'-lambda_invoke_eligibility-calculation-statemachine',
            role=lambda_role,
            timeout=duration.minutes(5),
            environment={
                    'account_number': account_num,
                    'environment_type': environment
                    }
        )

        #Defining all task for lamba's and glue

        glue_task_1 = tasks.GlueStartJobRun(
            self,
            id="glue_transcript_noshow_s3_to_raw",
            glue_job_name=environment+"-glue-transcript-noshow-s3-to-raw",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB
        )
        
        glue_task_2 = tasks.GlueStartJobRun(
            self,
            id="glue_transcript_noshow_raw_to_staging",
            glue_job_name=environment+"-glue-transcript-noshow-raw-to-staging",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB
        )

        glue_task_3 = tasks.GlueStartJobRun(
            self,
            id="glue_process_transcript_retraction",
            glue_job_name=environment+"-glue-process-transcript-retraction",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB
        )

        lambda_task_1 = tasks.LambdaInvoke(self, "lambda_invoke_eligibility",
            lambda_function=lambda_invoke_eligibility,
        )
        
        machine_definition = glue_task_1.next(glue_task_2.next(glue_task_3.next(lambda_task_1)))

        
        sfn.StateMachine(self, "transcripts-retraction-workflow",
            definition=machine_definition,
            state_machine_name=environment+"-transcripts-retraction-workflow"
        )
