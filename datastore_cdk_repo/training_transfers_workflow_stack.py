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
    aws_stepfunctions as stepfunctions
)
import boto3
from .glue_connection import GlueConnection
from bin.ec2_utils import EC2Utils

class TrainingTransfersWorkflowStack(Stack):
    def __init__(self,scope: Construct,id: str,environment: str, account_num: str, **kwargs) -> None:
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
        
        ec2_utils = EC2Utils('us-west-2', account_num)
        vpc_id_from_boto, subnet_ids, route_table_ids, sg_group_id, sg_group_name = ec2_utils.get_vpc_subnets_and_security_group(environment)

        if environment == 'dev':
            lambda_vpc = None
            lambda_security_group = None
            glue_connection = GlueConnection(self, 'glue_connection', 'rdsconnect')
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


            glue_connection = GlueConnection(self, 'glue_connection', 'connection-uw2-p-seiubg-prod-b2bds')

        # Creating lambda's functions & Glue jobs
        lambda_check_cdwa_trainingtransfer = _lambda.Function(
            self, 
            "lambda-check-cdwa-trainingtransfer", 
            runtime=_lambda.Runtime.PYTHON_3_9, 
            code=_lambda.Code.from_asset(
                "trainingtransfers-workflow/lambda/lambda-check-cdwa-trainingtransfer/"
            ), 
            handler="lambda_function.lambda_handler", 
            function_name=environment+"-lambda-check-cdwa-trainingtransfer", 
            role=lambda_role,
            timeout=duration.minutes(2),
            environment={
                'account_number': account_num,
                'environment_type': environment
            }
        )

        lambda_check_trainingtransfer = _lambda.Function(
            self, 
            "lambda-check-trainingtransfer", 
            runtime=_lambda.Runtime.PYTHON_3_9, 
            code=_lambda.Code.from_asset(
                "trainingtransfers-workflow/lambda/lambda-check-trainingtransfer/"
            ), 
            handler="lambda_function.lambda_handler", 
            function_name=environment+"-lambda-check-trainingtransfer", 
            role=lambda_role,
            timeout=duration.minutes(2),
            environment={
                'account_number': account_num,
                'environment_type': environment
                }
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

        lambda_check_file_processed_status = _lambda.Function(
            self, 
            "lambda-check-file-processed-status", 
            runtime=_lambda.Runtime.PYTHON_3_9, 
            code=_lambda.Code.from_asset(
                "trainingtransfers-workflow/lambda/lambda-check-file-processed-status/"
            ), 
            handler="lambda_function.lambda_handler", 
            function_name=environment+"-lambda-check-file-processed-status", 
            role=lambda_role,
            timeout=duration.minutes(2),            
            layers=[custom_layer,AWS_Parameters_and_Secrets_layer],
            environment={
                'account_number': account_num,
                'environment_type': environment
            },
            vpc = lambda_vpc,
            security_groups = lambda_security_group
        )

        lambda_invoke_file_processed_email = _lambda.Function(
            self, 
            "lambda-invoke-file-processed-email", 
            runtime=_lambda.Runtime.PYTHON_3_9, 
            code=_lambda.Code.from_asset(
                "trainingtransfers-workflow/lambda/lambda-invoke-file-processed-email/"
            ), 
            handler="lambda_function.lambda_handler", 
            function_name=environment+"-lambda-invoke-file-processed-email", 
            role=lambda_role,
            timeout=duration.minutes(2),
            environment={
                'account_number': account_num,
                'environment_type': environment
                }
        )

        lambda_cdwa_file_validation_status = _lambda.Function(
            self, 
            "lambda-cdwa-file-validation-status", 
            runtime=_lambda.Runtime.PYTHON_3_9, 
            code=_lambda.Code.from_asset(
                "trainingtransfers-workflow/lambda/lambda-cdwa-file-validation-status/"
            ), 
            handler="lambda_function.lambda_handler", 
            function_name=environment+"-lambda-cdwa-file-validation-status", 
            role=lambda_role,
            timeout=duration.minutes(2),
            environment={
                'account_number': account_num,
                'environment_type': environment
            },
            vpc = lambda_vpc,
            security_groups = lambda_security_group,
            layers=[custom_layer,AWS_Parameters_and_Secrets_layer]
        )

        lambda_invoke_file_validation_email = _lambda.Function(
            self, 
            "lambda-invoke-file-validation-email", 
            runtime=_lambda.Runtime.PYTHON_3_9, 
            code=_lambda.Code.from_asset(
                "trainingtransfers-workflow/lambda/lambda-invoke-file-validation-email/"
            ), 
            handler="lambda_function.lambda_handler", 
            function_name=environment+"-lambda-invoke-file-validation-email", 
            role=lambda_role,
            timeout=duration.minutes(2),
            environment={
                'account_number': account_num,
                'environment_type': environment
            },
            layers=[custom_layer,AWS_Parameters_and_Secrets_layer]
        )

        job = _glue_alpha.Job(self, "glue-cdwa-transfers-s3-to-raw",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('trainingtransfers-workflow/glue/glue-cdwa-transfers-s3-to-raw.py')
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                "--account_number": account_num,
                "--environment_type": environment
            },  
            role=glue_role,
            job_name=environment+'-glue-cdwa-transfers-s3-to-raw'

        )
        
        job = _glue_alpha.Job(self, "glue-cdwa-transfers-validation",
            executable=_glue_alpha.JobExecutable.python_shell(
                glue_version=_glue_alpha.GlueVersion.V1_0,
                python_version=_glue_alpha.PythonVersion.THREE_NINE,
                script=_glue_alpha.Code.from_asset('trainingtransfers-workflow/glue/glue-cdwa-transfers-validation.py')
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                "--account_number": account_num,
                "--environment_type": environment
            },  
            role=glue_role,
            job_name=environment+'-glue-cdwa-transfers-validation'

        )

        job = _glue_alpha.Job(self, "glue-cdwa-transfers-raw-to-staging-transfers",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('trainingtransfers-workflow/glue/glue-cdwa-transfers-raw-to-staging-transfers.py')
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                "--account_number": account_num,
                "--environment_type": environment
            },  
            role=glue_role,
            job_name=environment+'-glue-cdwa-transfers-raw-to-staging-transfers'

        )

        job = _glue_alpha.Job(self, "glue-manual-qualtrics-training-transferhours-s3-to-raw",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('trainingtransfers-workflow/glue/glue-manual-qualtrics-training-transferhours-s3-to-raw.py')
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                "--account_number": account_num,
                "--environment_type": environment
            },  
            role=glue_role,
            job_name=environment+'-glue-manual-qualtrics-training-transferhours-s3-to-raw'

        )


        job = _glue_alpha.Job(self, "glue-manual-qualtrics-training-transferhours-raw-to-staging",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('trainingtransfers-workflow/glue/glue-manual-qualtrics-training-transferhours-raw-to-staging.py')
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                "--account_number": account_num,
                "--environment_type": environment
            },  
            role=glue_role,
            job_name=environment+'-glue-manual-qualtrics-training-transferhours-raw-to-staging'

        )


        job = _glue_alpha.Job(self, "glue-process-training-transfers",
            executable=_glue_alpha.JobExecutable.python_shell(
                glue_version=_glue_alpha.GlueVersion.V1_0,
                python_version=_glue_alpha.PythonVersion.THREE_NINE,
                script=_glue_alpha.Code.from_asset('trainingtransfers-workflow/glue/glue-process-training-transfers.py')
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                "--account_number": account_num,
                "--environment_type": environment
            },  
            role=glue_role,
            job_name=environment+'-glue-process-training-transfers'

        )



        # Defining all task for lamba's and glue
        lambda_task_1 = tasks.LambdaInvoke(
            self, 
            "lambda_check_cdwa_trainingtransfer", 
            lambda_function=lambda_check_cdwa_trainingtransfer, 
            # Lambda's result is in the attribute `Payload`
        )

        lambda_task_2 = tasks.LambdaInvoke(
            self, 
            "lambda_check_trainingtransfer", 
            lambda_function=lambda_check_trainingtransfer, 
            # Lambda's result is in the attribute `Payload`
            output_path="$.Payload", 
        )

        lambda_task_3 = tasks.LambdaInvoke(
            self, 
            "lambda_check_file_processed_status", 
            lambda_function=lambda_check_file_processed_status, 
            # Lambda's result is in the attribute `Payload`
            payload=sfn.TaskInput.from_object({"type": "Processing"}),
            result_selector={
                "filename": sfn.JsonPath.string_at("$.Payload.body.filename"),
                "filecount": sfn.JsonPath.string_at("$.Payload.body.filecount"),
            }
        )

        lambda_task_4 = tasks.LambdaInvoke(
            self, 
            "lambda_invoke_file_processed_email", 
            lambda_function=lambda_invoke_file_processed_email, 
            # Lambda's result is in the attribute `Payload`
            payload=sfn.TaskInput.from_object({
                    "filename.$": "$.filename",
                    "filecount.$": "$.filecount",
                    "type": "Processing"
            })
        )

        lambda_task_5 = tasks.LambdaInvoke(
            self, 
            "lambda_cdwa_file_validation_status", 
            lambda_function=lambda_cdwa_file_validation_status, 
            # Lambda's result is in the attribute `Payload`
            payload=sfn.TaskInput.from_object({"type": "Datavalidation"}),
            result_selector={
                "filename": sfn.JsonPath.string_at("$.Payload.body.filename"),
                "filecount": sfn.JsonPath.string_at("$.Payload.body.filecount"),
            }
        )

        lambda_task_6 = tasks.LambdaInvoke(
            self, 
            "lambda_invoke_file_validation_email", 
            lambda_function=lambda_invoke_file_validation_email, 
            # Lambda's result is in the attribute `Payload`
            payload=sfn.TaskInput.from_object({
                    "filename.$": "$.filename",
                    "filecount.$": "$.filecount",
                    "type": "Datavalidation"
            })
        ) 

        glue_task_1 = tasks.GlueStartJobRun(
            self, 
            id="glue_cdwa_transfers_s3_to_raw", 
            glue_job_name=environment+"-glue-cdwa-transfers-s3-to-raw",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB 
        )

        glue_task_2 = tasks.GlueStartJobRun(
            self, 
            id="glue_cdwa_transfers_validation", 
            glue_job_name=environment+"-glue-cdwa-transfers-validation",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB 
        )

        glue_task_3 = tasks.GlueStartJobRun(
            self, 
            id="glue_cdwa_transfers_raw_to_staging_transfers", 
            glue_job_name=environment+"-glue-cdwa-transfers-raw-to-staging-transfers",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB 
        )

        glue_task_4 = tasks.GlueStartJobRun(
            self, 
            id="glue_manual_qualtrics_training_transferhours_s3_to_raw", 
            glue_job_name=environment+"-glue-manual-qualtrics-training-transferhours-s3-to-raw",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB
        )

        glue_task_5 = tasks.GlueStartJobRun(
            self, 
            id="glue_manual_qualtrics_training_transferhours_raw_to_staging", 
            glue_job_name=environment+"-glue-manual-qualtrics-training-transferhours-raw-to-staging",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB 
        )

        glue_task_6 = tasks.GlueStartJobRun(
            self, 
            id="glue_process_training_transfers", 
            glue_job_name=environment+"-glue-process-training-transfers",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB 
        )

        #----------------------------
        definition1 = glue_task_1.next((sfn.Choice(self, "has-loaded-files")
                        .when(
                                sfn.Condition.string_equals("$.JobRunState", "SUCCEEDED"),                        
                                lambda_task_3.next(lambda_task_4.next(glue_task_2))
                            ).otherwise(glue_task_2)
                            .afterwards()
                            )
        )

        definition2 = (sfn.Choice(self, "has-validation-completed")
                        .when(
                                sfn.Condition.string_equals("$.JobRunState", "SUCCEEDED"),                        
                                lambda_task_5.next(lambda_task_6.next(glue_task_3))
                            ).otherwise(glue_task_3)
                            .afterwards()
        )

        #-----------------------------

        definition = (
            sfn.Parallel(self,id="invoke-all-training-sources-parallel-jobs")
            .branch(
                lambda_task_1.next(
                    sfn.Choice(self,"has-cdwa-training-transfer-files")
                    .when(
                        sfn.Condition.boolean_equals("$.Payload.result",True),
                        definition1.next(definition2)                       
                    )
                    .otherwise(
                        sfn.Pass(self,"end-cdwa-transfers-process")
                    )
                )
            )
            .branch(
                lambda_task_2.next(
                    sfn.Choice(self,"has-qualtrics-training-transfer-files")
                    .when(
                        sfn.Condition.boolean_equals("$.result",True), 
                        glue_task_4.next(glue_task_5), 
                    )
                    .otherwise(sfn.Pass(self,"end-qualrics-transfers-process"))
                )
            )
        )

        machine_definition = definition.next(glue_task_6)

        sfn.StateMachine(
            self, 
            "training-transfers-workflow", 
            definition=machine_definition,
            state_machine_name=environment+"-training-transfers-workflow", 
        )