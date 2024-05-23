from constructs import Construct
from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_glue as _glue,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as tasks,
    aws_iam,
    aws_glue_alpha as _glue_alpha,
    aws_stepfunctions as stepfunctions
)
from .glue_connection import GlueConnection
from bin.get_caller_identity import AccountNumberGetter

class SalesforceoutboundWorkflowStack(Stack):

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

        job = _glue_alpha.Job(self, "glue-sf-outbound-person",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('salesforce-outbound-workflow/glue/glue-sf-outbound-person.py')
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                            "--account_number": account_num,
                            "--environment_type": environment
            },  
            role=glue_role,
            job_name=environment+'-glue-sf-outbound-person'
        )

        job = _glue_alpha.Job(self, "glue-sf-outbound-employmentrelationship",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('salesforce-outbound-workflow/glue/glue-sf-outbound-employmentrelationship.py')
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                            "--account_number": account_num,
                            "--environment_type": environment
            },  
            role=glue_role,
            job_name=environment+'-glue-sf-outbound-employmentrelationship'
        )

        job = _glue_alpha.Job(self, "glue-sf-outbound-credential",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('salesforce-outbound-workflow/glue/glue-sf-outbound-credential.py')
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                            "--account_number": account_num,
                            "--environment_type": environment
            },  
            role=glue_role,
            job_name=environment+'-glue-sf-outbound-credential'
        )

        job = _glue_alpha.Job(self, "glue-sf-outbound-employer",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('salesforce-outbound-workflow/glue/glue-sf-outbound-employer.py')
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                            "--account_number": account_num,
                            "--environment_type": environment
            },  
            role=glue_role,
            job_name=environment+'-glue-sf-outbound-employer'
        )

        job = _glue_alpha.Job(self, "glue-sf-benefits-certification-fund",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('salesforce-outbound-workflow/glue/glue-sf-benefits-certification-fund.py')
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                            "--account_number": account_num,
                            "--environment_type": environment
            },  
            role=glue_role,
            job_name=environment+'-glue-sf-benefits-certification-fund'
        )


        #Defining all task for lamba's and glue

        glue_task_1 = tasks.GlueStartJobRun(
            self,
            id="glue_sf_outbound_person",
            glue_job_name=environment+"-glue-sf-outbound-person",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB
        )
        
        glue_task_2 = tasks.GlueStartJobRun(
            self,
            id="glue_sf_outbound_employmentrelationship",
            glue_job_name=environment+"-glue-sf-outbound-employmentrelationship",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB
        )

        glue_task_3 = tasks.GlueStartJobRun(
            self,
            id="glue_sf_outbound_credential",
            glue_job_name=environment+"-glue-sf-outbound-credential",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB
        )

        glue_task_4 = tasks.GlueStartJobRun(
            self,
            id="glue_sf_outbound_employer",
            glue_job_name=environment+"-glue-sf-outbound-employer",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB
        )

        glue_task_5 = tasks.GlueStartJobRun(
            self,
            id="glue_sf_benefits_certification_fund",
            glue_job_name=environment+"-glue-sf-benefits-certification-fund",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB
        )

       

        machine_definition = glue_task_1.next(glue_task_2.next(glue_task_3.next(glue_task_4.next(glue_task_5))))
        
        sfn.StateMachine(self, "salesforce-outbound-workflow",
            definition=machine_definition,
            state_machine_name=environment+"-salesforce-outbound-workflow"
        )
