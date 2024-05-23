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
    aws_stepfunctions as stepfunctions
)
from .glue_connection import GlueConnection
from bin.get_caller_identity import AccountNumberGetter

class TrainingCompletionsWorkflowStack(Stack):
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

        if environment == 'dev':
            glue_connection = GlueConnection(self, 'glue_connection', 'rdsconnect')
        else:
            glue_connection = GlueConnection(self, 'glue_connection', 'connection-uw2-p-seiubg-prod-b2bds')


        # Creating lambda's functions & Glue jobs
        lambda_check_cdwatransfers_archive = _lambda.Function(
            self, 
            "lambda-check-cdwatransfers-archive", 
            runtime=_lambda.Runtime.PYTHON_3_9, 
            code=_lambda.Code.from_asset("training-completions-workflow/lambda/lambda-check-cdwatransfers-archive"), 
            handler="lambda_function.lambda_handler", 
            function_name=environment+"-lambda-check-cdwatransfers-archive", 
            role=lambda_role,
            timeout=duration.minutes(1),
            environment={
                'account_number': account_num,
                'environment_type': environment}
        )

        lambda_check_cornerstone = _lambda.Function(
            self, 
            "lambda-check-cornerstone", 
            runtime=_lambda.Runtime.PYTHON_3_9, 
            code=_lambda.Code.from_asset("training-completions-workflow/lambda/lambda-check-cornerstone"), 
            handler="lambda_function.lambda_handler", 
            function_name=environment+"-lambda-check-cornerstone", 
            role=lambda_role,
            timeout=duration.minutes(1),
            environment={
                'account_number': account_num,
                'environment_type': environment}
        )

        lambda_check_cornerstone_archive = _lambda.Function(
            self, 
            "lambda-check-cornerstone-archive", 
            runtime=_lambda.Runtime.PYTHON_3_9, 
            code=_lambda.Code.from_asset("training-completions-workflow/lambda/lambda-check-cornerstone-archive"), 
            handler="lambda_function.lambda_handler", 
            function_name=environment+"-lambda-check-cornerstone-archive", 
            role=lambda_role,
            timeout=duration.minutes(1),
            environment={
                'account_number': account_num,
                'environment_type': environment}
        )

        lambda_check_docebo = _lambda.Function(
            self, 
            "lambda-check-docebo", 
            runtime=_lambda.Runtime.PYTHON_3_9, 
            code=_lambda.Code.from_asset("training-completions-workflow/lambda/lambda-check-docebo"), 
            handler="lambda_function.lambda_handler", 
            function_name=environment+"-lambda-check-docebo", 
            role=lambda_role,
            timeout=duration.minutes(1),
            environment={
                'account_number': account_num,
                'environment_type': environment}
        )

        lambda_check_docebo_ilt = _lambda.Function(
            self, 
            "lambda-check-docebo-ilt", 
            runtime=_lambda.Runtime.PYTHON_3_9, 
            code=_lambda.Code.from_asset("training-completions-workflow/lambda/lambda-check-docebo-ilt"), 
            handler="lambda_function.lambda_handler", 
            function_name=environment+"-lambda-check-docebo-ilt", 
            role=lambda_role,
            timeout=duration.minutes(1),
            environment={
                'account_number': account_num,
                'environment_type': environment}
        )

        lambda_check_docebo_archive = _lambda.Function(
            self, 
            "lambda-check-docebo-archive", 
            runtime=_lambda.Runtime.PYTHON_3_9, 
            code=_lambda.Code.from_asset("training-completions-workflow/lambda/lambda-check-docebo-archive"), 
            handler="lambda_function.lambda_handler", 
            function_name=environment+"-lambda-check-docebo-archive", 
            role=lambda_role,
            timeout=duration.minutes(1),
            environment={
                'account_number': account_num,
                'environment_type': environment}
        )
        
        lambda_check_docebo_ilt_archive = _lambda.Function(
            self, 
            "lambda-check-docebo-ilt-archive", 
            runtime=_lambda.Runtime.PYTHON_3_9, 
            code=_lambda.Code.from_asset("training-completions-workflow/lambda/lambda-check-docebo-ilt-archive"), 
            handler="lambda_function.lambda_handler", 
            function_name=environment+"-lambda-check-docebo-ilt-archive", 
            role=lambda_role,
            timeout=duration.minutes(1),
            environment={
                'account_number': account_num,
                'environment_type': environment}
        )

        lambda_check_qualtricsos_archive = _lambda.Function(
            self, 
            "lambda-check-qualtricsos-archive", 
            runtime=_lambda.Runtime.PYTHON_3_9, 
            code=_lambda.Code.from_asset("training-completions-workflow/lambda/lambda-check-qualtricsos-archive"), 
            handler="lambda_function.lambda_handler", 
            function_name=environment+"-lambda-check-qualtricsos-archive", 
            role=lambda_role,
            timeout=duration.minutes(1),
            environment={
                'account_number': account_num,
                'environment_type': environment}
        )

        lambda_check_qualtricsos = _lambda.Function(
            self, 
            "lambda-check-qualtricsos", 
            runtime=_lambda.Runtime.PYTHON_3_9, 
            code=_lambda.Code.from_asset("training-completions-workflow/lambda/lambda-check-qualtricsos"), 
            handler="lambda_function.lambda_handler", 
            function_name=environment+"-lambda-check-qualtricsos", 
            role=lambda_role,
            timeout=duration.minutes(1),
            environment={
                    'account_number': account_num,
                    'environment_type': environment
                    }
        )

        lambda_check_transcript_corrections = _lambda.Function(
            self, 
            "lambda-check-transcript-corrections", 
            runtime=_lambda.Runtime.PYTHON_3_9, 
            code=_lambda.Code.from_asset("training-completions-workflow/lambda/lambda-check-transcript-corrections"), 
            handler="lambda_function.lambda_handler", 
            function_name=environment+"-lambda-check-transcript-corrections", 
            role=lambda_role,
            timeout=duration.minutes(1),
            environment={
                    'account_number': account_num,
                    'environment_type': environment}
        )

        lambda_check_transcript_corrections_archive = _lambda.Function(
            self, 
            "lambda-check-transcript-corrections-archive", 
            runtime=_lambda.Runtime.PYTHON_3_9, 
            code=_lambda.Code.from_asset("training-completions-workflow/lambda/lambda-check-transcript-corrections-archive"), 
            handler="lambda_function.lambda_handler", 
            function_name=environment+"-lambda-check-transcript-corrections-archive", 
            role=lambda_role,
            timeout=duration.minutes(1),
            environment={
                    'account_number': account_num,
                    'environment_type': environment}
        )

        job = _glue_alpha.Job(self, "glue-cdwa-os-transfers-raw-to-raw-traininghistory",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('training-completions-workflow/glue/glue-cdwa-os-transfers-raw-to-raw-traininghistory.py')
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                            "--account_number": account_num,
                            "--environment_type": environment
            },  
            role=glue_role,
            job_name=environment+'-glue-cdwa-os-transfers-raw-to-raw-traininghistory'

        )


        job = _glue_alpha.Job(self, "glue-cornerstone-completions-raw-to-raw-traininghistory",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('training-completions-workflow/glue/glue-cornerstone-completions-raw-to-raw-traininghistory.py')
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                            "--account_number": account_num,
                            "--environment_type": environment
            },  
            role=glue_role,
            job_name=environment+'-glue-cornerstone-completions-raw-to-raw-traininghistory'

        )


        job = _glue_alpha.Job(self, "glue-cornerstone-completions-s3-to-raw",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('training-completions-workflow/glue/glue-cornerstone-completions-s3-to-raw.py')
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                            "--account_number": account_num,
                            "--environment_type": environment
            },  
            role=glue_role,
            job_name=environment+'-glue-cornerstone-completions-s3-to-raw'

        )

        job = _glue_alpha.Job(self, "glue-coursecompletions-raw-to-staging-traininghistory",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('training-completions-workflow/glue/glue-coursecompletions-raw-to-staging-traininghistory.py')
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                            "--account_number": account_num,
                            "--environment_type": environment
            },  
            role=glue_role,
            job_name=environment+'-glue-coursecompletions-raw-to-staging-traininghistory'

        )

        job = _glue_alpha.Job(self, "glue-docebo-coursecompletions-raw-to-raw-traininghistory",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('training-completions-workflow/glue/glue-docebo-coursecompletions-raw-to-raw-traininghistory.py')
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                            "--account_number": account_num,
                            "--environment_type": environment
            },  
            role=glue_role,
            job_name=environment+'-glue-docebo-coursecompletions-raw-to-raw-traininghistory'

        )

        job = _glue_alpha.Job(self, "glue-docebo-ilt-coursecompletions-raw-to-raw-traininghistory",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('training-completions-workflow/glue/glue-docebo-ilt-coursecompletions-raw-to-raw-traininghistory.py')
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                            "--account_number": account_num,
                            "--environment_type": environment
            },  
            role=glue_role,
            job_name=environment+'-glue-docebo-ilt-coursecompletions-raw-to-raw-traininghistory'

        )

        job = _glue_alpha.Job(self, "glue-docebo-coursecompletions-s3-to-raw",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('training-completions-workflow/glue/glue-docebo-coursecompletions-s3-to-raw.py')
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                            "--account_number": account_num,
                            "--environment_type": environment
            },  
            role=glue_role,
            job_name=environment+'-glue-docebo-coursecompletions-s3-to-raw'

        )

        job = _glue_alpha.Job(self, "glue-docebo-ilt-coursecompletions-s3-to-raw",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('training-completions-workflow/glue/glue-docebo-ilt-coursecompletions-s3-to-raw.py')
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                            "--account_number": account_num,
                            "--environment_type": environment
            },  
            role=glue_role,
            job_name=environment+'-glue-docebo-ilt-coursecompletions-s3-to-raw'

        )

        job = _glue_alpha.Job(self, "glue-dshs-os-completion-raw-to-raw-traininghistory",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('training-completions-workflow/glue/glue-dshs-os-completion-raw-to-raw-traininghistory.py')
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                            "--account_number": account_num,
                            "--environment_type": environment
            },  
            role=glue_role,
            job_name=environment+'-glue-dshs-os-completion-raw-to-raw-traininghistory'

        )

        job = _glue_alpha.Job(self, "glue-dshs-os-completion-s3-to-raw",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('training-completions-workflow/glue/glue-dshs-os-completion-s3-to-raw.py')
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                            "--account_number": account_num,
                            "--environment_type": environment
            },  
            role=glue_role,
            job_name=environment+'-glue-dshs-os-completion-s3-to-raw'

        )

        job = _glue_alpha.Job(self, "glue-identify-and-change-of-learningpath",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('training-completions-workflow/glue/glue-identify-and-change-of-learningpath.py')
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                            "--account_number": account_num,
                            "--environment_type": environment
            },  
            role=glue_role,
            job_name=environment+'-glue-identify-and-change-of-learningpath'

        )

        job = _glue_alpha.Job(self, "glue-learningpath-update-to-trainingrequirement",
            executable=_glue_alpha.JobExecutable.python_shell(
                glue_version=_glue_alpha.GlueVersion.V1_0,
                python_version=_glue_alpha.PythonVersion.THREE_NINE,
                script=_glue_alpha.Code.from_asset('training-completions-workflow/glue/glue-learningpath-update-to-trainingrequirement.py')
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                            "--account_number": account_num,
                            "--environment_type": environment
            },  
            role=glue_role,
            job_name=environment+'-glue-learningpath-update-to-trainingrequirement'

        )

        job = _glue_alpha.Job(self, "glue-ojtcalculations",
            executable=_glue_alpha.JobExecutable.python_shell(
                glue_version=_glue_alpha.GlueVersion.V1_0,
                python_version=_glue_alpha.PythonVersion.THREE_NINE,
                script=_glue_alpha.Code.from_asset('training-completions-workflow/glue/glue-ojtcalculations.py')
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                            "--account_number": account_num,
                            "--environment_type": environment
            },  
            role=glue_role,
            job_name=environment+'-glue-ojtcalculations'

        )

        job = _glue_alpha.Job(self, "glue-training-completion-qualtrics-cleandata",
            executable=_glue_alpha.JobExecutable.python_shell(
                glue_version=_glue_alpha.GlueVersion.V1_0,
                python_version=_glue_alpha.PythonVersion.THREE_NINE,
                script=_glue_alpha.Code.from_asset('training-completions-workflow/glue/glue-training-completion-qualtrics-cleandata.py')
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                            "--account_number": account_num,
                            "--environment_type": environment
            },  
            role=glue_role,
            job_name=environment+'-glue-training-completion-qualtrics-cleandata'

        )

        job = _glue_alpha.Job(self, "glue-qualtrics-os-completion-s3-to-raw",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('training-completions-workflow/glue/glue-qualtrics-os-completion-s3-to-raw.py')
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                            "--account_number": account_num,
                            "--environment_type": environment
            },  
            role=glue_role,
            job_name=environment+'-glue-qualtrics-os-completion-s3-to-raw'

        )

        job = _glue_alpha.Job(self, "glue-qualtrics-os-completions-raw-to-raw-traininghistory",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('training-completions-workflow/glue/glue-qualtrics-os-completions-raw-to-raw-traininghistory.py')
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                            "--account_number": account_num,
                            "--environment_type": environment
            },  
            role=glue_role,
            job_name=environment+'-glue-qualtrics-os-completions-raw-to-raw-traininghistory'

        )

        job = _glue_alpha.Job(self, "glue-smartsheet-s3-to-raw",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('training-completions-workflow/glue/glue-smartsheet-s3-to-raw.py')
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                            "--account_number": account_num,
                            "--environment_type": environment
            },  
            role=glue_role,
            job_name=environment+'-glue-smartsheet-s3-to-raw'

        )

        job = _glue_alpha.Job(self, "glue-ss-coursecompletions-raw-to-raw-traininghistory",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('training-completions-workflow/glue/glue-ss-coursecompletions-raw-to-raw-traininghistory.py')
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                            "--account_number": account_num,
                            "--environment_type": environment
            },  
            role=glue_role,
            job_name=environment+'-glue-ss-coursecompletions-raw-to-raw-traininghistory'

        )

        job = _glue_alpha.Job(self, "glue-carina-processing",
            executable=_glue_alpha.JobExecutable.python_shell(
                glue_version=_glue_alpha.GlueVersion.V1_0,
                python_version=_glue_alpha.PythonVersion.THREE_NINE,
                script=_glue_alpha.Code.from_asset('training-completions-workflow/glue/glue-carina-processing.py')
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                            "--account_number": account_num,
                            "--environment_type": environment
            },  
            role=glue_role,
            job_name=environment+'-glue-carina-processing'

        )

        job = _glue_alpha.Job(self, "glue-truncate-all-trainings-raw-tables",
            executable=_glue_alpha.JobExecutable.python_shell(
                glue_version=_glue_alpha.GlueVersion.V1_0,
                python_version=_glue_alpha.PythonVersion.THREE_NINE,
                script=_glue_alpha.Code.from_asset('training-completions-workflow/glue/glue-truncate-all-trainings-raw-tables.py')
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                            "--account_number": account_num,
                            "--environment_type": environment
            },  
            role=glue_role,
            job_name=environment+'-glue-truncate-all-trainings-raw-tables'

        )

        job = _glue_alpha.Job(self, "glue-update-staging-learner",
            executable=_glue_alpha.JobExecutable.python_shell(
                glue_version=_glue_alpha.GlueVersion.V1_0,
                python_version=_glue_alpha.PythonVersion.THREE_NINE,
                script=_glue_alpha.Code.from_asset('training-completions-workflow/glue/glue-update-staging-learner.py')
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                            "--account_number": account_num,
                            "--environment_type": environment
            },  
            role=glue_role,
            job_name=environment+'-glue-update-staging-learner'

        )

        job = _glue_alpha.Job(self, "glue-update-trainings",
            executable=_glue_alpha.JobExecutable.python_shell(
                glue_version=_glue_alpha.GlueVersion.V1_0,
                python_version=_glue_alpha.PythonVersion.THREE_NINE,
                script=_glue_alpha.Code.from_asset('training-completions-workflow/glue/glue-update-trainings.py')
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                            "--account_number": account_num,
                            "--environment_type": environment
            },  
            role=glue_role,
            job_name=environment+'-glue-update-trainings'

        )

        job = _glue_alpha.Job(self, "glue-transcript-corrections-raw-to-raw-traininghistory",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('training-completions-workflow/glue/glue-transcript-corrections-raw-to-raw-traininghistory.py')
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                            "--account_number": account_num,
                             "--environment_type": environment
            },  
            role=glue_role,
            job_name=environment+'-glue-transcript-corrections-raw-to-raw-traininghistory'

        )


        job = _glue_alpha.Job(self, "glue-transcript-corrections-s3-to-raw",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('training-completions-workflow/glue/glue-transcript-corrections-s3-to-raw.py')
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                            "--account_number": account_num,
                             "--environment_type": environment
            },  
            role=glue_role,
            job_name=environment+'-glue-transcript-corrections-s3-to-raw'

        )
        
        job = _glue_alpha.Job(self, "glue-process-transcript-mapping",
            executable=_glue_alpha.JobExecutable.python_shell(
                glue_version=_glue_alpha.GlueVersion.V1_0,
                python_version=_glue_alpha.PythonVersion.THREE_NINE,
                script=_glue_alpha.Code.from_asset('training-completions-workflow/glue/glue-process-transcript-mapping.py')
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                            "--account_number": account_num,
                             "--environment_type": environment
            },  
            role=glue_role,
            job_name=environment+'-glue-process-transcript-mapping'

	    )


        # Defining all task for lamba's and glue
        lambda_task_1 = tasks.LambdaInvoke(
            self, 
            "lambda_check_qualtricsos", 
            lambda_function=lambda_check_qualtricsos, 
            # Lambda's result is in the attribute `Payload`
            output_path="$.Payload"
        )

        lambda_task_4 = tasks.LambdaInvoke(
            self, 
            "lambda_check_cornerstone", 
            lambda_function=lambda_check_cornerstone, 
            # Lambda's result is in the attribute `Payload`
            output_path="$.Payload"
        )

        lambda_task_5 = tasks.LambdaInvoke(
            self, 
            "lambda_check_docebo", 
            lambda_function=lambda_check_docebo, 
            # Lambda's result is in the attribute `Payload`
            output_path="$.Payload"
        )

        lambda_task_6 = tasks.LambdaInvoke(
            self, 
            "lambda_check_qualtricsos_archive", 
            lambda_function=lambda_check_qualtricsos_archive, 
            # Lambda's result is in the attribute `Payload`
            output_path="$.Payload"
        )

        lambda_task_8 = tasks.LambdaInvoke(
            self, 
            "lambda_check_cdwatransfers_archive", 
            lambda_function=lambda_check_cdwatransfers_archive, 
            # Lambda's result is in the attribute `Payload`
            output_path="$.Payload"
        )

        lambda_task_10 = tasks.LambdaInvoke(
            self, 
            "lambda_check_cornerstone_archive", 
            lambda_function=lambda_check_cornerstone_archive, 
            # Lambda's result is in the attribute `Payload`
            output_path="$.Payload"
        )

        lambda_task_11 = tasks.LambdaInvoke(
            self, 
            "lambda_check_docebo_archive", 
            lambda_function=lambda_check_docebo_archive, 
            # Lambda's result is in the attribute `Payload`
            output_path="$.Payload"
        )

        lambda_task_12 = tasks.LambdaInvoke(
            self, 
            "lambda_check_docebo_ilt", 
            lambda_function=lambda_check_docebo_ilt, 
            # Lambda's result is in the attribute `Payload`
            output_path="$.Payload"
        )

        lambda_task_13 = tasks.LambdaInvoke(
            self, 
            "lambda_check_docebo_ilt_archive", 
            lambda_function=lambda_check_docebo_ilt_archive, 
            # Lambda's result is in the attribute `Payload`
            output_path="$.Payload"
        )


        # lambda_task_4 = tasks.LambdaInvoke(
        lambda_task_check_transcript_corrections = tasks.LambdaInvoke(
            self, 
            "lambda_check_transcript_corrections", 
            lambda_function=lambda_check_transcript_corrections, 
            # Lambda's result is in the attribute `Payload`
            output_path="$.Payload"
        )
        
        # lambda_task_10 = tasks.LambdaInvoke(
        lambda_task_check_transcript_corrections_archive = tasks.LambdaInvoke(
            self, 
            "lambda_check_corrections_archive", 
            lambda_function=lambda_check_transcript_corrections_archive, 
            # Lambda's result is in the attribute `Payload`
            output_path="$.Payload"
        )

        glue_task_1 = tasks.GlueStartJobRun(
            self, 
            id="glue_qualtrics_os_completion_s3_to_raw", 
            glue_job_name=environment+"-glue-qualtrics-os-completion-s3-to-raw",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB
        )


        glue_task_2 = tasks.GlueStartJobRun(
            self, 
            id="glue_dshs_os_completion_s3_to_raw", 
            glue_job_name=environment+"-glue-dshs-os-completion-s3-to-raw",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB
        )

        glue_task_3 = tasks.GlueStartJobRun(
            self, 
            id="glue_smartsheet_s3_to_raw", 
            glue_job_name=environment+"-glue-smartsheet-s3-to-raw",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB
        )

        glue_task_4 = tasks.GlueStartJobRun(
            self, 
            id="glue_cornerstone_completions_s3_to_raw", 
            glue_job_name=environment+"-glue-cornerstone-completions-s3-to-raw",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB 
        )

        glue_task_5 = tasks.GlueStartJobRun(
            self, 
            id="glue_docebo_coursecompletions_s3_to_raw", 
            glue_job_name=environment+"-glue-docebo-coursecompletions-s3-to-raw",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB 
        )

        glue_task_6 = tasks.GlueStartJobRun(
            self, 
            id="glue_training_completion_qualtrics_cleandata", 
            glue_job_name=environment+"-glue-training-completion-qualtrics-cleandata",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB 
        )

        glue_task_7 = tasks.GlueStartJobRun(
            self, 
            id="glue_truncate_all_trainings_raw_tables", 
            glue_job_name=environment+"-glue-truncate-all-trainings-raw-tables",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB 
        )

        glue_task_8 = tasks.GlueStartJobRun(
            self, 
            id="glue_qualtrics_os_completions_raw_to_raw_traininghistory", 
            glue_job_name=environment+"-glue-qualtrics-os-completions-raw-to-raw-traininghistory",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB 
        )

        glue_task_9 = tasks.GlueStartJobRun(
            self, 
            id="glue_dshs_os_completion_raw_to_raw_traininghistory", 
            glue_job_name=environment+"-glue-dshs-os-completion-raw-to-raw-traininghistory",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB 
        )

        glue_task_10 = tasks.GlueStartJobRun(
            self, 
            id="glue_cdwa_os_transfers_raw_to_raw_traininghistory", 
            glue_job_name=environment+"-glue-cdwa-os-transfers-raw-to-raw-traininghistory",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB 
        )

        glue_task_11 = tasks.GlueStartJobRun(
            self, 
            id="glue_ss_coursecompletions_raw_to_raw_traininghistory", 
            glue_job_name=environment+"-glue-ss-coursecompletions-raw-to-raw-traininghistory",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB 
        )

        glue_task_12 = tasks.GlueStartJobRun(
            self, 
            id="glue_cornerstone_completions_raw_to_raw_traininghistory", 
            glue_job_name=environment+"-glue-cornerstone-completions-raw-to-raw-traininghistory",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB 
        )

        glue_task_13 = tasks.GlueStartJobRun(
            self, 
            id="glue_docebo_coursecompletions_raw_to_raw_traininghistory", 
            glue_job_name=environment+"-glue-docebo-coursecompletions-raw-to-raw-traininghistory",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB 
        )

        glue_task_14 = tasks.GlueStartJobRun(
            self, 
            id="glue_coursecompletions_raw_to_staging_traininghistory", 
            glue_job_name=environment+"-glue-coursecompletions-raw-to-staging-traininghistory",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB 
        )

        glue_task_15 = tasks.GlueStartJobRun(
            self, 
            id="glue_update_trainings", 
            glue_job_name=environment+"-glue-update-trainings",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB 
        )

        glue_task_16 = tasks.GlueStartJobRun(
            self, 
            id="glue_identify_and_change_of_learningpath", 
            glue_job_name=environment+"-glue-identify-and-change-of-learningpath",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB 
        )

        glue_task_17 = tasks.GlueStartJobRun(
            self, 
            id="glue_learningpath_update_to_trainingrequirement", 
            glue_job_name=environment+"-glue-learningpath-update-to-trainingrequirement",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB 
        )

        glue_task_18 = tasks.GlueStartJobRun(
            self, 
            id="glue_update_staging_learner", 
            glue_job_name=environment+"-glue-update-staging-learner",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB 
        )

        glue_task_19 = tasks.GlueStartJobRun(
            self, 
            id="glue_carina_processing", 
            glue_job_name=environment+"-glue-carina-processing",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB 
        )

        glue_task_20 = tasks.GlueStartJobRun(
            self, 
            id="glue_ojtcalculations", 
            glue_job_name=environment+"-glue-ojtcalculations",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB 
        )

        glue_task_21 = tasks.GlueStartJobRun(
            self, 
            id="glue_docebo_ilt_coursecompletions_s3_to_raw", 
            glue_job_name=environment+"-glue-docebo-ilt-coursecompletions-s3-to-raw",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB 
        )

        glue_task_22 = tasks.GlueStartJobRun(
            self, 
            id="glue_docebo_ilt_coursecompletions_raw_to_raw_traininghistory", 
            glue_job_name=environment+"-glue-docebo-ilt-coursecompletions-raw-to-raw-traininghistory",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB 
        )

        # glue_task_4 = tasks.GlueStartJobRun(
        glue_task_transcript_corrections_s3_to_raw = tasks.GlueStartJobRun(
            self, 
            id="glue_transcript_corrections_s3_to_raw", 
            glue_job_name=environment+"-glue-transcript-corrections-s3-to-raw",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB 
        )

        # glue_task_12 = tasks.GlueStartJobRun(
        glue_task_ts_corrections_raw_to_raw_traininghistory = tasks.GlueStartJobRun(
            self, 
            id="glue_transcript_corrections_raw_to_raw_traininghistory", 
            glue_job_name=environment+"-glue-transcript-corrections-raw-to-raw-traininghistory",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB 
        )
        
        glue_task_transcript_mapping = tasks.GlueStartJobRun(
            self, 
            id="glue_process_transcript_mapping", 
            glue_job_name=environment+"-glue-process-transcript-mapping",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB 
        )

        end_state_qualtrics_os = sfn.Pass(self,"end-qualtrics-os-ingestion-process")
        end_state_dshs_os = sfn.Pass(self,"end-dshs-os-ingestion-process")
        end_state_smartsheet = sfn.Pass(self,"end-smartsheet-ingestion-process")
        end_state_cornerstone = sfn.Pass(self,"end-cornerstone-ingestion-process")
        end_state_docebo = sfn.Pass(self,"end-docebo-ingestion-process")
        end_state_docebo_ilt = sfn.Pass(self,"end-docebo-ilt-ingestion-process")
        end_state_transcript_corrections = sfn.Pass(self,"end-transcript-correction-ingestion-process")

        machine_definition_1 = (
            sfn.Parallel(self,id="invoke-all-training-sources-parallel-jobs")
            .branch(
                lambda_task_1.next(
                    sfn.Choice(self,"has-qualtrics-os-files")
                    .when(
                        sfn.Condition.boolean_equals("$.result",True), 
                        glue_task_1.next(end_state_qualtrics_os)
                    )
                    .otherwise(end_state_qualtrics_os)
                )
            )
            .branch(
                lambda_task_4.next(
                    sfn.Choice(self, "has-cornerstone-files")
                    .when(
                        sfn.Condition.boolean_equals("$.result",True), 
                        glue_task_4.next(end_state_cornerstone), 
                    )
                    .otherwise(end_state_cornerstone)
                )
            )
            .branch(
                lambda_task_12.next(
                    sfn.Choice(self, "has-docebo-ilt-files")
                    .when(
                        sfn.Condition.boolean_equals("$.result",True), 
                        glue_task_21.next(end_state_docebo), 
                    )
                    .otherwise(end_state_docebo)
                )
            )
            .branch(
                lambda_task_5.next(
                    sfn.Choice(self, "has-docebo-files")
                    .when(
                        sfn.Condition.boolean_equals("$.result",True), 
                        glue_task_5.next(end_state_docebo_ilt), 
                    )
                    .otherwise(end_state_docebo_ilt)
                )
            )
            .branch(
                lambda_task_check_transcript_corrections.next(
                    sfn.Choice(self, "has-transcript-correction-files")
                    .when(
                        sfn.Condition.boolean_equals("$.result",True), 
                        glue_task_transcript_corrections_s3_to_raw.next(end_state_transcript_corrections), 
                    )
                    .otherwise(end_state_transcript_corrections)
                )
            )
        )
        end_state_qualtrics_os_raw = sfn.Pass(self,"end-qualtrics-os-raw-to-raw-ingestion-process")
        end_state_cornerstone_raw = sfn.Pass(self,"end-cornerstone-raw-to-raw-ingestion-process")
        end_state_docebo_raw = sfn.Pass(self,"end-docebo-raw-to-raw-ingestion-process")
        end_state_cdwa_raw = sfn.Pass(self,"end-cdwa-os-raw-to-raw-ingestion-process")
        end_state_docebo_ilt_raw = sfn.Pass(self,"end-docebo-ilt-raw-to-raw-ingestion-process")
        end_state_transcript_corrections_raw = sfn.Pass(self,"end-transcript-corrections-raw-to-raw-ingestion-process")

        machine_definition_2 = (
            sfn.Parallel(self,id="raw-to-raw-traininghistory-parallel-jobs")
            .branch(
                lambda_task_6.next(
                    sfn.Choice(self, "has-ingested-qualtrics-os")
                    .when(
                        sfn.Condition.boolean_equals("$.result",True), 
                        glue_task_8.next(end_state_qualtrics_os_raw), 
                    )
                    .otherwise(end_state_qualtrics_os_raw)
                )
            )
            .branch(
                lambda_task_8.next(
                    sfn.Choice(self, "has-ingested-cdwa-transfers")
                    .when(
                        sfn.Condition.boolean_equals("$.result",True), 
                        glue_task_10.next(end_state_cdwa_raw), 
                    )
                    .otherwise(end_state_cdwa_raw)
                )
            )
            .branch(
                lambda_task_10.next(
                    sfn.Choice(self, "has-ingested-cornerstone-completions")
                    .when(
                        sfn.Condition.boolean_equals("$.result",True), 
                        glue_task_12.next(end_state_cornerstone_raw), 
                    )
                    .otherwise(end_state_cornerstone_raw)
                )
            )
            .branch(
                lambda_task_11.next(
                    sfn.Choice(self, "has-ingested-docebo-completions")
                    .when(
                        sfn.Condition.boolean_equals("$.result",True), 
                        glue_task_13.next(end_state_docebo_raw), 
                    )
                    .otherwise(end_state_docebo_raw)
                )
            )
            .branch(
                lambda_task_13.next(
                    sfn.Choice(self, "has-ingested-docebo-ilt-completions")
                    .when(
                        sfn.Condition.boolean_equals("$.result",True), 
                        glue_task_22.next(end_state_docebo_ilt_raw), 
                    )
                    .otherwise(end_state_docebo_ilt_raw)
                )
            )
            .branch(
                lambda_task_check_transcript_corrections_archive.next(
                    sfn.Choice(self, "has-ingested-transcript-corrections")
                    .when(
                        sfn.Condition.boolean_equals("$.result",True), 
                        glue_task_ts_corrections_raw_to_raw_traininghistory.next(end_state_transcript_corrections_raw), 
                    )
                    .otherwise(end_state_transcript_corrections_raw)
                )
            )
        )

        definition = machine_definition_1.next(glue_task_6.next(glue_task_7.next(machine_definition_2.next(glue_task_14.next(glue_task_15.next(glue_task_16.next(glue_task_17.next(glue_task_transcript_mapping.next(glue_task_18.next(glue_task_19.next(glue_task_20)))))))))))

        sfn.StateMachine(
            self, 
            "training-completions-workflow", 
            definition=definition,
            state_machine_name=environment+"-training-completions-workflow", 
        )