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

class ExamWorkflowStack(Stack):

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
        lambda_check_exam = _lambda.Function(
            self, 'lambda-check-exam',
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset('exam-workflow/lambda/lambda-check-exam/'),
            handler='lambda_function.lambda_handler',
            function_name=environment+'-lambda-check-exam',
            role=lambda_role,
            timeout=duration.minutes(2),
            environment={
                    'account_number': account_num,
                    'environment_type': environment
                    }
        )

        job = _glue_alpha.Job(self, "'glue-exam-raw-to-prod",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('exam-workflow/glue/glue-exam-raw-to-prod.py')
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                            "--account_number": account_num,
                            "--environment_type" :environment
            },  
            role=glue_role,
            job_name=environment+'-glue-exam-raw-to-prod'

        )

        job = _glue_alpha.Job(self, "glue-exam-s3-to-raw",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('exam-workflow/glue/glue-exam-s3-to-raw.py')
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                            "--account_number": account_num,
                            "--environment_type" :environment
            },  
            role=glue_role,
            job_name=environment+'-glue-exam-s3-to-raw'

        )

        #Defining all task for lamba's and glue
        lambda_task_1 = tasks.LambdaInvoke(self, "lambda_check_exam",
            lambda_function=lambda_check_exam,
            # Lambda's result is in the attribute `Payload`
            output_path="$.Payload"
        )

        glue_task_2 = tasks.GlueStartJobRun(
            self,
            id="glue_exam_s3_to_raw",
            glue_job_name=environment+"-glue-exam-s3-to-raw",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB
        )

        glue_task_3 = tasks.GlueStartJobRun(
            self,
            id="glue_exam_raw_to_prod",
            glue_job_name=environment+"-glue-exam-raw-to-prod",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB
        )
        end_doh_process=sfn.Pass(self, "end-doh-process")

        machine_definition = lambda_task_1.next(sfn.Choice(self,"has-files")
                    .when(
                        sfn.Condition.boolean_equals("$.result", True),
                        glue_task_2.next(glue_task_3)
                    )
                    .otherwise(end_doh_process))
        
        sfn.StateMachine(self, "exam-workflow", 
            definition=machine_definition,
            state_machine_name=environment+"-exam-workflow"
        )
