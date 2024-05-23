from constructs import Construct
from aws_cdk import (
    Stack,
    aws_stepfunctions as sfn, 
    aws_stepfunctions_tasks as tasks, 
    aws_iam, 
    aws_glue_alpha as _glue_alpha 
)
from bin.get_caller_identity import AccountNumberGetter
from bin.ec2_utils import EC2Utils

class ApiToS3WorkflowStack(Stack):

    def __init__(self,scope: Construct,id: str,environment: str, account_num: str, **kwargs) -> None:
        super().__init__(scope,id,**kwargs)
        

        if environment == 'dev':
                   
            # Get the IAM role by name
            glue_role = aws_iam.Role.from_role_name(
                self,"GlueRole", 
                'glue-poc-s3access-iam-role'
            )
        else:
                       
            # Get the IAM role by name
            glue_role = aws_iam.Role.from_role_name(
                self,"GlueRole", 
                'role-p-glue-data-pipelines'
            )

        # Define the Glue job

        _glue_alpha.Job(self, "glue-qualtrics-api-to-s3",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('api-and-sftp-to-s3-workflow/glue/glue-qualtrics-api-to-s3.py')
            ),
            role=glue_role,
            job_name=environment + '-glue-qualtrics-api-to-s3',
            default_arguments={
                "--account_number": account_num,
                "--environment_type": environment,
            }

        )

        _glue_alpha.Job(self, "glue-qualtrics-os-completion-api-to-s3",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('api-and-sftp-to-s3-workflow/glue/glue-qualtrics-os-completion-api-to-s3.py')
            ),
            role=glue_role,
            job_name=environment + '-glue-qualtrics-os-completion-api-to-s3',
            default_arguments={
                "--account_number": account_num,
                "--environment_type": environment,
            }
        )
        
        glue_qualtrics_api_to_s3_task = tasks.GlueStartJobRun(
            self, 
            id="glue_qualtrics_api_to_s3", 
            glue_job_name=environment + "-glue-qualtrics-api-to-s3",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB
        )

        glue_qualtrics_os_completion_api_to_s3_task = tasks.GlueStartJobRun(
            self, 
            id="glue_qualtrics_os_completion_api_to_s3", 
            glue_job_name=environment + "-glue-qualtrics-os-completion-api-to-s3",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB
        )

       
        api_to_s3_statemachine_definition = (
            sfn.Parallel(self,id="api-to-S3-parallel-jobs")
            .branch(
                glue_qualtrics_api_to_s3_task)
            .branch(
                glue_qualtrics_os_completion_api_to_s3_task)
            )
        
        # Set the definition of the parent state machine
        sfn.StateMachine(self,"api-to-s3-workflow",  
            definition=api_to_s3_statemachine_definition,
            state_machine_name=environment + "-api-to-s3-workflow"    
        )
