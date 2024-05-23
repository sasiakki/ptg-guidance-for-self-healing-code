from constructs import Construct
from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_glue as _glue,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as tasks,
    aws_iam,
    aws_glue_alpha as _glue_alpha,
    aws_stepfunctions as stepfunctions,
    Duration as duration,
)

from .glue_connection import GlueConnection
from bin.get_caller_identity import AccountNumberGetter


class BenefitsContinuationStack(Stack):
    def __init__(
        self, scope: Construct, id: str, environment: str, account_num: str, **kwargs
    ) -> None:
        super().__init__(scope, id, **kwargs)

        # Get the IAM role by name
        lambda_role = aws_iam.Role.from_role_name(
            self, "LambdaRole", "role-d-lambda-execute"
        )
        glue_role = aws_iam.Role.from_role_name(
            self, "GlueRole", "role-p-glue-data-pipelines"
        )

        if environment == "dev":
            glue_connection = GlueConnection(self, "glue_connection", "rdsconnect")
        else:
            glue_connection = GlueConnection(
                self, "glue_connection", "connection-uw2-p-seiubg-prod-b2bds"
            )

        # Defines an AWS Lambda resource
        lambda_check_benefitscontinuation = _lambda.Function(
            self,
            "lambda-check-benefitscontinuation",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset(
                "benefits_continuation/lambda/lambda_check_benefitscontinuation/"
            ),
            handler="lambda_function.lambda_handler",
            function_name=environment + "-lambda_check_benefitscontinuation",
            role=lambda_role,
            timeout=duration.minutes(1),
            environment={
                "account_number": account_num,
                "environment_type": environment,
            },
        )
        # Defines an AWS glue job resource
        job = _glue_alpha.Job(
            self,
            "glue-benefitscontinuation-s3-raw",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset(
                    "benefits_continuation/glue/glue-benefitscontinuation-s3-raw.py"
                ),
            ),
            connections=[glue_connection.get_connection()],
            default_arguments={
                "--account_number": account_num,
                "--environment_type": environment,
            },
            role=glue_role,
            job_name=environment + "-glue-benefitscontinuation-s3-raw",
        )

        job = _glue_alpha.Job(
            self,
            "glue-benefitscontinuation-raw-staging",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset(
                    "benefits_continuation/glue/glue-benefitscontinuation-raw-staging.py"
                ),
            ),
            connections=[glue_connection.get_connection()],
            default_arguments={
                "--account_number": account_num,
                "--environment_type": environment,
            },
            role=glue_role,
            job_name=environment + "-glue-benefitscontinuation-raw-staging",
        )

        job = _glue_alpha.Job(
            self,
            "glue-update-trainingrequirement-benefitscontinuation",
            executable=_glue_alpha.JobExecutable.python_shell(
                glue_version=_glue_alpha.GlueVersion.V1_0,
                python_version=_glue_alpha.PythonVersion.THREE_NINE,
                script=_glue_alpha.Code.from_asset(
                    "benefits_continuation/glue/glue-update-trainingrequirement-benefitscontinuation.py"
                ),
            ),
            connections=[glue_connection.get_connection()],
            default_arguments={
                "--account_number": account_num,
                "--environment_type": environment,
            },
            role=glue_role,
            job_name=environment
            + "-glue-update-trainingrequirement-benefitscontinuation",
        )

        # Defines tasks for lambda and glue jobs
        lambda_task_1 = tasks.LambdaInvoke(
            self,
            "lambda_check_benefitscontinuation",
            lambda_function=lambda_check_benefitscontinuation,
            # Lambda's result is in the attribute `Payload`
            output_path="$.Payload",
        )

        glue_task1 = tasks.GlueStartJobRun(
            self,
            id="glue_ip_benefitscontinuation_s3_raw",
            glue_job_name=environment + "-glue-benefitscontinuation-s3-raw",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB,
        )

        glue_task2 = tasks.GlueStartJobRun(
            self,
            id="glue_benefitscontinuation_raw_staging",
            glue_job_name=environment + "-glue-benefitscontinuation-raw-staging",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB,
        )

        glue_task3 = tasks.GlueStartJobRun(
            self,
            id="glue_update_trainingrequirement_benefitscontinuation",
            glue_job_name=environment
            + "-glue-update-trainingrequirement-benefitscontinuation",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB,
        )

        machine_definition = lambda_task_1.next(
            sfn.Choice(self, "has-files")
            .when(
                sfn.Condition.boolean_equals("$.result", True),
                glue_task1.next(glue_task2.next(glue_task3)),
            )
            .otherwise(sfn.Pass(self, "end-benefits-continuation-process"))
        )

        # define state machine
        sfn.StateMachine(
            self,
            "StateMachine_benefits_continuation",
            definition=machine_definition,
            state_machine_name=environment + "-benefits-continuation-workflow",
        )
