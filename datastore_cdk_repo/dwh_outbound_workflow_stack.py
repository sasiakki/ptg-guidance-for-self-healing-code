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

class DWHOutboundWorkflowStack(Stack):

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

        if environment == 'dev':    
            glue_connection = GlueConnection(self, 'glue_connection', 'rdsconnect')
            
        else:
            glue_connection = GlueConnection(self, 'glue_connection', 'connection-uw2-p-seiubg-prod-b2bds')

        # Creating Glue jobs 
        job = _glue_alpha.Job(self, "glue-dwh-branch-outbound",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V3_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('dwh-outbound-workflow/glue/glue-dwh-branch-outbound.py')
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                            "--account_number": account_num,
                            "--environment_type":environment
            },  
            role=glue_role,
            job_name=environment+'-glue-dwh-branch-outbound'

        )

        job = _glue_alpha.Job(self, "glue-dwh-coursecatalog-outbound",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V3_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('dwh-outbound-workflow/glue/glue-dwh-coursecatalog-outbound.py')
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                            "--account_number": account_num,
                            "--environment_type":environment
            },  
            role=glue_role,
            job_name=environment+'-glue-dwh-coursecatalog-outbound'

        )

        job = _glue_alpha.Job(self, "glue-dwh-courseequivalency-outbound",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V3_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('dwh-outbound-workflow/glue/glue-dwh-courseequivalency-outbound.py')
                
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                            "--account_number": account_num,
                            "--environment_type":environment
            },  
            role=glue_role,
            job_name=environment+'-glue-dwh-courseequivalency-outbound'

        )

        job = _glue_alpha.Job(self, "glue-dwh-credential-outbound",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V3_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('dwh-outbound-workflow/glue/glue-dwh-credential-outbound.py')
               
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                            "--account_number": account_num,
                            "--environment_type":environment
            },  
            role=glue_role,
            job_name=environment+'-glue-dwh-credential-outbound'

        )

        job = _glue_alpha.Job(self, "glue-dwh-dohcompleted-outbound",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V3_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('dwh-outbound-workflow/glue/glue-dwh-dohcompleted-outbound.py')
                
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                            "--account_number": account_num,
                            "--environment_type":environment
            },  
            role=glue_role,
            job_name=environment+'-glue-dwh-dohcompleted-outbound'

        )

        job = _glue_alpha.Job(self, "glue-dwh-dohclassified-outbound",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V3_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('dwh-outbound-workflow/glue/glue-dwh-dohclassified-outbound.py')
                
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                            "--account_number": account_num,
                            "--environment_type":environment
            },  
            role=glue_role,
            job_name=environment+'-glue-dwh-dohclassified-outbound'

        )

        job = _glue_alpha.Job(self, "glue-dwh-duedateextension-outbound",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V3_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('dwh-outbound-workflow/glue/glue-dwh-duedateextension-outbound.py')
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                            "--account_number": account_num,
                            "--environment_type":environment
            },  
            role=glue_role,
            job_name=environment+'-glue-dwh-duedateextension-outbound'

        )

        job = _glue_alpha.Job(self, "glue-dwh-employer-outbound",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V3_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('dwh-outbound-workflow/glue/glue-dwh-employer-outbound.py')
              
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                            "--account_number": account_num,
                            "--environment_type":environment
            },  
            role=glue_role,
            job_name=environment+'-glue-dwh-employer-outbound'

        )

        job = _glue_alpha.Job(self, "glue-dwh-employertrust-outbound",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V3_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('dwh-outbound-workflow/glue/glue-dwh-employertrust-outbound.py')
                
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                            "--account_number": account_num,
                            "--environment_type":environment
            },  
            role=glue_role,
            job_name=environment+'-glue-dwh-employertrust-outbound'

        )

        job = _glue_alpha.Job(self, "glue-dwh-employmentrelationship-outbound",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V3_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('dwh-outbound-workflow/glue/glue-dwh-employmentrelationship-outbound.py')
               
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                            "--account_number": account_num,
                            "--environment_type":environment
            },  
            role=glue_role,
            job_name=environment+'-glue-dwh-employmentrelationship-outbound'

        )

        job = _glue_alpha.Job(self, "glue-dwh-exam-outbound",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V3_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('dwh-outbound-workflow/glue/glue-dwh-exam-outbound.py')
               
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                            "--account_number": account_num,
                            "--environment_type":environment
            },  
            role=glue_role,
            job_name=environment+'-glue-dwh-exam-outbound'

        )

        job = _glue_alpha.Job(self, "glue-dwh-instructor-outbound",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V3_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('dwh-outbound-workflow/glue/glue-dwh-instructor-outbound.py')
              
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                            "--account_number": account_num,
                            "--environment_type":environment
            },  
            role=glue_role,
            job_name=environment+'-glue-dwh-instructor-outbound'

        )

        job = _glue_alpha.Job(self, "glue-dwh-ojteligible-outbound",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V3_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('dwh-outbound-workflow/glue/glue-dwh-ojteligible-outbound.py')
              
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                            "--account_number": account_num,
                            "--environment_type":environment
            },  
            role=glue_role,
            job_name=environment+'-glue-dwh-ojteligible-outbound'

        )

        job = _glue_alpha.Job(self, "glue-dwh-person-outbound",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V3_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('dwh-outbound-workflow/glue/glue-dwh-person-outbound.py')
            
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                            "--account_number": account_num,
                            "--environment_type":environment
            },  
            role=glue_role,
            job_name=environment+'-glue-dwh-person-outbound'

        )


        job = _glue_alpha.Job(self, "glue-dwh-trainingrequirement-outbound",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V3_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('dwh-outbound-workflow/glue/glue-dwh-trainingrequirement-outbound.py')
            
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                            "--account_number": account_num,
                            "--environment_type":environment
            },  
            role=glue_role,
            job_name=environment+'-glue-dwh-trainingrequirement-outbound'

        )

        job = _glue_alpha.Job(self, "glue-dwh-trainingtransfers-outbound",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V3_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('dwh-outbound-workflow/glue/glue-dwh-trainingtransfers-outbound.py')
             
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                            "--account_number": account_num,
                            "--environment_type":environment
            },  
            role=glue_role,
            job_name=environment+'-glue-dwh-trainingtransfers-outbound'

        )

        job = _glue_alpha.Job(self, "glue-dwh-transcript-outbound",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V3_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('dwh-outbound-workflow/glue/glue-dwh-transcript-outbound.py')
             
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                            "--account_number": account_num,
                            "--environment_type":environment
            },  
            role=glue_role,
            job_name=environment+'-glue-dwh-transcript-outbound'

        )

        job = _glue_alpha.Job(self, "glue-dwh-transfers_trainingprogram-outbound",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V3_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset('dwh-outbound-workflow/glue/glue-dwh-transfers_trainingprogram-outbound.py')
             
            ),
            connections = [glue_connection.get_connection()],

            default_arguments={
                            "--account_number": account_num,
                            "--environment_type":environment
            },  
            role=glue_role,
            job_name=environment+'-glue-dwh-transfers_trainingprogram-outbound'

        )

        

        #Defining all task for glue
        glue_task_1 = tasks.GlueStartJobRun(
            self,
            id="glue_dwh_branch_outbound",
            glue_job_name=environment+"-glue-dwh-branch-outbound",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB
        )

        glue_task_3 = tasks.GlueStartJobRun(
            self,
            id="glue_dwh_coursecatalog_outbound",
            glue_job_name=environment+"-glue-dwh-coursecatalog-outbound",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB
        )

        glue_task_4 = tasks.GlueStartJobRun(
            self,
            id="glue_dwh_courseequivalency_outbound",
            glue_job_name=environment+"-glue-dwh-courseequivalency-outbound",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB
        )

        glue_task_5 = tasks.GlueStartJobRun(
            self,
            id="glue_dwh_credential_outbound",
            glue_job_name=environment+"-glue-dwh-credential-outbound",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB
        )

        glue_task_6 = tasks.GlueStartJobRun(
            self,
            id="glue_dwh_dohclassified_outbound",
            glue_job_name=environment+"-glue-dwh-dohclassified-outbound",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB
        )

        glue_task_7 = tasks.GlueStartJobRun(
            self,
            id="glue_dwh_dohcompleted_outbound",
            glue_job_name=environment+"-glue-dwh-dohcompleted-outbound",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB
        )

        glue_task_8 = tasks.GlueStartJobRun(
            self,
            id="glue_dwh_duedateextension_outbound",
            glue_job_name=environment+"-glue-dwh-duedateextension-outbound",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB
        )

        glue_task_9 = tasks.GlueStartJobRun(
            self,
            id="glue_dwh_employer_outbound",
            glue_job_name=environment+"-glue-dwh-employer-outbound",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB
        )

        glue_task_10 = tasks.GlueStartJobRun(
            self,
            id="glue_dwh_employertrust_outbound",
            glue_job_name=environment+"-glue-dwh-employertrust-outbound",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB
        )

        glue_task_11 = tasks.GlueStartJobRun(
            self,
            id="glue_dwh_employmentrelationship_outbound",
            glue_job_name=environment+"-glue-dwh-employmentrelationship-outbound",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB
        )

        glue_task_12 = tasks.GlueStartJobRun(
            self,
            id="glue_dwh_exam_outbound",
            glue_job_name=environment+"-glue-dwh-exam-outbound",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB
        )

        glue_task_13 = tasks.GlueStartJobRun(
            self,
            id="glue_dwh_instructor_outbound",
            glue_job_name=environment+"-glue-dwh-instructor-outbound",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB
        )

        glue_task_14 = tasks.GlueStartJobRun(
            self,
            id="glue_dwh_ojteligible_outbound",
            glue_job_name=environment+"-glue-dwh-ojteligible-outbound",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB
        )

        glue_task_15 = tasks.GlueStartJobRun(
            self,
            id="glue_dwh_person_outbound",
            glue_job_name=environment+"-glue-dwh-person-outbound",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB
        )


        glue_task_17 = tasks.GlueStartJobRun(
            self,
            id="glue_dwh_trainingrequirement_outbound",
            glue_job_name=environment+"-glue-dwh-trainingrequirement-outbound",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB
        )

        glue_task_18 = tasks.GlueStartJobRun(
            self,
            id="glue_dwh_trainingtransfers_outbound",
            glue_job_name=environment+"-glue-dwh-trainingtransfers-outbound",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB
        )

        glue_task_2 = tasks.GlueStartJobRun(
            self,
            id="glue_dwh_transcript_outbound",
            glue_job_name=environment+"-glue-dwh-transcript-outbound",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB
        )

        glue_task_16 = tasks.GlueStartJobRun(
            self,
            id="glue_dwh_transfers_trainingprogram_outbound",
            glue_job_name=environment+"-glue-dwh-transfers_trainingprogram-outbound",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB
        )


        machine_definition = (
            sfn.Parallel(self,id="invoke-all-dwh-parallel-jobs")
                .branch(
                glue_task_1)
                .branch(
                glue_task_2)
                .branch(
                glue_task_3)
                .branch(
                glue_task_4)
                .branch(
                glue_task_5)
                .branch(
                glue_task_6)
                .branch(
                glue_task_7)
                .branch(
                glue_task_8)
                .branch(
                glue_task_9)
                .branch(
                glue_task_10)
                .branch(
                glue_task_11)
                .branch(
                glue_task_12)
                .branch(
                glue_task_13)
                .branch(
                glue_task_14)
                .branch(
                glue_task_15)
                .branch(
                glue_task_16)
                .branch(
                glue_task_17)
                .branch(
                glue_task_18)
                
        )
        
        sfn.StateMachine(self, "dwh_outbound_workflow_stack",
            definition=machine_definition,            
            state_machine_name=environment+"-dwh_outbound_workflow_stack"
        )
