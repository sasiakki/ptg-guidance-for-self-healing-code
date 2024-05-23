from constructs import Construct
from aws_cdk import (
    Stack,
    aws_s3 as s3,
    aws_lambda as _lambda,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as tasks,
    aws_iam,
    Duration as duration,
    aws_ec2,
    aws_events as events,
    aws_events_targets as targets,
    aws_stepfunctions as stepfunctions,
    triggers
)
import boto3, os, glob, json, time
from .glue_connection import GlueConnection
from bin.get_caller_identity import AccountNumberGetter
from bin.ec2_utils import EC2Utils

class RDSStack(Stack):
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

        ec2_utils = EC2Utils('us-west-2', account_num)
        vpc_id_from_boto, subnet_ids, route_table_ids, sg_group_id, sg_group_name = ec2_utils.get_vpc_subnets_and_security_group(environment)

        
        if environment == 'dev':
            glue_connection = GlueConnection(self, 'glue_connection', 'rdsconnect')
            lambda_vpc = None
            lambda_security_group = None
            s3_bucket_name = f'seiubg-{environment}-db-scripts-jdnf83'
        else:
            glue_connection = GlueConnection(self, 'glue_connection', 'connection-uw2-p-seiubg-prod-b2bds')
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
            s3_bucket_name = f'seiubg-{environment}-db-scripts-jdnf83'
                
        # Reference the existing S3 bucket
        bucket = s3.Bucket.from_bucket_name(self, 'ExisitingBucket', s3_bucket_name)

        # Copy files to the existing S3 bucket
        self.copy_files_to_bucket(bucket)

        custom_layer = _lambda.LayerVersion(
            scope=self, id="custom-layer",
            code=_lambda.AssetCode("lambda_layer/custom-layer/"),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_9],
        )
 
        lambda_execute_db_scripts = _lambda.Function(
            self, 'lambda-execute-db-scripts',
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset('rds-workflow/lambda/lambda-execute-db-scripts/'),
            handler='lambda_function.lambda_handler',
            function_name=environment+'-lambda-execute-db-scripts',
            role=lambda_role,
            timeout=duration.minutes(15),
            layers=[custom_layer],
            environment={
                'account_number': account_num,
                'environment_type': environment
            },
            vpc = lambda_vpc,
            security_groups = lambda_security_group
        )

        triggers.Trigger(self, "DBScriptsExecutionTrigger",
            handler=lambda_execute_db_scripts,
            timeout=duration.minutes(15),
            invocation_type=triggers.InvocationType.EVENT
        )

        lambda_task_1 = tasks.LambdaInvoke(self, "lambda_execute_db_scripts",
            lambda_function=lambda_execute_db_scripts,
            output_path="$.Payload"
        )

        sfn.StateMachine(self, "rds-deployment",
            definition=lambda_task_1,
            state_machine_name=environment+"-rds-deployment"
        )


    def copy_files_to_bucket(self, bucket: s3.IBucket) -> None:

        all_sql_scripts = []
        s3_client = boto3.client('s3')
        for foldername, subfolders, filelist in os.walk('./db_scripts'):
            for file in filelist:
                if(file.endswith('.sql')):
                    sql_file_path = os.path.join(foldername,file)
                    all_sql_scripts.append(sql_file_path)

        for script in all_sql_scripts:        
            file_name = os.path.basename('./db_scripts/'+script)
            s3_key = f'db_scripts/{file_name}'  # Destination key in the S3 bucket
            s3_client.upload_file(script, bucket.bucket_name, s3_key)

        time.sleep(2)
        file_content = 'This is a temporary file.'
        with open('db_scripts/temp.txt', "w") as file:
            file.write(file_content)
        s3_client.upload_file("db_scripts/temp.txt", bucket.bucket_name, 'db_scripts/temp.txt')
        if os.path.exists("db_scripts/temp.txt"):
            os.remove("db_scripts/temp.txt")

