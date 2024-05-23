from constructs import Construct
from aws_cdk import (
    Stack,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as tasks,
    aws_iam,
    aws_glue_alpha as _glue_alpha,
)
from .glue_connection import GlueConnection


class MigrationWorkflowStack(Stack):
    def __init__(
        self, scope: Construct, id: str, environment: str, account_num: str, **kwargs
    ) -> None:
        super().__init__(scope, id, **kwargs)

        if environment == "dev":
            # Get the IAM role by name
            lambda_role = aws_iam.Role.from_role_name(
                self, "LambdaRole", "role-d-lambda-execute"
            )

            # Get the IAM role by name
            glue_role = aws_iam.Role.from_role_name(
                self, "GlueRole", "glue-poc-s3access-iam-role"
            )
            glue_connection = GlueConnection(self, "glue_connection", "rdsconnect")
            cryptography_pythonlib = "s3://b2b-jars/cryptography/cffi-1.15.0-cp37-cp37m-manylinux_2_12_x86_64.manylinux2010_x86_64.whl,s3://b2b-jars/cryptography/fernet-1.0.1.zip,s3://b2b-jars/cryptography/cryptography-36.0.2-cp36-abi3-manylinux_2_24_x86_64.whl,s3://b2b-jars/cryptography/pycparser-2.21-py2.py3-none-any.whl,s3://b2b-jars/cryptography/pyaes-1.6.1.tar.gz"

        else:
            # Get the IAM role by name
            lambda_role = aws_iam.Role.from_role_name(
                self, "LambdaRole", "role-p-lambda-execute"
            )

            # Get the IAM role by name
            glue_role = aws_iam.Role.from_role_name(
                self, "GlueRole", "role-p-glue-data-pipelines"
            )
            glue_connection = GlueConnection(
                self, "glue_connection", "connection-uw2-p-seiubg-prod-b2bds"
            )
        cryptography_pythonlib = "s3://seiubg-b2bds-prod-glue-etl-scripts-b0p3e/dependencies/cryptography_dependencies/cffi-1.15.0-cp37-cp37m-manylinux_2_12_x86_64.manylinux2010_x86_64.whl,s3://seiubg-b2bds-prod-glue-etl-scripts-b0p3e/dependencies/fernet-1.0.1.zip,s3://seiubg-b2bds-prod-glue-etl-scripts-b0p3e/dependencies/cryptography_dependencies/cryptography-36.0.2-cp36-abi3-manylinux_2_24_x86_64.whl,s3://seiubg-b2bds-prod-glue-etl-scripts-b0p3e/dependencies/cryptography_dependencies/pycparser-2.21-py2.py3-none-any.whl,s3://seiubg-b2bds-prod-glue-etl-scripts-b0p3e/dependencies/cryptography_dependencies/pyaes-1.6.1.tar.gz"

        # Define the Glue job

        _glue_alpha.Job(
            self,
            "glue-coursecatalog-version-update",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset(
                    "migration_scripts/glue/glue-coursecatalog-version-update.py"
                ),
            ),
            role=glue_role,
            job_name=environment + "-glue-coursecatalog-version-update",
            default_arguments={
                "--account_number": account_num,
                "--class": "GlueApp",
                "--environment_type": environment,
            },
            connections=[glue_connection.get_connection()],
            worker_type=_glue_alpha.WorkerType.G_1_X,
            worker_count=10,
        )

        _glue_alpha.Job(
            self,
            "glue-migration-logs-traineestatuslogs",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset(
                    "migration_scripts/glue/glue-migration-logs-traineestatuslogs.py"
                ),
            ),
            role=glue_role,
            job_name=environment + "-glue-migration-logs-traineestatuslogs",
            default_arguments={
                "--account_number": account_num,
                "--class": "GlueApp",
                "--environment_type": environment,
            },
            connections=[glue_connection.get_connection()],
            worker_type=_glue_alpha.WorkerType.G_1_X,
            worker_count=10,
        )

        _glue_alpha.Job(
            self,
            "glue-migration-prod-branch",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset(
                    "migration_scripts/glue/glue-migration-prod-branch.py"
                ),
            ),
            role=glue_role,
            job_name=environment + "-glue-migration-prod-branch",
            default_arguments={
                "--account_number": account_num,
                "--class": "GlueApp",
                "--environment_type": environment,
            },
            connections=[glue_connection.get_connection()],
            worker_type=_glue_alpha.WorkerType.G_1_X,
            worker_count=10,
        )

        _glue_alpha.Job(
            self,
            "glue-migration-prod-course-catalog",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset(
                    "migration_scripts/glue/glue-migration-prod-course-catalog.py"
                ),
            ),
            role=glue_role,
            job_name=environment + "-glue-migration-prod-course-catalog",
            default_arguments={
                "--account_number": account_num,
                "--class": "GlueApp",
                "--environment_type": environment,
            },
            connections=[glue_connection.get_connection()],
            worker_type=_glue_alpha.WorkerType.G_1_X,
            worker_count=10,
        )

        _glue_alpha.Job(
            self,
            "glue-migration-prod-dohclassified",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset(
                    "migration_scripts/glue/glue-migration-prod-dohclassified.py"
                ),
            ),
            role=glue_role,
            job_name=environment + "-glue-migration-prod-dohclassified",
            default_arguments={
                "--account_number": account_num,
                "--class": "GlueApp",
                "--environment_type": environment,
            },
            connections=[glue_connection.get_connection()],
            worker_type=_glue_alpha.WorkerType.G_1_X,
            worker_count=10,
        )

        _glue_alpha.Job(
            self,
            "glue-migration-prod-dohcompleted",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset(
                    "migration_scripts/glue/glue-migration-prod-dohcompleted.py"
                ),
            ),
            role=glue_role,
            job_name=environment + "-glue-migration-prod-dohcompleted",
            default_arguments={
                "--account_number": account_num,
                "--class": "GlueApp",
                "--environment_type": environment,
            },
            connections=[glue_connection.get_connection()],
            worker_type=_glue_alpha.WorkerType.G_1_X,
            worker_count=10,
        )

        _glue_alpha.Job(
            self,
            "glue-migration-prod-duedateextension",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset(
                    "migration_scripts/glue/glue-migration-prod-duedateextension.py"
                ),
            ),
            role=glue_role,
            job_name=environment + "-glue-migration-prod-duedateextension",
            default_arguments={
                "--account_number": account_num,
                "--class": "GlueApp",
                "--environment_type": environment,
            },
            connections=[glue_connection.get_connection()],
            worker_type=_glue_alpha.WorkerType.G_1_X,
            worker_count=10,
        )

        _glue_alpha.Job(
            self,
            "glue-migration-prod-employer",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset(
                    "migration_scripts/glue/glue-migration-prod-employer.py"
                ),
            ),
            role=glue_role,
            job_name=environment + "-glue-migration-prod-employer",
            default_arguments={
                "--account_number": account_num,
                "--class": "GlueApp",
                "--environment_type": environment,
            },
            connections=[glue_connection.get_connection()],
            worker_type=_glue_alpha.WorkerType.G_1_X,
            worker_count=10,
        )

        _glue_alpha.Job(
            self,
            "glue-migration-prod-employer-trust",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset(
                    "migration_scripts/glue/glue-migration-prod-employer-trust.py"
                ),
            ),
            role=glue_role,
            job_name=environment + "-glue-migration-prod-employer-trust",
            default_arguments={
                "--account_number": account_num,
                "--class": "GlueApp",
                "--environment_type": environment,
            },
            connections=[glue_connection.get_connection()],
            worker_type=_glue_alpha.WorkerType.G_1_X,
            worker_count=10,
        )

        _glue_alpha.Job(
            self,
            "glue-migration-prod-employmentrelationship",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset(
                    "migration_scripts/glue/glue-migration-prod-employmentrelationship.py"
                ),
            ),
            role=glue_role,
            job_name=environment + "-glue-migration-prod-employmentrelationship",
            default_arguments={
                "--account_number": account_num,
                "--class": "GlueApp",
                "--environment_type": environment,
            },
            connections=[glue_connection.get_connection()],
            worker_type=_glue_alpha.WorkerType.G_1_X,
            worker_count=10,
        )

        _glue_alpha.Job(
            self,
            "glue-migration-prod-exam",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset(
                    "migration_scripts/glue/glue-migration-prod-exam.py"
                ),
            ),
            role=glue_role,
            job_name=environment + "-glue-migration-prod-exam",
            default_arguments={
                "--account_number": account_num,
                "--class": "GlueApp",
                "--environment_type": environment,
            },
            connections=[glue_connection.get_connection()],
            worker_type=_glue_alpha.WorkerType.G_1_X,
            worker_count=10,
        )

        _glue_alpha.Job(
            self,
            "glue-migration-prod-instructor",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset(
                    "migration_scripts/glue/glue-migration-prod-instructor.py"
                ),
            ),
            role=glue_role,
            job_name=environment + "-glue-migration-prod-instructor",
            default_arguments={
                "--account_number": account_num,
                "--class": "GlueApp",
                "--environment_type": environment,
            },
            connections=[glue_connection.get_connection()],
            worker_type=_glue_alpha.WorkerType.G_1_X,
            worker_count=10,
        )

        _glue_alpha.Job(
            self,
            "glue-migration-prod-ojteligible",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset(
                    "migration_scripts/glue/glue-migration-prod-ojteligible.py"
                ),
            ),
            role=glue_role,
            job_name=environment + "-glue-migration-prod-ojteligible",
            default_arguments={
                "--account_number": account_num,
                "--class": "GlueApp",
                "--environment_type": environment,
            },
            connections=[glue_connection.get_connection()],
            worker_type=_glue_alpha.WorkerType.G_1_X,
            worker_count=10,
        )

        _glue_alpha.Job(
            self,
            "glue-migration-prod-person",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset(
                    "migration_scripts/glue/glue-migration-prod-person.py"
                ),
            ),
            role=glue_role,
            job_name=environment + "-glue-migration-prod-person",
            default_arguments={
                "--account_number": account_num,
                "--class": "GlueApp",
                "--environment_type": environment,
            },
            connections=[glue_connection.get_connection()],
            worker_type=_glue_alpha.WorkerType.G_1_X,
            worker_count=10,
        )

        _glue_alpha.Job(
            self,
            "glue-migration-prod-trainingrequirement",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset(
                    "migration_scripts/glue/glue-migration-prod-trainingrequirement.py"
                ),
            ),
            role=glue_role,
            job_name=environment + "-glue-migration-prod-trainingrequirement",
            default_arguments={
                "--account_number": account_num,
                "--class": "GlueApp",
                "--environment_type": environment,
            },
            connections=[glue_connection.get_connection()],
            worker_type=_glue_alpha.WorkerType.G_1_X,
            worker_count=10,
        )
        # Deprecated
        # _glue_alpha.Job(
        #     self,
        #     "glue-migration-prod-trainingtransfers",
        #     executable=_glue_alpha.JobExecutable.python_etl(
        #         glue_version=_glue_alpha.GlueVersion.V4_0,
        #         python_version=_glue_alpha.PythonVersion.THREE,
        #         script=_glue_alpha.Code.from_asset(
        #             "migration_scripts/glue/glue-migration-prod-trainingtransfers.py"
        #         ),
        #     ),
        #     role=glue_role,
        #     job_name=environment + "-glue-migration-prod-trainingtransfers",
        #     default_arguments={
        #         "--account_number": account_num,
        #         "--class": "GlueApp",
        #         "--environment_type": environment,
        #     },
        #     connections=[glue_connection.get_connection()],
        #     worker_type=_glue_alpha.WorkerType.G_1_X,
        #     worker_count=10,
        # )

        _glue_alpha.Job(
            self,
            "glue-migration-prod-transcript",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset(
                    "migration_scripts/glue/glue-migration-prod-transcript.py"
                ),
            ),
            role=glue_role,
            job_name=environment + "-glue-migration-prod-transcript",
            default_arguments={
                "--account_number": account_num,
                "--class": "GlueApp",
                "--environment_type": environment,
            },
            connections=[glue_connection.get_connection()],
            worker_type=_glue_alpha.WorkerType.G_1_X,
            worker_count=10,
        )

        _glue_alpha.Job(
            self,
            "glue-migration-raw-credential-delta",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset(
                    "migration_scripts/glue/glue-migration-raw-credential-delta.py"
                ),
            ),
            role=glue_role,
            job_name=environment + "-glue-migration-raw-credential-delta",
            default_arguments={
                "--account_number": account_num,
                "--class": "GlueApp",
                "--environment_type": environment,
            },
            connections=[glue_connection.get_connection()],
            worker_type=_glue_alpha.WorkerType.G_1_X,
            worker_count=10,
        )

        _glue_alpha.Job(
            self,
            "glue-migration-staging-idcrosswalk",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V3_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset(
                    "migration_scripts/glue/glue-migration-staging-idcrosswalk.py"
                ),
            ),
            role=glue_role,
            job_name=environment + "-glue-migration-staging-idcrosswalk",
            default_arguments={
                "--account_number": account_num,
                "--class": "GlueApp",
                "--additional-python-modules": cryptography_pythonlib,
                "--environment_type": environment,
            },
            connections=[glue_connection.get_connection()],
            worker_type=_glue_alpha.WorkerType.G_1_X,
            worker_count=10,
        )

        _glue_alpha.Job(
            self,
            "glue-migration-staging-personhistory",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset(
                    "migration_scripts/glue/glue-migration-staging-personhistory.py"
                ),
            ),
            role=glue_role,
            job_name=environment + "-glue-migration-staging-personhistory",
            default_arguments={
                "--account_number": account_num,
                "--class": "GlueApp",
                "--environment_type": environment,
            },
            connections=[glue_connection.get_connection()],
            worker_type=_glue_alpha.WorkerType.G_1_X,
            worker_count=10,
        )
        _glue_alpha.Job(
            self,
            "glue-migration-logs-transcript-archived",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset(
                    "migration_scripts/glue/glue-migration-logs-transcript-archived.py"
                ),
            ),
            role=glue_role,
            job_name=environment + "-glue-migration-logs-transcript-archived",
            default_arguments={
                "--account_number": account_num,
                "--class": "GlueApp",
                "--environment_type": environment,
            },
            connections=[glue_connection.get_connection()],
            worker_type=_glue_alpha.WorkerType.G_1_X,
            worker_count=10,
        )

        _glue_alpha.Job(
            self,
            "glue-process-clean-tables",
            executable=_glue_alpha.JobExecutable.python_shell(
                glue_version=_glue_alpha.GlueVersion.V1_0,
                python_version=_glue_alpha.PythonVersion.THREE_NINE,
                script=_glue_alpha.Code.from_asset(
                    "migration_scripts/glue/glue-process-clean-tables.py"
                ),
            ),
            role=glue_role,
            connections=[glue_connection.get_connection()],
            default_arguments={
                "--account_number": account_num,
                "--environment_type": environment,
            },
            job_name=environment + "-glue-process-clean-tables",
        )
        
        # Glue task : glue_task_0 is run it manually and verify all the tables vere truncated, 
        # Don't add to the state machine definition
        glue_task_0 = tasks.GlueStartJobRun(
            self,
            id="glue_process_clean_tables",
            glue_job_name=environment + "-glue-process-clean-tables",
        )

        # Glue task : glue_task_1 is run it manually if we want to update the coursecatalog provided by TP, 
        # Don't add to the state machine definition
        
        glue_task_1 = tasks.GlueStartJobRun(
            self,
            id="glue_coursecatalog_version_update",
            glue_job_name=environment + "-glue-coursecatalog-version-update",
        )

        glue_task_2 = tasks.GlueStartJobRun(
            self,
            id="glue_migration_logs_traineestatuslogs",
            glue_job_name=environment + "-glue-migration-logs-traineestatuslogs",
        )

        glue_task_3 = tasks.GlueStartJobRun(
            self,
            id="glue_migration_prod_branch",
            glue_job_name=environment + "-glue-migration-prod-branch",
        )

        glue_task_4 = tasks.GlueStartJobRun(
            self,
            id="glue_migration_prod_course_catalog",
            glue_job_name=environment + "-glue-migration-prod-course-catalog",
        )

        glue_task_5 = tasks.GlueStartJobRun(
            self,
            id="glue_migration_prod_dohclassified",
            glue_job_name=environment + "-glue-migration-prod-dohclassified",
        )

        glue_task_6 = tasks.GlueStartJobRun(
            self,
            id="glue_migration_prod_dohcompleted",
            glue_job_name=environment + "-glue-migration-prod-dohcompleted",
        )

        glue_task_7 = tasks.GlueStartJobRun(
            self,
            id="glue_migration_prod_duedateextension",
            glue_job_name=environment + "-glue-migration-prod-duedateextension",
        )

        glue_task_8 = tasks.GlueStartJobRun(
            self,
            id="glue_migration_prod_employer",
            glue_job_name=environment + "-glue-migration-prod-employer",
        )

        glue_task_9 = tasks.GlueStartJobRun(
            self,
            id="glue_migration_prod_employer_trust",
            glue_job_name=environment + "-glue-migration-prod-employer-trust",
        )

        glue_task_10 = tasks.GlueStartJobRun(
            self,
            id="glue_migration_prod_employmentrelationship",
            glue_job_name=environment + "-glue-migration-prod-employmentrelationship",
        )

        glue_task_11 = tasks.GlueStartJobRun(
            self,
            id="glue_migration_prod_exam",
            glue_job_name=environment + "-glue-migration-prod-exam",
        )

        glue_task_12 = tasks.GlueStartJobRun(
            self,
            id="glue_migration_prod_instructor",
            glue_job_name=environment + "-glue-migration-prod-instructor",
        )

        glue_task_13 = tasks.GlueStartJobRun(
            self,
            id="glue_migration_prod_ojteligible",
            glue_job_name=environment + "-glue-migration-prod-ojteligible",
        )

        glue_task_14 = tasks.GlueStartJobRun(
            self,
            id="glue_migration_prod_person",
            glue_job_name=environment + "-glue-migration-prod-person",
        )

        glue_task_15 = tasks.GlueStartJobRun(
            self,
            id="glue_migration_logs_transcript_archived",
            glue_job_name=environment + "-glue-migration-logs-transcript-archived",
        )

        glue_task_16 = tasks.GlueStartJobRun(
            self,
            id="glue_migration_prod_trainingrequirement",
            glue_job_name=environment + "-glue-migration-prod-trainingrequirement",
        )

        # Deprecated
        # glue_task_17 = tasks.GlueStartJobRun(
        #     self,
        #     id="glue_migration_prod_trainingtransfers",
        #     glue_job_name=environment + "-glue-migration-prod-trainingtransfers",
        # )

        glue_task_18 = tasks.GlueStartJobRun(
            self,
            id="glue_migration_prod_transcript",
            glue_job_name=environment + "-glue-migration-prod-transcript",
        )

        glue_task_19 = tasks.GlueStartJobRun(
            self,
            id="glue_migration_raw_credential_delta",
            glue_job_name=environment + "-glue-migration-raw-credential-delta",
        )

        glue_task_20 = tasks.GlueStartJobRun(
            self,
            id="glue_migration_staging_idcrosswalk",
            glue_job_name=environment + "-glue-migration-staging-idcrosswalk",
        )

        glue_task_21 = tasks.GlueStartJobRun(
            self,
            id="glue_migration_staging_personhistory",
            glue_job_name=environment + "-glue-migration-staging-personhistory",
        )

        

        machine_definition = (
            sfn.Parallel(self, id="invoke-all-migration-parallel-jobs")
            .branch(glue_task_2)
            .branch(glue_task_3)
            .branch(glue_task_4)
            .branch(glue_task_5)
            .branch(glue_task_6)
            .branch(glue_task_7)
            .branch(glue_task_8)
            .branch(glue_task_9)
            .branch(glue_task_10)
            .branch(glue_task_11)
            .branch(glue_task_12)
            .branch(glue_task_13)
            .branch(glue_task_14)
            .branch(glue_task_15)
            .branch(glue_task_16)
            .branch(glue_task_18)
            .branch(glue_task_19)
            .branch(glue_task_20)
            .branch(glue_task_21)
        )

        sfn.StateMachine(
            self,
            "migration_scripts_workflow_stack",
            definition=machine_definition,
            state_machine_name=environment + "-migration_scripts_workflow_stack",
        )
