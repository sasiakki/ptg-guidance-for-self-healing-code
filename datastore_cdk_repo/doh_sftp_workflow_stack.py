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


class DohSftpWorkflowstack(Stack):

    def __init__(self,scope: Construct,id: str, environment: str, account_num: str, **kwargs) -> None:
        super().__init__(scope,id,**kwargs)
        # Create an instance of AccountNumberGetter
        account_number = AccountNumberGetter()

        account_id = AccountNumberGetter()
        # Call the get_account_number method
        devops_account_id = account_number.get_account_number()

        # Get the IAM role by name
        lambda_role = aws_iam.Role.from_role_name(
                self,"LambdaRole", 
                'role-d-lambda-execute'
        )
        glue_role = aws_iam.Role.from_role_name(
            self,"GlueRole", 
            'role-p-glue-data-pipelines'
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

        layer_pandas_3_8 = f'arn:aws:lambda:us-west-2:{devops_account_id}:layer:pandas:1'
        layer_xlrd_3_8 = f'arn:aws:lambda:us-west-2:{devops_account_id}:layer:xlrd:2'
        layer_paramiko_3_8 = f'arn:aws:lambda:us-west-2:{devops_account_id}:layer:paramiko:2'
            

        AWS_Lambda_Python38_layer_pandas = _lambda.LayerVersion.from_layer_version_arn(
            scope=self, id='layer_pandas_3_8',
            layer_version_arn=layer_pandas_3_8
        )

        AWS_Lambda_Python38_layer_xlrd = _lambda.LayerVersion.from_layer_version_arn(
            scope=self, id='layer_xlrd_3_8',
            layer_version_arn=layer_xlrd_3_8
        )

        AWS_Lambda_Python38_layer_paramiko = _lambda.LayerVersion.from_layer_version_arn(
            scope=self, id='layer_paramiko_3_8',
            layer_version_arn=layer_paramiko_3_8
        )

        layer_aws_layer_3_8 = 'arn:aws:lambda:us-west-2:420165488524:layer:AWSLambda-Python38-SciPy1x:107'
        AWS_Lambda_Python38_SciPy1x = _lambda.LayerVersion.from_layer_version_arn(
            scope=self, id='AWSLambda-Python38-SciPy1x',
            layer_version_arn=layer_aws_layer_3_8
        )

        layer_arn = 'arn:aws:lambda:us-west-2:345057560386:layer:AWS-Parameters-and-Secrets-Lambda-Extension:4'
        AWS_Parameters_and_Secrets_layer = _lambda.LayerVersion.from_layer_version_arn(
            scope=self, id='AWS-Parameters-and-Secrets-Lambda-Extension',
            layer_version_arn=layer_arn
        )

        custom_layer = _lambda.LayerVersion(
            scope=self, id="custom-layer",
            code=_lambda.AssetCode("lambda_layer/custom-layer/"),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_9],
        )


        lambda_sftp_doh = _lambda.Function(
            self,'lambda-sftp-doh', 
            runtime=_lambda.Runtime.PYTHON_3_8, 
            code=_lambda.Code.from_asset('api-and-sftp-to-s3-workflow/lambda/lambda-sftp'), 
            handler='lambda_function.lambda_handler', 
            function_name=environment+'-lambda-sftp-doh', 
            role=lambda_role,
            timeout=duration.minutes(5),
            environment={
                'account_number': account_num,
                'environment_type' : environment
            },
            layers = [AWS_Lambda_Python38_layer_xlrd,AWS_Lambda_Python38_layer_pandas,AWS_Lambda_Python38_SciPy1x,AWS_Lambda_Python38_layer_paramiko]
        )

        lambda_sftp_db_log_read_doh = _lambda.Function(
            self,'lambda-sftp-db-log-read-doh', 
            runtime=_lambda.Runtime.PYTHON_3_9, 
            code=_lambda.Code.from_asset('api-and-sftp-to-s3-workflow/lambda/lambda-sftp-db-log-read'), 
            handler='lambda_function.lambda_handler', 
            function_name=environment+'-lambda-sftp-db-log-read-doh', 
            role=lambda_role,
            layers=[custom_layer,AWS_Parameters_and_Secrets_layer],
            timeout=duration.minutes(5),
            environment={
                'account_number': account_num,
                'environment_type' : environment
            },
            vpc = lambda_vpc,
            security_groups=lambda_security_group
        )

        lambda_sftp_db_log_write_doh = _lambda.Function(
            self,'lambda-sftp-db-log-write-doh', 
            runtime=_lambda.Runtime.PYTHON_3_9, 
            code=_lambda.Code.from_asset('api-and-sftp-to-s3-workflow/lambda/lambda-sftp-db-log-write'), 
            handler='lambda_function.lambda_handler', 
            function_name=environment+'-lambda-sftp-db-log-write-doh', 
            role=lambda_role,
            layers=[custom_layer,AWS_Parameters_and_Secrets_layer],
            timeout=duration.minutes(5),
            environment={
                'account_number': account_num,
                'environment_type' : environment
            },
            vpc = lambda_vpc,
            security_groups=lambda_security_group
        )


        input_data_doh_completed = { 
            "category": "doh-inbound-completed"
        }

        input_doh_completed_json = json.dumps(input_data_doh_completed)
        input_doh_completed_object = sfn.TaskInput.from_text(input_doh_completed_json)


        lambda_task_3 = tasks.LambdaInvoke(self,"lambda_sftp_db_log_write_doh_completed", 
            lambda_function=lambda_sftp_db_log_write_doh, 
            # Lambda's result is in the attribute `Payload`
            # Pass input data as a JSON string
            payload=sfn.TaskInput.from_json_path_at("$.Payload")
        )


        lambda_task_2 = tasks.LambdaInvoke(self,"lambda_sftp_doh_completed", 
            lambda_function=lambda_sftp_doh, 
            # Lambda's result is in the attribute `Payload`
            # Pass input data as a JSON string
            payload=sfn.TaskInput.from_json_path_at("$.Payload")
        )

        lambda_task_1 = tasks.LambdaInvoke(self,"lambda_sftp_db_log_read_doh_completed", 
            lambda_function=lambda_sftp_db_log_read_doh, 
            # Lambda's result is in the attribute `Payload`
            # Pass input data as a JSON string 
            payload=input_doh_completed_object
        )


        input_data_doh_classified = { 
            "category": "doh-inbound-classified"
        }

        input_doh_classified_json = json.dumps(input_data_doh_classified)
        input_doh_classified_object = sfn.TaskInput.from_text(input_doh_classified_json)


        lambda_task_6 = tasks.LambdaInvoke(self,"lambda_sftp_db_log_write_doh_classified", 
            lambda_function=lambda_sftp_db_log_write_doh, 
            # Lambda's result is in the attribute `Payload`
            # Pass input data as a JSON string
            payload=sfn.TaskInput.from_json_path_at("$.Payload")
        )


        lambda_task_5 = tasks.LambdaInvoke(self,"lambda_sftp_doh_classified", 
            lambda_function=lambda_sftp_doh, 
            # Lambda's result is in the attribute `Payload`
            # Pass input data as a JSON string
            payload=sfn.TaskInput.from_json_path_at("$.Payload")
        )

        lambda_task_4 = tasks.LambdaInvoke(self,"lambda_sftp_db_log_read_doh_classified", 
            lambda_function=lambda_sftp_db_log_read_doh, 
            # Lambda's result is in the attribute `Payload`
            # Pass input data as a JSON string 
            payload=input_doh_classified_object
        )
        
        
        definition = (
            sfn.Parallel(self,id="invoke-all-doh-parallel-jobs")
            .branch(
                    lambda_task_1.next(lambda_task_2.next(lambda_task_3))
            )
            .branch(
                   lambda_task_4.next(lambda_task_5.next(lambda_task_6))
            )
            .next(sfn.Pass(self,"end-doh-parallel-process"))
        )

        sfn.StateMachine(self,"doh-sftp-workflow",  
            definition=definition,
            state_machine_name=environment+"-doh-sftp-workflow"    
        )