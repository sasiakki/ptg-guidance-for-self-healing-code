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

class DshsOutboundWorkflowStack(Stack):

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
        
        extra_python_lib= "s3://seiu-b2bds-glue-dependencies/paramiko-3.1.0-py3-none-any.whl"
        cryptography_pythonlib = "s3://seiu-b2bds-glue-dependencies/cffi-1.15.0-cp37-cp37m-manylinux_2_12_x86_64.manylinux2010_x86_64.whl,s3://seiu-b2bds-glue-dependencies/fernet-1.0.1.zip,s3://seiu-b2bds-glue-dependencies/cryptography-36.0.2-cp36-abi3-manylinux_2_24_x86_64.whl,s3://seiu-b2bds-glue-dependencies/pycparser-2.21-py2.py3-none-any.whl,s3://seiu-b2bds-glue-dependencies/pyaes-1.6.1.tar.gz"
        # Creating Glue jobs 
        job = _glue_alpha.Job(self, "glue-apssn-decrypt-outbound",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V3_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('dshs-outbound-workflow/glue/glue-apssn-decrypt-outbound.py')
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                "--account_number": account_num,
                "--additional-python-modules": cryptography_pythonlib,
                "--environment_type": environment
            },  
            role=glue_role,
            job_name=environment+'-glue-apssn-decrypt-outbound'

        )

        job = _glue_alpha.Job(self, "glue-apssn-sftp-upload",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V3_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('dshs-outbound-workflow/glue/glue-apssn-sftp-upload.py')
            ),
            default_arguments={
                "--account_number": account_num,
                "--additional-python-modules": extra_python_lib,
                "--environment_type": environment
            },  
            role=glue_role,
            job_name=environment+'-glue-apssn-sftp-upload',
            worker_type=_glue_alpha.WorkerType.G_1_X,
            worker_count=2

        )

        job = _glue_alpha.Job(self, "glue-dshsprovider-outbound",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V3_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('dshs-outbound-workflow/glue/glue-dshsprovider-outbound.py')
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                "--account_number": account_num,
                "--environment_type": environment
            },  
            role=glue_role,
            job_name=environment+'-glue-dshsprovider-outbound'

        )

        job = _glue_alpha.Job(self, "glue-dshsprovider-sftp-upload",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V3_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('dshs-outbound-workflow/glue/glue-dshsprovider-sftp-upload.py')
            ),
            default_arguments={
                "--account_number": account_num,
                "--additional-python-modules": extra_python_lib,
                "--environment_type": environment
            },  
            role=glue_role,
            job_name=environment+'-glue-dshsprovider-sftp-upload',
            worker_type=_glue_alpha.WorkerType.G_1_X,
            worker_count=2

        )

        #Defining all task for glue

        glue_task_1 = tasks.GlueStartJobRun(
            self,
            id="glue_dshsprovider_outbound",
            glue_job_name=environment+"-glue-dshsprovider-outbound",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB
        )

        glue_task_2 = tasks.GlueStartJobRun(
            self,
            id="glue_dshsprovider_sftp_upload",
            glue_job_name=environment+"-glue-dshsprovider-sftp-upload",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB
        )

        glue_task_3 = tasks.GlueStartJobRun(
            self,
            id="glue_apssn_decrypt_outbound",
            glue_job_name=environment+"-glue-apssn-decrypt-outbound",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB
        )

        glue_task_4 = tasks.GlueStartJobRun(
            self,
            id="glue_apssn_sftp_upload",
            glue_job_name=environment+"-glue-apssn-sftp-upload",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB
        )

        definition = (
            sfn.Parallel(self,id="invoke-all-dshs-parallel-jobs")
            .branch(
                    glue_task_1.next(glue_task_2)
            )
            .branch(
                    glue_task_3.next(glue_task_4)
            )
            .next(sfn.Pass(self,"end-dshs-parallel-process"))
        )
        
        sfn.StateMachine(self, "dshs_outbound_workflow_stack",
            definition=definition,            
            state_machine_name=environment+"-dshs_outbound_workflow_stack"
        )
