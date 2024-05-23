from constructs import Construct
from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_glue as _glue,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as tasks,
    aws_iam,
    aws_glue_alpha as _glue_alpha,
    Duration as duration,
    aws_stepfunctions as stepfunctions
)
from .glue_connection import GlueConnection
from bin.get_caller_identity import AccountNumberGetter
from bin.ec2_utils import EC2Utils

class CredentialWorkflowStack(Stack):

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

        if environment == 'dev':
            glue_connection = GlueConnection(self, 'glue_connection', 'rdsconnect')
        else:
           glue_connection = GlueConnection(self, 'glue_connection', 'connection-uw2-p-seiubg-prod-b2bds')

        # Creating lambda's functions & Glue jobs 
        lambda_check_credential = _lambda.Function(
            self, 'lambda_check_credential',
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset('credential-workflow/lambda/lambda-check-credential/'),
            handler='lambda_function.lambda_handler',
            function_name=environment+'-lambda-check-credential',
            role=lambda_role,
            timeout=duration.minutes(2),
            environment={
                'account_number': account_num,
                'environment_type': environment
            }
        )

        job = _glue_alpha.Job(self, "glue-credentials-delta-processing",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('credential-workflow/glue/glue-credentials-delta-processing.py')
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                            "--account_number": account_num,
                            "--environment_type": environment
            },  
            role=glue_role,
            job_name=environment+'-glue-credentials-delta-processing'
        )

        job = _glue_alpha.Job(self, "glue-credentials-delta-raw-to-staging-personhistory",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('credential-workflow/glue/glue-credentials-delta-raw-to-staging-personhistory.py')
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                            "--account_number": account_num,
                            "--environment_type": environment
            },  
            role=glue_role,
            job_name=environment+'-glue-credentials-delta-raw-to-staging-personhistory'
        )

        #job = _glue_alpha.Job(self, "glue-credentials-delta-to-prodcredentials",
        #    executable=_glue_alpha.JobExecutable.python_etl(
        #        glue_version=_glue_alpha.GlueVersion.V4_0,
        #        python_version=_glue_alpha.PythonVersion.THREE,
        #        script=_glue_alpha.Code.from_asset('credential-workflow/glue/glue-credentials-delta-to-prodcredentials.py')
        #    ),
        #    connections = [glue_connection.get_connection()],

        #    default_arguments={
        #                    "--account_number": account_num,
        #                    "--environment_type": environment
        #    },  
        #    role=glue_role,
        #    job_name=environment+'-glue-credentials-delta-to-prodcredentials'
        #)

        job = _glue_alpha.Job(self, "glue-credentials-doh-s3-to-raw",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('credential-workflow/glue/glue-credentials-doh-s3-to-raw.py')
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                            "--account_number": account_num,
                            "--environment_type": environment
            },  
            role=glue_role,
            job_name=environment+'-glue-credentials-doh-s3-to-raw'
        )

        job = _glue_alpha.Job(self, "glue-credentials-ospi-s3-to-raw",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('credential-workflow/glue/glue-credentials-ospi-s3-to-raw.py')
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                            "--account_number": account_num,
                            "--environment_type": environment
            },  
            role=glue_role,
            job_name=environment+'-glue-credentials-ospi-s3-to-raw'
        )              

        #Defining all task for lamba's and glue
        lambda_task_1 = tasks.LambdaInvoke(self, "lambda-check-credential",
            lambda_function=lambda_check_credential,
            # Lambda's result is in the attribute `Payload`
            result_path="$.Payload"
        )

        glue_task_2 = tasks.GlueStartJobRun(
            self,
            id="glue_credentials_doh_s3_to_raw",
            glue_job_name=environment+"-glue-credentials-doh-s3-to-raw",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB 
        )
        
        glue_task_3 = tasks.GlueStartJobRun(
            self,
            id="glue_credentials_ospi_s3_to_raw",
            glue_job_name=environment+"-glue-credentials-ospi-s3-to-raw",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB 
        )

        glue_task_4 = tasks.GlueStartJobRun(
            self,
            id="glue_credentials_delta_processing",
            glue_job_name=environment+"-glue-credentials-delta-processing",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB 
        )

        glue_task_5 = tasks.GlueStartJobRun(
            self,
            id="glue_credentials_delta-raw_to_staging_personhistory",
            glue_job_name=environment+"-glue-credentials-delta-raw-to-staging-personhistory",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB 
        )

        end_credential_process=sfn.Pass(self, "end-credential-process")

        machine_definition = lambda_task_1.next(sfn.Choice(self,"has-files")
            .when(
                sfn.Condition.boolean_equals("$.Payload.Payload.result", True),
                glue_task_2.next(glue_task_3.next(glue_task_4.next(glue_task_5)))
            )
            .otherwise(end_credential_process))
        sfn.StateMachine(self, "credential-workflow",
            definition=machine_definition,
            state_machine_name=environment+"-credential-workflow"
        )
