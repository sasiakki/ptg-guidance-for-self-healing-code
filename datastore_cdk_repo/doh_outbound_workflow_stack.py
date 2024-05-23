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

class DohOutboundWorkflowStack(Stack):

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

        extra_python_lib ='s3://seiu-b2bds-glue-dependencies/paramiko-3.1.0-py3-none-any.whl'


        # Creating Glue jobs
        job = _glue_alpha.Job(self, "glue-doh-completed-outbound",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V3_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('doh-outbound-workflow/glue/glue-doh-completed-outbound.py')
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                "--account_number": account_num,
                "--environment_type": environment
            },  
            role=glue_role,
            job_name=environment+'-glue-doh-completed-outbound'

        )

        job = _glue_alpha.Job(self, "glue-dohcompleted-sftp-upload",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V3_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('doh-outbound-workflow/glue/glue-dohcompleted-sftp-upload.py')
            ),
            role=glue_role,
            default_arguments={
                "--account_number": account_num,
                "--additional-python-modules": extra_python_lib,
                "--environment_type": environment    
            },  
            job_name=environment+'-glue-dohcompleted-sftp-upload',
            worker_type=_glue_alpha.WorkerType.G_1_X,
            worker_count=2
        )

        job = _glue_alpha.Job(self, "glue-doh-classified-outbound",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V3_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('doh-outbound-workflow/glue/glue-doh-classified-outbound.py')
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                "--account_number": account_num,
                "--environment_type": environment
            },  
            role=glue_role,
            job_name=environment+'-glue-doh-classified-outbound'

        )

        job = _glue_alpha.Job(self, "glue-dohclassified-sftp-upload",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V3_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('doh-outbound-workflow/glue/glue-dohclassified-sftp-upload.py')
            ),
            role=glue_role,
            default_arguments={
                "--account_number": account_num,
                "--additional-python-modules": extra_python_lib,
                "--environment_type": environment
            },  
            job_name=environment+'-glue-dohclassified-sftp-upload',
            worker_type=_glue_alpha.WorkerType.G_1_X,
            worker_count=2
        )

        #Defining all task for glue
        glue_task_1 = tasks.GlueStartJobRun(
            self,
            id="glue_doh_completed_outbound",
            glue_job_name=environment+"-glue-doh-completed-outbound",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB
        )

        glue_task_2 = tasks.GlueStartJobRun(
            self,
            id="glue_dohcompleted_sftp_upload",
            glue_job_name=environment+"-glue-dohcompleted-sftp-upload",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB
        )

        glue_task_3 = tasks.GlueStartJobRun(
            self,
            id="glue_doh-classified-outbound",
            glue_job_name=environment+"-glue-doh-classified-outbound",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB
        )

        glue_task_4 = tasks.GlueStartJobRun(
            self,
            id="glue_dohclassified_sftp_upload",
            glue_job_name=environment+"-glue-dohclassified-sftp-upload",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB
        )

        definition = (
            sfn.Parallel(self,id="invoke-all-doh-parallel-jobs")
            .branch(
                    glue_task_1.next(glue_task_2)
            )
            .branch(
                    glue_task_3.next(glue_task_4)
            )
            .next(sfn.Pass(self,"end-doh-parallel-process"))
        )
        
        sfn.StateMachine(self, "doh-outbound-workflow",
            definition=definition,            
            state_machine_name=environment+"-doh-outbound-workflow"
        )
