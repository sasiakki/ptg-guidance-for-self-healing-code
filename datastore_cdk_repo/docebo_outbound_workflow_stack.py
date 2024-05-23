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

class DoceboOutboundWorkflowStack(Stack):

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
            extra_python_lib = 's3://b2b-jars/python39-whl/paramiko-3.1.0-py3-none-any.whl'
            glue_connection = GlueConnection(self, 'glue_connection', 'rdsconnect')
        else:
            extra_python_lib ='s3://seiubg-b2bds-prod-glue-etl-scripts-b0p3e/dependencies/python39-whl/paramiko-3.1.0-py3-none-any.whl'

            glue_connection = GlueConnection(self, 'glue_connection', 'connection-uw2-p-seiubg-prod-b2bds')


        # Creating Glue jobs
        job = _glue_alpha.Job(self, "glue-docebo-new-useraccount-outbound",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V3_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('docebo-outbound/glue/glue-docebo-new-useraccount-outbound.py')
            ),
            role=glue_role,
            default_arguments={
                "--account_number": account_num,
                "--class": "GlueApp",
                "--environment_type": environment
            },
            connections = [glue_connection.get_connection()],
            job_name=environment+'-glue-docebo-new-useraccount-outbound',
            worker_type=_glue_alpha.WorkerType.G_1_X,
            worker_count=10
        )

        job = _glue_alpha.Job(self, "glue-docebo-new-trainingfile-outbound",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V3_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('docebo-outbound/glue/glue-docebo-new-trainingfile-outbound.py')
            ),
            default_arguments={
                "--account_number": account_num,
                "--class": "GlueApp",
                "--environment_type": environment
            },
            connections = [glue_connection.get_connection()],
            role=glue_role,
            job_name=environment+'-glue-docebo-new-trainingfile-outbound',
            worker_type=_glue_alpha.WorkerType.G_1_X,
            worker_count=10

        )

        job = _glue_alpha.Job(self, "glue-docebo-update-useraccount-outbound",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V3_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('docebo-outbound/glue/glue-docebo-update-useraccount-outbound.py')
            ),
            role=glue_role,
            default_arguments={
                "--account_number": account_num,
                "--class": "GlueApp",
                "--environment_type": environment
            },            
            connections = [glue_connection.get_connection()],
            job_name=environment+'-glue-docebo-update-useraccount-outbound',
            worker_type=_glue_alpha.WorkerType.G_1_X,
            worker_count=10
        )

        glue_task_1 = tasks.GlueStartJobRun(
            self, 
            id="glue_docebo_new_useraccount_outbound", 
            glue_job_name=environment+"-glue-docebo-new-useraccount-outbound", 
            integration_pattern=sfn.IntegrationPattern.RUN_JOB
        )

        glue_task_2 = tasks.GlueStartJobRun(
            self, 
            id="glue_docebo_new_trainingfile_outbound", 
            glue_job_name=environment+"-glue-docebo-new-trainingfile-outbound", 
            integration_pattern=sfn.IntegrationPattern.RUN_JOB
        )

        glue_task_3 = tasks.GlueStartJobRun(
            self, 
            id="glue_docebo_update_useraccount_outbound", 
            glue_job_name=environment+"-glue-docebo-update-useraccount-outbound", 
            integration_pattern=sfn.IntegrationPattern.RUN_JOB
        )
        

        machine_definition = glue_task_1.next(glue_task_2.next(glue_task_3))

        sfn.StateMachine(self,"docebo-outbound-workflow", 
            definition=machine_definition,            
            state_machine_name=environment+"-docebo-outbound-workflow"
        )
