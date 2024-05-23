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

class QualtricsWorkflowStack(Stack):

    def __init__(self,scope: Construct,id: str, environment: str, account_num: str, **kwargs) -> None:
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


        # Creating lambda's functions & Glue jobs 
        lambda_check_qualtrics = _lambda.Function(
            self,'lambda_check_qualtrics', 
            runtime=_lambda.Runtime.PYTHON_3_9, 
            code=_lambda.Code.from_asset('qualtrics-workflow/lambda/lambda-check-qualtrics'), 
            handler='lambda_function.lambda_handler', 
            function_name=environment+'-lambda-check-qualtrics', 
            role=lambda_role,
            timeout=duration.minutes(5),
            environment={
                    'account_number': account_num,
                    'environment_type': environment
                    }
        )

        job = _glue_alpha.Job(self, "glue-qualtrics-s3-to-raw",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('qualtrics-workflow/glue/glue-qualtrics-s3-to-raw.py')
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                            "--account_number": account_num,
                            "--environment_type": environment
            },  
            role=glue_role,
            job_name=environment+'-glue-qualtrics-s3-to-raw'
        )


        job = _glue_alpha.Job(self, "glue-qualtrics-cleandata",
            executable=_glue_alpha.JobExecutable.python_shell(
                glue_version=_glue_alpha.GlueVersion.V1_0,
                python_version=_glue_alpha.PythonVersion.THREE_NINE,
                script=_glue_alpha.Code.from_asset('qualtrics-workflow/glue/glue-qualtrics-cleandata.py')
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                            "--account_number": account_num,
                            "--environment_type": environment
            },  
            role=glue_role,
            job_name=environment+'-glue-qualtrics-cleandata'

        )


        job = _glue_alpha.Job(self, "glue-qualtrics-raw-to-person-history",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('qualtrics-workflow/glue/glue-qualtrics-raw-to-person-history.py')
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                            "--account_number": account_num,
                            "--environment_type": environment
            },  
            role=glue_role,
            job_name=environment+'-glue-qualtrics-raw-to-person-history'

        )
        

        job = _glue_alpha.Job(self, "glue-qualtrics-raw-to-employmentrelationshiphistory",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('qualtrics-workflow/glue/glue-qualtrics-raw-to-employmentrelationshiphistory.py')
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                            "--account_number": account_num,
                            "--environment_type": environment
            },  
            role=glue_role,
            job_name=environment+'-glue-qualtrics-raw-to-employmentrelationshiphistory'

        )


        job = _glue_alpha.Job(self, "glue-ap-to-employmentrelationship",
            executable=_glue_alpha.JobExecutable.python_shell(
                glue_version=_glue_alpha.GlueVersion.V1_0,
                python_version=_glue_alpha.PythonVersion.THREE_NINE,
                script=_glue_alpha.Code.from_asset('qualtrics-workflow/glue/glue-ap-to-employmentrelationship.py')
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                            "--account_number": account_num,
                            "--environment_type": environment
            },  
            role=glue_role,
            job_name=environment+'-glue-ap-to-employmentrelationship'

        )



        #Defining all task for lamba's and glue
        lambda_task_1 = tasks.LambdaInvoke(self,"lambda-check-qualtrics", 
            lambda_function=lambda_check_qualtrics, 
            # Lambda's result is in the attribute `Payload`
            result_path="$.Payload"
        )

        glue_task_2 = tasks.GlueStartJobRun(
            self, 
            id="glue_qualtrics_s3_to_raw", 
            glue_job_name=environment+"-glue-qualtrics-s3-to-raw", 
            integration_pattern=sfn.IntegrationPattern.RUN_JOB
        )
        
        glue_task_3 = tasks.GlueStartJobRun(
            self, 
            id="glue_qualtrics_cleandata", 
            glue_job_name=environment+"-glue-qualtrics-cleandata", 
            integration_pattern=sfn.IntegrationPattern.RUN_JOB
        )

        glue_task_4 = tasks.GlueStartJobRun(
            self, 
            id="glue_qualtrics_raw_to_person_history", 
            glue_job_name=environment+"-glue-qualtrics-raw-to-person-history", 
            integration_pattern=sfn.IntegrationPattern.RUN_JOB
        )

        glue_task_5 = tasks.GlueStartJobRun(
            self, 
            id="glue_qualtrics_raw_to_employmentrelationshiphistory", 
            glue_job_name=environment+"-glue-qualtrics-raw-to-employmentrelationshiphistory", 
            integration_pattern=sfn.IntegrationPattern.RUN_JOB
        )

        glue_task_6 = tasks.GlueStartJobRun(
            self, 
            id="glue_ap_to_employmentrelationship", 
            glue_job_name=environment+"-glue-ap-to-employmentrelationship", 
            integration_pattern=sfn.IntegrationPattern.RUN_JOB
        )

        
        machine_definition = lambda_task_1.next(sfn.Choice(self, "has-files")
            .when(
                sfn.Condition.boolean_equals("$.Payload.Payload.result",True), 
                glue_task_2.next(glue_task_3.next(glue_task_4.next(glue_task_5.next(glue_task_6))))
            )
            .otherwise(sfn.Pass(self,"end-qualtrics-process")))
        
        sfn.StateMachine(self,"qualtrics-workflow", 
            definition=machine_definition,
            state_machine_name=environment+"-qualtrics-workflow"
        )
