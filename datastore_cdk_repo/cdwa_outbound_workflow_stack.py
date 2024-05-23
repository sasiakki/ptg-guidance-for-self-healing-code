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
import json
from bin.ec2_utils import EC2Utils


class LambdaLayer(Construct):
    def __init__(self, scope: Construct, id: str):
        super().__init__(scope, id)

        # Create an instance of AccountNumberGetter
        account_number = AccountNumberGetter()

        # Call the get_account_number method
        account_num = account_number.get_account_number()

        # Add layer using an ARN
        arn_layer_arn = (
            f"arn:aws:lambda:us-west-2:{account_num}:layer:bg-ds-python-custom-layer:1"
        )
        arn_layer = _lambda.LayerVersion.from_layer_version_arn(
            self, "eligibility-dependencies", arn_layer_arn
        )
        # Store the layers in a list
        self.layers = [arn_layer]


class CDWAOutboundWorkflowStack(Stack):
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
            extra_python_lib = (
                "s3://b2b-jars/python39-whl/paramiko-3.1.0-py3-none-any.whl"
            )
            
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
            
            extra_python_lib = "s3://seiubg-b2bds-prod-glue-etl-scripts-b0p3e/dependencies/python39-whl/paramiko-3.1.0-py3-none-any.whl"
            
        dependencies_layer = LambdaLayer(self, "eligibility-dependencies")

        # Creating lambda's functions & Glue jobs 
        lambda_cdwa_outbound_email_notification = _lambda.Function(
            self,
            "lambda_cdwa_outbound_email_notification",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset(
                "cdwa-outbound/lambda/lambda-cdwa-outbound-email-notification/"
            ),
            handler="lambda_function.lambda_handler",
            function_name=environment + "-lambda-cdwa-outbound-email-notification",
            role=lambda_role,
            timeout=duration.minutes(2),
            environment={
                "account_number": account_num,
                "environment_type": environment,
            },
        )

        lambda_cdwa_outbound_traineestatus_status = _lambda.Function(
            self,
            "lambda_CDWA_traineestatus_status",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset(
                "cdwa-outbound/lambda/lambda-cdwa-outbound-traineestatus-status/"
            ),
            handler="lambda_function.lambda_handler",
            function_name=environment + "-lambda-cdwa-outbound-traineestatus-status",
            role=lambda_role,
            timeout=duration.minutes(2),
            environment={
                "account_number": account_num,
                "environment_type": environment,
            },            
            vpc=lambda_vpc,
            security_groups=lambda_security_group,
            layers=dependencies_layer.layers,
        )
        
        job = _glue_alpha.Job(
            self,
            "glue-cdwa-outbound-sftp-upload",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V3_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset(
                    "cdwa-outbound/glue/glue-cdwa-outbound-sftp-upload.py"
                ),
            ),
            default_arguments={
                "--account_number": account_num,
                "--additional-python-modules": extra_python_lib,
                "--environment_type": environment,
            },  
            role=glue_role,
            job_name=environment + "-glue-cdwa-outbound-sftp-upload",
            worker_type=_glue_alpha.WorkerType.G_1_X,
            worker_count=2,
        )

        job = _glue_alpha.Job(
            self,
            "glue-cdwa-outbound-trainee-status",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V3_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset(
                    "cdwa-outbound/glue/glue-cdwa-outbound-trainee-status.py"
                ),
            ),
            connections=[glue_connection.get_connection()],
            worker_type=_glue_alpha.WorkerType.G_2_X,
            worker_count=10,
            default_arguments={
                "--account_number": account_num,
                "--environment_type": environment,
            },
            role=glue_role,
            job_name=environment + "-glue-cdwa-outbound-trainee-status",
        )

        # Defining all task for lamba's and glue
        lambda_task_2 = tasks.LambdaInvoke(
            self,
            "lambda-cdwa-outbound-email-notification",
            lambda_function=lambda_cdwa_outbound_email_notification,
            # Lambda's result is in the attribute `Payload`
            payload=sfn.TaskInput.from_object(
                {
                    "filename.$": "$.filename",
                    "filecount.$": "$.filecount",
                    "type": "Outbound",
                }
            ),
        )
        
        lambda_task_1 = tasks.LambdaInvoke(
            self,
            "lambda-cdwa-outbound-traineestatus-status",
            lambda_function=lambda_cdwa_outbound_traineestatus_status,
            # Lambda's result is in the attribute `Payload`
            # output_path="$.Payload",
            payload=sfn.TaskInput.from_object({"type": "Outbound"}),
            result_selector={
                "filename": sfn.JsonPath.string_at("$.Payload.body.filename"),
                "filecount": sfn.JsonPath.string_at("$.Payload.body.filecount"),
            },
        )

        glue_task_2 = tasks.GlueStartJobRun(
            self,
            id="glue-cdwa-sftp-upload",
            glue_job_name=environment + "-glue-cdwa-outbound-sftp-upload",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB,
        )

        glue_task_1 = tasks.GlueStartJobRun(
            self,
            id="glue-cdwa-trainee-status-outbound",
            glue_job_name=environment + "-glue-cdwa-outbound-trainee-status",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB,
        )
        
        endstate = sfn.Pass(self, "end-cdwa-process")
        machine_definition = glue_task_1.next(
            glue_task_2.next(
                sfn.Choice(self, "has-outbound-file-generated")
                .when(
                    sfn.Condition.string_equals(
                        "$.JobName", environment + "-glue-cdwa-outbound-trainee-status"
                    ).and_(sfn.Condition.string_equals("$.JobRunState", "SUCCEEDED")),
                    lambda_task_1.next(lambda_task_2),
                )
                .otherwise(endstate)
            )
        )


        sfn.StateMachine(
            self,
            "cdwa-outbound-workflow",
            definition=machine_definition,
            state_machine_name=environment + "-cdwa-outbound-workflow",
        )

    