#DT-951 Remove RelDOBLang from E2E Process
'''
from constructs import Construct
from aws_cdk import (
    Stack,
    aws_lambda as _lambda,
    aws_glue as _glue,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as tasks,
    aws_iam,    
    aws_glue_alpha as _glue_alpha
)
import boto3, json
from .glue_connection import GlueConnection
from bin.get_caller_identity import AccountNumberGetter

class ReldoblangWorkflowStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        
        # Create an instance of AccountNumberGetter
        account_number = AccountNumberGetter()

        # Call the get_account_number method
        account_num = account_number.get_account_number()

        if account_num == '529350069891':
            # Get the IAM role by name
            lambda_role = aws_iam.Role.from_role_name(
                self,"LambdaRole", 
                'role-d-lambda-execute'
            )

        
            # Get the IAM role by name
            glue_role = aws_iam.Role.from_role_name(
                self,"GlueRole", 
                'glue-poc-s3access-iam-role'
            )
            glue_connection = GlueConnection(self, 'glue_connection', 'rdsconnect')
        else:
            # Get the IAM role by name
            lambda_role = aws_iam.Role.from_role_name(
                self,"LambdaRole", 
                'role-p-lambda-execute'
            )

            
            # Get the IAM role by name
            glue_role = aws_iam.Role.from_role_name(
                self,"GlueRole", 
                'role-p-glue-data-pipelines'
            )   

            glue_connection = GlueConnection(self, 'glue_connection', 'connection-uw2-p-seiubg-prod-b2bds')


        # client10 = boto3.client('secretsmanager')

        # response1 = client10.get_secret_value(
        #     SecretId='prod/b2bds/rds/system-pipelines'
        # )


        # database_secrets = json.loads(response1['SecretString'])

        # B2B_USER = database_secrets['username']
        # B2B_PASSWORD = database_secrets['password']
        # B2B_HOST = database_secrets['host']
        # B2B_PORT = database_secrets['port']
        # B2B_NAME = 'b2bds'

        # # Define the connection properties
        # connection_properties = {
        #     "JDBC_CONNECTION_URL": f"jdbc:postgresql://{B2B_HOST}:{B2B_PORT}/{B2B_NAME}",
        #     "USERNAME": B2B_USER,
        #     "PASSWORD": B2B_PASSWORD,
        # }

        # connection = _glue.CfnConnection(
        #     self, "MyGlueConnection",
        #     connection_input=_glue.CfnConnection.ConnectionInputProperty(
        #         connection_type="JDBC",
        #         connection_properties={
        #             "JDBC_CONNECTION_URL": "jdbc:postgresql://{B2B_HOST}:{B2B_PORT}/{B2B_NAME}",
        #             "USERNAME": B2B_USER,
        #             "PASSWORD": B2B_PASSWORD
        #         }
        #     )
        # )

        # # Get existing AWS Glue connection by name
        # existing_connection_props = _glue.CfnConnectionProps(
        #     connection_input = _glue.CfnConnection.ConnectionInputProperty(
        #         connection_type="connectionType",
        #         name="connection-uw2-p-seiubg-prod-b2bds"
        #     )
        # )

        # existing_connection = _glue.CfnConnection(
        #     self, "ExistingGlueConnection",
        #     existing_connection_props
        # )

        # existing_connection = _glue.CfnConnection..from_connection_arn(
        #     self, "MyExistingGlueConnection",
        #     connection_arn="arn:aws:glue:us-west-2:123456789012:connection/my-connection-name"
        # )

        # # Create the Glue connection
        # connection = _glue.CfnConnection().Connection(
        #     self, "MyJDBCConnection",
        #     connection_name="my-jdbc-connection",
        #     connection_type=_glue.CfnConnectionProps.ConnectionType.JDBC,
        #     description="My JDBC connection",
        #     jdbc_properties=connection_properties,
        # )

        # s3_bucket = 'dsworkflowstacks-pipelineartifactsbucketaea9a052-109sj1o43d6qg'
        # s3 = boto3.resource('s3')
        # s3_files = list(s3.Bucket(''+s3_bucket+'').objects.filter(Prefix='DSWorkflowStacks-Pip/seiu_uat_r/'))
        # #df= list(objects.key.endswith('TXT'))
        # s3_files.sort(key=lambda o: o.last_modified, reverse=True)
        # sourcepath = "s3://"+s3_bucket+"/"+s3_files[1].key+""

        lambda_check_reldoblang_s3 = _lambda.Function(
            self,
            "lambda-check-reldoblang-s3",
            runtime=_lambda.Runtime.PYTHON_3_9,
            code=_lambda.Code.from_asset("reldoblang-workflow/lambda/lambda-check-reldoblang"),
            handler="lambda_function.lambda_handler",
            function_name=environment+"-lambda-check-reldoblang-s3",
            role=lambda_role,
            environment={
                    'account_number': account_num}
        )

        job = _glue_alpha.Job(self, "glue-reldob-s3-to-raw",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('reldoblang-workflow/glue_jobs/glue-reldob-s3-to-raw.py')
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                            "--account_number": account_num
            },  
            role=glue_role,
            job_name=environment+'-glue-reldob-s3-to-raw'

        )

        job = _glue_alpha.Job(self, "glue-reldob-update-staging",
            executable=_glue_alpha.JobExecutable.python_shell(
                glue_version=_glue_alpha.GlueVersion.V1_0,
                python_version=_glue_alpha.PythonVersion.THREE_NINE,
                script=_glue_alpha.Code.from_asset('reldoblang-workflow/glue_jobs/glue-reldob-update-staging.py')
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                            "--account_number": account_num
            },  
            role=glue_role,
            job_name=environment+'-glue-reldob-update-staging'

        )

        end_reldoblang_process=sfn.Pass(self, "end-reldoblang-process")

        # Defining all task for lamba's and glue
        lambda_task_1 = tasks.LambdaInvoke(
            self,
            "lambda_check_reldoblang_s3",
            lambda_function=lambda_check_reldoblang_s3,
            # Lambda's result is in the attribute `Payload
            result_path="$.lambda_handler",
        )
       
        glue_task_2 = tasks.GlueStartJobRun(
            self, 
            id="glue_reldob_s3_to_raw",
            glue_job_name=environment+"-glue-reldob-s3-to-raw",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB
        ).add_catch(
            end_reldoblang_process,
            errors=["States.ALL"]
        )

        glue_task_3 = tasks.GlueStartJobRun(
            self,
            id="glue_reldob-update-staging",
            glue_job_name=environment+"-glue-reldob-update-staging",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB
        )

        
        machine_definition = lambda_task_1.next(
            sfn.Choice(self, "has-files")
            .when(
                sfn.Condition.boolean_equals("$.lambda_handler.Payload.result", True),
                glue_task_2.next(glue_task_3)
            )
            .otherwise(end_reldoblang_process)
        )
        
        sfn.StateMachine(self, "reldoblang-workflow",
            definition=machine_definition,
            state_machine_name=environment+"-reldoblang-workflow"
        )
        
'''