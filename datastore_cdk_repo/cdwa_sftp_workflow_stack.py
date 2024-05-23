from constructs import Construct
from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_glue as _glue,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as tasks,
    aws_iam,
    Duration as duration,
    aws_ec2,
    aws_stepfunctions as stepfunctions
)
import json
from bin.get_caller_identity import AccountNumberGetter
from bin.ec2_utils import EC2Utils


class Lambdalayer(_lambda.LayerVersion):
    def __init__(self, scope: Construct, id: str):
        super().__init__(
            scope,
            id,
            code=_lambda.Code.from_asset("lambda_layer/python-custom-layer/"),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_9]
        )


class CdwaSftpWorkflowstack(Stack):
    def __init__(self, scope: Construct, id: str, environment: str, account_num: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        

        # Get the IAM role by name
        lambda_role = aws_iam.Role.from_role_name(
            self, "LambdaRole", "role-d-lambda-execute"
        )
        ec2_utils = EC2Utils('us-west-2', account_num)
        vpc_id_from_boto, subnet_ids, route_table_ids, sg_group_id, sg_group_name = ec2_utils.get_vpc_subnets_and_security_group(environment)

        if environment == 'dev':
            lambda_vpc = None
            lambda_security_group = None
        else:
            lambda_vpc = aws_ec2.Vpc.from_vpc_attributes(
                self,
                "lambda_vpc",
                vpc_id=vpc_id_from_boto,
                region="us-west-2",
                availability_zones=["us-west-2a", "us-west-2b", "us-west-2c", "us-west-2d"],
                private_subnet_ids=subnet_ids,
                private_subnet_route_table_ids=route_table_ids,
            )
            lambda_security_group_object = aws_ec2.SecurityGroup.from_security_group_id(
                self, sg_group_name, sg_group_id
            )
            lambda_security_group = [lambda_security_group_object]

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


        lambda_sftp_cdwa = _lambda.Function(
            self,'lambda-sftp-cdwa', 
            runtime=_lambda.Runtime.PYTHON_3_9, 
            code=_lambda.Code.from_asset('api-and-sftp-to-s3-workflow/lambda/lambda-sftp'), 
            handler='lambda_function.lambda_handler', 
            function_name=environment + '-lambda-sftp-cdwa', 
            role=lambda_role,
            layers=[custom_layer,AWS_Parameters_and_Secrets_layer],
            timeout=duration.minutes(5),
            environment={
                "account_number": account_num,
                "environment_type": environment,
            },
            memory_size=512
        )


        lambda_sftp_db_log_read_cdwa = _lambda.Function(
            self,'lambda-sftp-db-log-read-cdwa-providerinfo', 
            runtime=_lambda.Runtime.PYTHON_3_9, 
            code=_lambda.Code.from_asset('api-and-sftp-to-s3-workflow/lambda/lambda-sftp-db-log-read'), 
            handler='lambda_function.lambda_handler', 
            function_name=environment + '-lambda-sftp-db-log-read-cdwa', 
            role=lambda_role,
            layers=[custom_layer,AWS_Parameters_and_Secrets_layer],
            timeout=duration.minutes(5),
            environment={
                "account_number": account_num,
                "environment_type": environment,
            },
            vpc = lambda_vpc,
            security_groups = lambda_security_group
        )

        lambda_sftp_db_log_write_cdwa = _lambda.Function(
            self,'lambda-sftp-db-log-write-cdwa', 
            runtime=_lambda.Runtime.PYTHON_3_9, 
            code=_lambda.Code.from_asset('api-and-sftp-to-s3-workflow/lambda/lambda-sftp-db-log-write'), 
            handler='lambda_function.lambda_handler', 
            function_name=environment + '-lambda-sftp-db-log-write-cdwa', 
            role=lambda_role,
            layers=[custom_layer,AWS_Parameters_and_Secrets_layer],
            timeout=duration.minutes(5),
            environment={
                "account_number": account_num,
                "environment_type": environment,
            },
            vpc = lambda_vpc,
            security_groups = lambda_security_group
        )

        input_data_cdwa_providerinfo= {
            "category": "cdwa-providerinfo"
        }

        input_cdwa_providerinfo_json = json.dumps(input_data_cdwa_providerinfo)
        input_cdwa_providerinfo_object = sfn.TaskInput.from_text(input_cdwa_providerinfo_json)

        lambda_task_3 = tasks.LambdaInvoke(self,"lambda_sftp_db_log_write_cdwa_providerinfo", 
            lambda_function=lambda_sftp_db_log_write_cdwa, 
            # Lambda's result is in the attribute `Payload`
            # Pass input data as a JSON string
            payload=sfn.TaskInput.from_json_path_at("$.Payload"),
        )

        lambda_task_2 = tasks.LambdaInvoke(self,"lambda_sftp_cdwa_providerinfo", 
            lambda_function=lambda_sftp_cdwa, 
            # Lambda's result is in the attribute `Payload`
            # Pass input data as a JSON string
            payload=sfn.TaskInput.from_json_path_at("$.Payload"),
        )

        lambda_task_1 = tasks.LambdaInvoke(self,"lambda_sftp_db_log_read_cdwa_providerinfo", 
            lambda_function=lambda_sftp_db_log_read_cdwa, 
            # Lambda's result is in the attribute `Payload`
            # Pass input data as a JSON string
            payload=input_cdwa_providerinfo_object, 
        )
        
        
        input_data_cdwa_transfers = {
            "category": "cdwa-trainingtransfer"
        }

        input_cdwa_transfers_json = json.dumps(input_data_cdwa_transfers)
        input_cdwa_transfers_object = sfn.TaskInput.from_text(input_cdwa_transfers_json)


        lambda_task_6 = tasks.LambdaInvoke(self,"lambda_sftp_db_log_write_cdwa_training_transfers", 
            lambda_function=lambda_sftp_db_log_write_cdwa, 
            # Lambda's result is in the attribute `Payload`
            # Pass input data as a JSON string
            payload=sfn.TaskInput.from_json_path_at("$.Payload")
        )


        lambda_task_5 = tasks.LambdaInvoke(self,"lambda_sftp_cdwa_training_transfers", 
            lambda_function=lambda_sftp_cdwa, 
            # Lambda's result is in the attribute `Payload`
            # Pass input data as a JSON string
            payload=sfn.TaskInput.from_json_path_at("$.Payload")
        )

        lambda_task_4 = tasks.LambdaInvoke(self,"lambda_sftp_db_log_read_cdwa_training_transfers", 
            lambda_function=lambda_sftp_db_log_read_cdwa, 
            # Lambda's result is in the attribute `Payload`
            # Pass input data as a JSON string
            payload=input_cdwa_transfers_object
        )

        definition = (
            sfn.Parallel(self,id="invoke-all-cdwa-parallel-jobs")
            .branch(
                    lambda_task_1.next(lambda_task_2.next(lambda_task_3))
            )
            .branch(
                   lambda_task_4.next(lambda_task_5.next(lambda_task_6))
            )
            .next(sfn.Pass(self,"end-cdwa-parallel-process"))
        )

        sfn.StateMachine(self,"cdwa-sftp-workflow",  
            definition=definition,
            state_machine_name=environment + "-cdwa-sftp-workflow"    
        )