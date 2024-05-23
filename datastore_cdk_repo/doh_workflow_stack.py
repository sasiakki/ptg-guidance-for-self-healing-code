from constructs import Construct
from aws_cdk import (
    Stack, 
    aws_lambda as _lambda, 
    aws_glue as _glue, 
    aws_stepfunctions as sfn, 
    aws_stepfunctions_tasks as tasks, 
    Duration, 
    aws_iam,
    aws_glue_alpha as _glue_alpha,
    Duration as duration,
    aws_stepfunctions as stepfunctions
)
from .glue_connection import GlueConnection
from bin.get_caller_identity import AccountNumberGetter


class DOHWorkflowStack(Stack):
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
        lambda_check_doh = _lambda.Function(
            self, 
            "lambda_check_doh", 
            runtime=_lambda.Runtime.PYTHON_3_9, 
            code=_lambda.Code.from_asset("doh-workflow/lambda/lambda-check-doh"), 
            handler="lambda_function.lambda_handler", 
            function_name=environment+"-lambda-check-doh", 
            role=lambda_role,
            timeout=duration.minutes(5),
            environment={
                    'account_number': account_num,
                    'environment_type': environment}
        )

        lambda_check_doh_classified = _lambda.Function(
            self, 
            "lambda_check_doh_classified", 
            runtime=_lambda.Runtime.PYTHON_3_9, 
            code=_lambda.Code.from_asset("doh-workflow/lambda/lambda-check-doh-classified"), 
            handler="lambda_function.lambda_handler", 
            function_name=environment+"-lambda-check-doh-classified", 
            role=lambda_role,
            timeout=duration.minutes(5),
            environment={
                    'account_number': account_num,
                    'environment_type':environment}
        )


        job = _glue_alpha.Job(self, "glue-doh-classified-raw-to-prod",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('doh-workflow/glue/glue-doh-classified-raw-to-prod.py')
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                            "--account_number": account_num,
                            "--environment_type":environment
            },  
            role=glue_role,
            job_name=environment+'-glue-doh-classified-raw-to-prod'

        )

        job = _glue_alpha.Job(self, "glue-doh-classified-s3-to-raw",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('doh-workflow/glue/glue-doh-classified-s3-to-raw.py')
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                            "--account_number": account_num,
                            "--environment_type":environment
            },  
            role=glue_role,
            job_name=environment+'-glue-doh-classified-s3-to-raw'

        )

        job = _glue_alpha.Job(self, "glue-doh-clean-data",
            executable=_glue_alpha.JobExecutable.python_shell(
                glue_version=_glue_alpha.GlueVersion.V1_0,
                python_version=_glue_alpha.PythonVersion.THREE_NINE,
                script=_glue_alpha.Code.from_asset('doh-workflow/glue/glue-doh-clean-data.py')
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                            "--account_number": account_num,
                            "--environment_type":environment
            },  
            role=glue_role,
            job_name=environment+'-glue-doh-clean-data'

        )

        job = _glue_alpha.Job(self, "glue-doh-completed-raw-to-prod",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('doh-workflow/glue/glue-doh-completed-raw-to-prod.py')
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                            "--account_number": account_num,
                            "--environment_type":environment
            },  
            role=glue_role,
            job_name=environment+'-glue-doh-completed-raw-to-prod'

        )

        job = _glue_alpha.Job(self, "glue-doh-completed-s3-to-raw",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('doh-workflow/glue/glue-doh-completed-s3-to-raw.py')
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                            "--account_number": account_num,
                            "--environment_type":environment
            },  
            role=glue_role,
            job_name=environment+'-glue-doh-completed-s3-to-raw'

        )


        # Defining all task for lamba's and glue
        lambda_task_1 = tasks.LambdaInvoke(
            self, 
            "lambda-check-doh", 
            lambda_function=lambda_check_doh, 
            # Lambda's result is in the attribute `Payload`
            result_path="$.lambda_handler"
        )

        lambda_task_2 = tasks.LambdaInvoke(
            self, 
            "lambda-check-doh-classified", 
            lambda_function=lambda_check_doh_classified, 
            # Lambda's result is in the attribute `Payload`
            result_path="$.lambda_handler"
        )

        glue_task_2 = tasks.GlueStartJobRun(
            self, 
            id="glue_doh_classified_raw_to_prod", 
            glue_job_name=environment+"-glue-doh-classified-raw-to-prod",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB
        )

        glue_task_1 = tasks.GlueStartJobRun(
            self, 
            id="glue_doh_classified_s3_to_raw", 
            glue_job_name=environment+"-glue-doh-classified-s3-to-raw",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB 
        )

        glue_task_4 = tasks.GlueStartJobRun(
            self, 
            id="glue_doh_clean_data", 
            glue_job_name=environment+"-glue-doh-clean-data",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB  
        )

        glue_task_5 = tasks.GlueStartJobRun(
            self, 
            id="glue_doh_completed_raw_to_prod", 
            glue_job_name=environment+"-glue-doh-completed-raw-to-prod",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB 
        )

        glue_task_3 = tasks.GlueStartJobRun(
            self, 
            id="glue_doh_completed_s3_to_raw", 
            glue_job_name=environment+"-glue-doh-completed-s3-to-raw",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB  
        )

        wait_task = sfn.Wait(
                    self,"Wait 120 Sec", 
                        time=sfn.WaitTime.timestamp_path(
                            "$$.Execution.StartTime + 120"
                        )
                    )
                    
        wait_job = sfn.Wait(
            self,"Wait 120 Seconds", 
            time=sfn.WaitTime.duration(
                Duration.seconds(120))
        )


        definition = (
            sfn.Parallel(self,id="invoke-all-doh-parallel-jobs")
            .branch(
                lambda_task_1.next(
                    sfn.Choice(self,"has-doh-completed-files").when(
                        sfn.Condition.boolean_equals("$.lambda_handler.Payload.result",True), 
                        glue_task_3.next(wait_job).next(glue_task_5)
                    )
                    .otherwise(
                        sfn.Pass(self,"end-doh-completed")), 
                    )
            )
            .branch(
                lambda_task_2.next(
                    sfn.Choice(self,"has-doh-classified-files")
                    .when(
                        sfn.Condition.boolean_equals("$.lambda_handler.Payload.result",True), 
                        glue_task_1.next(glue_task_4.next(glue_task_2)), 
                    )
                    .otherwise(sfn.Pass(self,"end-doh-classified-process"))
                )
            )
            .next(sfn.Pass(self,"end-doh-parallel-process"))
        )

        sfn.StateMachine(
            self, 
            "doh-workflow", 
            definition=definition,            
            state_machine_name=environment+"-doh-workflow", 
        )
