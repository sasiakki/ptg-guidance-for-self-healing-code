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
    aws_ec2,
    aws_stepfunctions as stepfunctions,
)
from .glue_connection import GlueConnection
from bin.get_caller_identity import AccountNumberGetter
from bin.ec2_utils import EC2Utils


class CDWAWorkflowStack(Stack):
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

        ec2_utils = EC2Utils("us-west-2", account_num)
        (
            vpc_id_from_boto,
            subnet_ids,
            route_table_ids,
            sg_group_id,
            sg_group_name,
        ) = ec2_utils.get_vpc_subnets_and_security_group(environment)

        if environment == "dev":
            lambda_vpc = None
            lambda_security_group = None
            glue_connection = GlueConnection(self, "glue_connection", "rdsconnect")

        else:
            lambda_vpc = aws_ec2.Vpc.from_vpc_attributes(
                self,
                "lambda_vpc",
                vpc_id=vpc_id_from_boto,
                region="us-west-2",
                availability_zones=[
                    "us-west-2a",
                    "us-west-2b",
                    "us-west-2c",
                    "us-west-2d",
                ],
                private_subnet_ids=subnet_ids,
                private_subnet_route_table_ids=route_table_ids,
            )
            lambda_security_group_object = aws_ec2.SecurityGroup.from_security_group_id(
                self, sg_group_name, sg_group_id
            )
            lambda_security_group = [lambda_security_group_object]

            glue_connection = GlueConnection(
                self, "glue_connection", "connection-uw2-p-seiubg-prod-b2bds"
            )

        cryptography_pythonlib = "s3://seiu-b2bds-glue-dependencies/cffi-1.15.0-cp37-cp37m-manylinux_2_12_x86_64.manylinux2010_x86_64.whl,s3://seiu-b2bds-glue-dependencies/fernet-1.0.1.zip,s3://seiu-b2bds-glue-dependencies/cryptography-36.0.2-cp36-abi3-manylinux_2_24_x86_64.whl,s3://seiu-b2bds-glue-dependencies/pycparser-2.21-py2.py3-none-any.whl,s3://seiu-b2bds-glue-dependencies/pyaes-1.6.1.tar.gz"
        layer_arn = "arn:aws:lambda:us-west-2:345057560386:layer:AWS-Parameters-and-Secrets-Lambda-Extension:4"
        AWS_Parameters_and_Secrets_layer = _lambda.LayerVersion.from_layer_version_arn(
            scope=self,
            id="AWS-Parameters-and-Secrets-Lambda-Extension",
            layer_version_arn=layer_arn,
        )

        custom_layer = _lambda.LayerVersion(
            scope=self,
            id="custom-layer",
            code=_lambda.AssetCode("lambda_layer/custom-layer/"),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_9],
        )

        # Creating lambda's functions & Glue jobs
        lambda_s3_check_cdwa = _lambda.Function(
            self,
            "lambda-s3-check-cdwa",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("cdwa-workflow/lambda/lambda-s3-check-cdwa/"),
            handler="lambda_function.lambda_handler",
            function_name=environment + "-lambda_s3_check_cdwa",
            role=lambda_role,
            timeout=duration.minutes(2),
            environment={
                "account_number": account_num,
                "environment_type": environment,
            },
        )

        lambda_get_cdwa_file_processing = _lambda.Function(
            self,
            "lambda-get-cdwa-file-processing",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset(
                "cdwa-workflow/lambda/lambda-get-cdwa-file-processing/"
            ),
            handler="lambda_function.lambda_handler",
            function_name=environment + "-lambda_get_cdwa_file_processing",
            role=lambda_role,
            timeout=duration.minutes(2),
            environment={
                "account_number": account_num,
                "environment_type": environment,
            },
            vpc=lambda_vpc,
            security_groups=lambda_security_group,
            layers=[custom_layer, AWS_Parameters_and_Secrets_layer],
        )

        lambda_get_cdwa_email_notification = _lambda.Function(
            self,
            "lambda-get-cdwa-email-notification",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset(
                "cdwa-workflow/lambda/lambda-get-cdwa-email-notification/"
            ),
            handler="lambda_function.lambda_handler",
            function_name=environment + "-lambda_get_cdwa_email_notification",
            role=lambda_role,
            timeout=duration.minutes(2),
            environment={
                "account_number": account_num,
                "environment_type": environment,
            },
            layers=[custom_layer, AWS_Parameters_and_Secrets_layer],
        )

        job = _glue_alpha.Job(
            self,
            "glue-cdwa-s3-to-raw",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V3_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset(
                    "cdwa-workflow/glue/glue-cdwa-s3-to-raw.py"
                ),
            ),
            connections=[glue_connection.get_connection()],
            default_arguments={
                "--account_number": account_num,
                "--additional-python-modules": cryptography_pythonlib,
                "--environment_type": environment,
            },
            role=glue_role,
            job_name=environment + "-glue-cdwa-s3-to-raw",
        )

        job = _glue_alpha.Job(
            self,
            "glue-cdwa-providerinfo-notification1",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset(
                    "cdwa-workflow/glue/glue-cdwa-providerinfo-notification.py"
                ),
            ),
            connections=[glue_connection.get_connection()],
            default_arguments={
                "--account_number": account_num,
                "--environment_type": environment,
            },
            role=glue_role,
            job_name=environment + "-glue-cdwa-providerinfo-notification1",
        )

        job = _glue_alpha.Job(
            self,
            "glue-cdwa-validation",
            executable=_glue_alpha.JobExecutable.python_shell(
                glue_version=_glue_alpha.GlueVersion.V1_0,
                python_version=_glue_alpha.PythonVersion.THREE_NINE,
                script=_glue_alpha.Code.from_asset(
                    "cdwa-workflow/glue/glue-cdwavalidation.py"
                ),
            ),
            connections=[glue_connection.get_connection()],
            default_arguments={
                "--account_number": account_num,
                "--environment_type": environment,
            },
            role=glue_role,
            job_name=environment + "-glue-cdwa-validation",
        )

        job = _glue_alpha.Job(
            self,
            "glue-cdwa-error-to-s3",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset(
                    "cdwa-workflow/glue/glue-cdwa-error-to-s3.py"
                ),
            ),
            connections=[glue_connection.get_connection()],
            default_arguments={
                "--account_number": account_num,
                "--environment_type": environment,
            },
            role=glue_role,
            job_name=environment + "-glue-cdwa-error-to-s3",
        )

        ##########
        # pipeline_p_cdwa_providerinfo_notification
        job = _glue_alpha.Job(
            self,
            "glue-cdwa-providerinfo-notification2",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset(
                    "cdwa-workflow/glue/glue-cdwa-providerinfo-notification.py"
                ),
            ),
            connections=[glue_connection.get_connection()],
            default_arguments={
                "--account_number": account_num,
                "--environment_type": environment,
            },
            role=glue_role,
            job_name=environment + "-glue-cdwa-providerinfo-notification2",
        )
        ##########

        job = _glue_alpha.Job(
            self,
            "glue-cdwa-raw-to-staging-personhistory",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset(
                    "cdwa-workflow/glue/glue-cdwa-raw-to-staging-person-history.py"
                ),
            ),
            connections=[glue_connection.get_connection()],
            default_arguments={
                "--account_number": account_num,
                "--environment_type": environment,
            },
            role=glue_role,
            job_name=environment + "-glue-cdwa-raw-to-staging-personhistory",
        )

        job = _glue_alpha.Job(
            self,
            "glue-cdwa-raw-to-staging-employementrelationshiphistory",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset(
                    "cdwa-workflow/glue/glue-cdwa-raw-to-staging-employementrelationshiphistory.py"
                ),
            ),
            connections=[glue_connection.get_connection()],
            default_arguments={
                "--account_number": account_num,
                "--environment_type": environment,
            },
            role=glue_role,
            job_name=environment
            + "-glue-cdwa-raw-to-staging-employementrelationshiphistory",
        )

        job = _glue_alpha.Job(
            self,
            "glue-cdwa-employmentrelationship",
            executable=_glue_alpha.JobExecutable.python_shell(
                glue_version=_glue_alpha.GlueVersion.V1_0,
                python_version=_glue_alpha.PythonVersion.THREE_NINE,
                script=_glue_alpha.Code.from_asset(
                    "cdwa-workflow/glue/glue-cdwa-providerinfo-employmentrelationship-process.py"
                ),
            ),
            connections=[glue_connection.get_connection()],
            default_arguments={
                "--account_number": account_num,
                "--environment_type": environment,
            },
            role=glue_role,
            job_name=environment + "-glue-cdwa-employmentrelationship",
        )

        # Defining all task for lamba's and glue
        lambda_task_1 = tasks.LambdaInvoke(
            self,
            "lambda_s3_check_cdwa",
            lambda_function=lambda_s3_check_cdwa,
        )

        lambda_task_2 = tasks.LambdaInvoke(
            self,
            "lambda_get_cdwa_file_processing",
            lambda_function=lambda_get_cdwa_file_processing,
            payload=sfn.TaskInput.from_object({"type": "Processing"}),
            result_selector={
                "filename": sfn.JsonPath.string_at("$.Payload.body.filename"),
                "filecount": sfn.JsonPath.string_at("$.Payload.body.filecount"),
            },
        )

        lambda_task_3 = tasks.LambdaInvoke(
            self,
            "lambda_get_cdwa_email_notification",
            lambda_function=lambda_get_cdwa_email_notification,
            payload=sfn.TaskInput.from_object(
                {
                    "filename.$": "$.filename",
                    "filecount.$": "$.filecount",
                    "type": "Processing",
                }
            ),
        )

        lambda_task_4 = tasks.LambdaInvoke(
            self,
            "lambda_get_cdwa_file_processing1",
            lambda_function=lambda_get_cdwa_file_processing,
            payload=sfn.TaskInput.from_object({"type": "Datavalidation"}),
            result_selector={
                "filename": sfn.JsonPath.string_at("$.Payload.body.filename"),
                "filecount": sfn.JsonPath.string_at("$.Payload.body.filecount"),
            },
        )

        lambda_task_5 = tasks.LambdaInvoke(
            self,
            "lambda_get_cdwa_email_notification1",
            lambda_function=lambda_get_cdwa_email_notification,
            payload=sfn.TaskInput.from_object(
                {
                    "filename.$": "$.filename",
                    "filecount.$": "$.filecount",
                    "type": "Datavalidation",
                }
            ),
        )

        glue_task_3 = tasks.GlueStartJobRun(
            self,
            id="glue_cdwa_s3_to_raw",
            glue_job_name=environment + "-glue-cdwa-s3-to-raw",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB,
        )

        glue_task_4 = tasks.GlueStartJobRun(
            self,
            id="glue_cdwa_validation",
            glue_job_name=environment + "-glue-cdwa-validation",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB,
        )

        glue_task_5 = tasks.GlueStartJobRun(
            self,
            id="glue_cdwa_error_to_s3",
            glue_job_name=environment + "-glue-cdwa-error-to-s3",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB,
        )

        glue_task_6 = tasks.GlueStartJobRun(
            self,
            id="glue_cdwa_raw_to_staging_personhistory",
            glue_job_name=environment + "-glue-cdwa-raw-to-staging-personhistory",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB,
        )

        glue_task_7 = tasks.GlueStartJobRun(
            self,
            id="glue_cdwa_raw_to_staging_employementrelationshiphistory",
            glue_job_name=environment
            + "-glue-cdwa-raw-to-staging-employementrelationshiphistory",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB,
        )

        glue_task_8 = tasks.GlueStartJobRun(
            self,
            id="glue_cdwa_employmentrelationship",
            glue_job_name=environment + "-glue-cdwa-employmentrelationship",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB,
        )

        definition1 = glue_task_3.next(
            (
                sfn.Choice(self, "has-file-loaded")
                .when(
                    sfn.Condition.string_equals(
                        "$.JobName", environment + "-glue-cdwa-s3-to-raw"
                    ).and_(sfn.Condition.string_equals("$.JobRunState", "SUCCEEDED")),
                    lambda_task_2.next(lambda_task_3.next(glue_task_4)),
                )
                .otherwise(glue_task_4)
                .afterwards()
            )
        )

        definition2 = (
            sfn.Choice(self, "has-validation-completed")
            .when(
                sfn.Condition.string_equals(
                    "$.JobName", environment + "-glue-cdwa-validation"
                ).and_(sfn.Condition.string_equals("$.JobRunState", "SUCCEEDED")),
                lambda_task_4.next(lambda_task_5.next(glue_task_5)),
            )
            .otherwise(glue_task_5)
            .afterwards()
        )

        endstate = sfn.Pass(self, "end-cdwa-process")

        machine_definition = lambda_task_1.next(
            sfn.Choice(self, "has-files")
            .when(
                sfn.Condition.boolean_equals("$.Payload.result", True),
                definition1.next(definition2).next(
                    glue_task_6.next(glue_task_7.next(glue_task_8))
                ),
            )
            .otherwise(endstate)
        )

        sfn.StateMachine(
            self,
            "cdwa-workflow",
            definition=machine_definition,
            state_machine_name=environment + "-cdwa-workflow",
        )
