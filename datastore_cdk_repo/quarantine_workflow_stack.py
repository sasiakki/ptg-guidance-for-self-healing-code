from constructs import Construct
from aws_cdk import (
    Stack, 
    aws_lambda as _lambda, 
    aws_glue as _glue, 
    aws_stepfunctions as sfn, 
    aws_stepfunctions_tasks as tasks, 
    aws_rds as rds, 
    aws_iam as aws_iam, 
    aws_glue_alpha as _glue_alpha,
    aws_stepfunctions as stepfunctions
)
from .glue_connection import GlueConnection
from bin.get_caller_identity import AccountNumberGetter

class QuarantineWorkflowStack(Stack):

    def __init__(self,scope: Construct,id: str,environment: str, account_num: str, **kwargs) -> None:
        super().__init__(scope,id,**kwargs)
        
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

        job = _glue_alpha.Job(self, "glue-approve-personquarantine-records",
            executable=_glue_alpha.JobExecutable.python_shell(
                glue_version=_glue_alpha.GlueVersion.V1_0,
                python_version=_glue_alpha.PythonVersion.THREE_NINE,
                script=_glue_alpha.Code.from_asset('quarantine-approval-workflow/glue/glue-approve-personquarantine-records.py')
            ),
            connections = [glue_connection.get_connection()],
            default_arguments={
                "--account_number": account_num,
                "--environment_type": environment
            },  
            role=glue_role,
            job_name=environment+'-glue-approve-personquarantine-records',
        )

        job = _glue_alpha.Job(self, "glue-quarantine-personmastering",
            executable=_glue_alpha.JobExecutable.python_shell(
                glue_version=_glue_alpha.GlueVersion.V1_0,
                python_version=_glue_alpha.PythonVersion.THREE_NINE,
                script=_glue_alpha.Code.from_asset('quarantine-approval-workflow/glue/glue-quarantine-personmastering.py')
            ),
            connections = [glue_connection.get_connection()],
            default_arguments={
                "--account_number": account_num,
                "--environment_type": environment
            },  
            role=glue_role,
            job_name=environment+'-glue-quarantine-personmastering',
        )
        
        glue_task_1 = tasks.GlueStartJobRun(
            self, 
            id="glue_approve_personquarantine_records", 
            glue_job_name=environment+"-glue-approve-personquarantine-records", 
            integration_pattern=sfn.IntegrationPattern.RUN_JOB
        )
    
        glue_task_2 = tasks.GlueStartJobRun(
            self, 
            id="glue_quarantine_personmastering", 
            glue_job_name=environment+"-glue-quarantine-personmastering", 
            integration_pattern=sfn.IntegrationPattern.RUN_JOB
        )

        machine_definition = glue_task_1.next(glue_task_2)
        
        sfn.StateMachine(self,"quarantine-workflow", 
            definition=machine_definition,
            state_machine_name=environment+"-quarantine-workflow"
        )

        