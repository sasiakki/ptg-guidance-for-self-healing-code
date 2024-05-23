from constructs import Construct
from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as tasks,
    aws_iam,
    aws_glue_alpha as _glue_alpha,
    Duration as duration,
    aws_ec2,
)
from .glue_connection import GlueConnection
from bin.get_caller_identity import AccountNumberGetter
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
            f"arn:aws:lambda:us-west-2:{account_num}:layer:eligibility-dependencies:1"
        )
        arn_layer = _lambda.LayerVersion.from_layer_version_arn(
            self, "eligibility-dependencies", arn_layer_arn
        )
        # Store the layers in a list
        self.layers = [arn_layer]


class EligibilityCalculationWorkflowStack(Stack):
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

        eligibility_dependencies_layer = LambdaLayer(self, "eligibility-dependencies")

        job = _glue_alpha.Job(
            self,
            "glue-eligibility-data-truncate",
            executable=_glue_alpha.JobExecutable.python_shell(
                glue_version=_glue_alpha.GlueVersion.V1_0,
                python_version=_glue_alpha.PythonVersion.THREE_NINE,
                script=_glue_alpha.Code.from_asset(
                    "eligibility-calculation-workflow/glue/glue-eligibility-data-truncate.py"
                ),
            ),
            role=glue_role,
            connections=[glue_connection.get_connection()],
            default_arguments={
                "--account_number": account_num,
                "--environment_type": environment,
            },
            job_name=environment + "-glue-eligibility-data-truncate",
        )

        job = _glue_alpha.Job(
            self,
            "glue-eligibility-data-inbound",
            executable=_glue_alpha.JobExecutable.python_shell(
                glue_version=_glue_alpha.GlueVersion.V1_0,
                python_version=_glue_alpha.PythonVersion.THREE_NINE,
                script=_glue_alpha.Code.from_asset(
                    "eligibility-calculation-workflow/glue/glue-eligibility-data-inbound.py"
                ),
            ),
            role=glue_role,
            connections=[glue_connection.get_connection()],
            default_arguments={
                "--account_number": account_num,
                "--environment_type": environment,
            },
            job_name=environment + "-glue-eligibility-data-inbound",
        )

        lambda_eligibility_compliance_iterator = _lambda.Function(
            self,
            "lambda-eligibility-compliance-iterator",
            runtime=_lambda.Runtime.NODEJS_14_X,
            code=_lambda.Code.from_asset(
                "eligibility-calculation-workflow/lambda/lambda_eligibility_compliance_iterator/"
            ),
            handler="index.processingMain",
            role=lambda_role,
            layers=eligibility_dependencies_layer.layers,
            timeout=duration.minutes(15),
            environment={
                "account_number": account_num,
                "environment_type": environment,
            },
            vpc=lambda_vpc,
            security_groups=lambda_security_group,
            function_name=environment + "-lambda_eligibility_compliance_iterator",
        )

        lambda_calculate_eligibility = _lambda.Function(
            self,
            "EligibilityFunction",
            runtime=_lambda.Runtime.NODEJS_14_X,
            # code=_lambda.S3Code(bucket=existing_bucket,key='eligibility-sam-build.zip/'),
            code=_lambda.Code.from_asset(
                "eligibility-cdk-sam-workflow/eligibility-ms-dev/.aws-sam/build/EligibilityFunction"
            ),
            handler="index.processingMain",
            role=lambda_role,
            layers=eligibility_dependencies_layer.layers,
            timeout=duration.minutes(15),
            environment={
                "account_number": account_num,
                "environment_type": environment,
            },
            vpc=lambda_vpc,
            security_groups=lambda_security_group,
            function_name=environment + "-lambda_calculate_eligibility",
        )

        glue_task1 = tasks.GlueStartJobRun(
            self,
            id="glue_eligibility_data_truncate",
            glue_job_name=environment + "-glue-eligibility-data-truncate",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB,
        )

        glue_task2 = tasks.GlueStartJobRun(
            self,
            id="glue_eligibility_data_inbound",
            glue_job_name=environment + "-glue-eligibility-data-inbound",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB,
        )

        lambda_task_1 = tasks.LambdaInvoke(
            self,
            "lambda_calculate_eligibility",
            lambda_function=lambda_calculate_eligibility,
            # Lambda's result is in the attribute `Payload`
            # output_path="$.Payload"
            result_path="$.result",
        )

        lambda_task_2 = tasks.LambdaInvoke(
            self,
            "lambda_eligibility_compliance_iterator",
            lambda_function=lambda_eligibility_compliance_iterator,
            retry_on_service_exceptions=True,
            result_path="$.iterator",
        )

        is_count_reached = (
            sfn.Choice(self, "IsCountReached")
            .when(
                sfn.Condition.boolean_equals("$.iterator.Payload.continue", True),
                lambda_task_1.next(lambda_task_2),
            )
            .otherwise(sfn.Succeed(self, "Success"))
        )

        definition = glue_task1.next(
            glue_task2.next(lambda_task_2.next(is_count_reached))
        )

        # define state machine
        sfn.StateMachine(
            self,
            "StateMachine_eligibility_calculation",
            definition=definition,
            state_machine_name=environment + "-eligibility-calculation-workflow",
        )
