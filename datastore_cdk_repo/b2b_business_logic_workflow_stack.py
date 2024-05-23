from constructs import Construct
from aws_cdk import (
    Stack,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as tasks,
    aws_iam,
    aws_glue_alpha as _glue_alpha,
)
from .glue_connection import GlueConnection


class B2BBusinesslogicStack(Stack):
    def __init__(
        self, scope: Construct, id: str, environment: str, account_num: str, **kwargs
    ) -> None:
        super().__init__(scope, id, **kwargs)

        glue_role = aws_iam.Role.from_role_name(
            self, "GlueRole", "role-p-glue-data-pipelines"
        )

        if environment == "dev":
            glue_connection = GlueConnection(self, "glue_connection", "rdsconnect")
        else:
            glue_connection = GlueConnection(
                self, "glue_connection", "connection-uw2-p-seiubg-prod-b2bds"
            )

        # Defines an AWS Lambda resource
        job = _glue_alpha.Job(
            self,
            "glue-personmastering",
            executable=_glue_alpha.JobExecutable.python_shell(
                glue_version=_glue_alpha.GlueVersion.V1_0,
                python_version=_glue_alpha.PythonVersion.THREE_NINE,
                script=_glue_alpha.Code.from_asset(
                    "b2b_business_logic/glue/glue-personmastering.py"
                ),
            ),
            role=glue_role,
            connections=[glue_connection.get_connection()],
            default_arguments={
                "--account_number": account_num,
                "--environment_type": environment
                },
            job_name=environment + "-glue-personmastering",
        )

        job = _glue_alpha.Job(
            self,
            "glue-clean-agency-dex-sourcekey",
            executable=_glue_alpha.JobExecutable.python_shell(
                glue_version=_glue_alpha.GlueVersion.V1_0,
                python_version=_glue_alpha.PythonVersion.THREE_NINE,
                script=_glue_alpha.Code.from_asset(
                    "b2b_business_logic/glue/glue-clean-agency-dex-sourcekey.py"
                ),
            ),
            role=glue_role,
            connections=[glue_connection.get_connection()],
            default_arguments={
                "--account_number": account_num,
                "--environment_type": environment,
            },
            job_name=environment + "-glue-clean-agency-dex-sourcekey",
        )

        job = _glue_alpha.Job(
            self,
            "glue-clean-agency-sourcekey",
            executable=_glue_alpha.JobExecutable.python_shell(
                glue_version=_glue_alpha.GlueVersion.V1_0,
                python_version=_glue_alpha.PythonVersion.THREE_NINE,
                script=_glue_alpha.Code.from_asset(
                    "b2b_business_logic/glue/glue-clean-agency-sourcekey.py"
                ),
            ),
            role=glue_role,
            connections=[glue_connection.get_connection()],
            default_arguments={
                "--account_number": account_num,
                "--environment_type": environment,
            },
            job_name=environment + "-glue-clean-agency-sourcekey",
        )

        job = _glue_alpha.Job(
            self,
            "glue-clean-quarantine-agency-terminated",
            executable=_glue_alpha.JobExecutable.python_shell(
                glue_version=_glue_alpha.GlueVersion.V1_0,
                python_version=_glue_alpha.PythonVersion.THREE_NINE,
                script=_glue_alpha.Code.from_asset(
                    "b2b_business_logic/glue/glue-clean-quarantine-agency-terminated.py"
                ),
            ),
            role=glue_role,
            connections=[glue_connection.get_connection()],
            default_arguments={
                "--account_number": account_num,
                "--environment_type": environment,
            },
            job_name=environment + "-glue-clean-quarantine-agency-terminated",
        )

        job = _glue_alpha.Job(
            self,
            "glue-clean-person-quarantine",
            executable=_glue_alpha.JobExecutable.python_shell(
                glue_version=_glue_alpha.GlueVersion.V1_0,
                python_version=_glue_alpha.PythonVersion.THREE_NINE,
                script=_glue_alpha.Code.from_asset(
                    "b2b_business_logic/glue/glue-clean-person-quarantine.py"
                ),
            ),
            role=glue_role,
            connections=[glue_connection.get_connection()],
            default_arguments={
                "--account_number": account_num,
                "--environment_type": environment,
            },
            job_name=environment + "-glue-clean-person-quarantine",
        )

        job = _glue_alpha.Job(
            self,
            "glue-person-quarantine-to-s3",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset(
                    "b2b_business_logic/glue/glue-person-quarantine-to-s3.py"
                ),
            ),
            role=glue_role,
            connections=[glue_connection.get_connection()],
            default_arguments={
                "--account_number": account_num,
                "--environment_type": environment,
            },
            job_name=environment + "-glue-person-quarantine-to-s3",
        )

        job = _glue_alpha.Job(
            self,
            "glue-update-earliest-hire-tracking-workcategory",
            executable=_glue_alpha.JobExecutable.python_shell(
                glue_version=_glue_alpha.GlueVersion.V1_0,
                python_version=_glue_alpha.PythonVersion.THREE_NINE,
                script=_glue_alpha.Code.from_asset(
                    "b2b_business_logic/glue/glue-update-earliest-hire-tracking-workcategory.py"
                ),
            ),
            role=glue_role,
            connections=[glue_connection.get_connection()],
            default_arguments={
                "--account_number": account_num,
                "--environment_type": environment,
            },
            job_name=environment + "-glue-update-earliest-hire-tracking-workcategory",
        )
        # need to check this job if exists--------------------
        job = _glue_alpha.Job(
            self,
            "glue-primarycredential-process",
            executable=_glue_alpha.JobExecutable.python_shell(
                glue_version=_glue_alpha.GlueVersion.V1_0,
                python_version=_glue_alpha.PythonVersion.THREE_NINE,
                script=_glue_alpha.Code.from_asset(
                    "b2b_business_logic/glue/glue-primarycredential-process.py"
                ),
            ),
            role=glue_role,
            connections=[glue_connection.get_connection()],
            default_arguments={
                "--account_number": account_num,
                "--environment_type": environment,
            },
            job_name=environment + "-glue-primarycredential-process",
        )

        job = _glue_alpha.Job(
            self,
            "glue-update-prod-person-with-primarycredential",
            executable=_glue_alpha.JobExecutable.python_shell(
                glue_version=_glue_alpha.GlueVersion.V1_0,
                python_version=_glue_alpha.PythonVersion.THREE_NINE,
                script=_glue_alpha.Code.from_asset(
                    "b2b_business_logic/glue/glue-update-prod-person-with-primarycredential.py"
                ),
            ),
            role=glue_role,
            connections=[glue_connection.get_connection()],
            default_arguments={
                "--account_number": account_num,
                "--environment_type": environment,
            },
            job_name=environment + "-glue-update-prod-person-with-primarycredential",
        )

        job = _glue_alpha.Job(
            self,
            "glue-doh-duedate",
            executable=_glue_alpha.JobExecutable.python_shell(
                glue_version=_glue_alpha.GlueVersion.V1_0,
                python_version=_glue_alpha.PythonVersion.THREE_NINE,
                script=_glue_alpha.Code.from_asset(
                    "b2b_business_logic/glue/glue-doh-duedate.py"
                ),
            ),
            role=glue_role,
            connections=[glue_connection.get_connection()],
            default_arguments={
                "--account_number": account_num,
                "--environment_type": environment,
            },
            job_name=environment + "-glue-doh-duedate",
        )

        job = _glue_alpha.Job(
            self,
            "glue-credentials-delta-to-Prodcredentials",
            executable=_glue_alpha.JobExecutable.python_etl(
                glue_version=_glue_alpha.GlueVersion.V4_0,
                python_version=_glue_alpha.PythonVersion.THREE,
                script=_glue_alpha.Code.from_asset(
                    "b2b_business_logic/glue/glue-credentials-delta-to-Prodcredentials.py"
                ),
            ),
            role=glue_role,
            connections=[glue_connection.get_connection()],
            default_arguments={
                "--account_number": account_num,
                "--environment_type": environment,
            },
            job_name=environment + "-glue-credentials-delta-to-Prodcredentials",
        )

        # Defines tasks for lambda and glue jobs
        glue_task1 = tasks.GlueStartJobRun(
            self,
            id="glue_personmastering",
            glue_job_name=environment + "-glue-personmastering",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB,
        )

        glue_task2 = tasks.GlueStartJobRun(
            self,
            id="glue_clean_agency_dex_sourcekey",
            glue_job_name=environment + "-glue-clean-agency-dex-sourcekey",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB,
        )

        glue_task3 = tasks.GlueStartJobRun(
            self,
            id="glue_clean_agency_sourcekey",
            glue_job_name=environment + "-glue-clean-agency-sourcekey",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB,
        )

        glue_task4 = tasks.GlueStartJobRun(
            self,
            id="glue_cleaningquarantineagencyterm",
            glue_job_name=environment + "-glue-clean-quarantine-agency-terminated",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB,
        )

        glue_task5 = tasks.GlueStartJobRun(
            self,
            id="glue_clean_person_quarantine",
            glue_job_name=environment + "-glue-clean-person-quarantine",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB,
        )

        glue_task6 = tasks.GlueStartJobRun(
            self,
            id="glue_personquarantine_to_s3",
            glue_job_name=environment + "-glue-person-quarantine-to-s3",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB,
        )

        glue_task7 = tasks.GlueStartJobRun(
            self,
            id="glue_updateearliest_hire_tracking_workcategory",
            glue_job_name=environment
            + "-glue-update-earliest-hire-tracking-workcategory",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB,
        )

        glue_task8 = tasks.GlueStartJobRun(
            self,
            id="glue_primarycredential_process",
            glue_job_name=environment + "-glue-primarycredential-process",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB,
        )

        glue_task9 = tasks.GlueStartJobRun(
            self,
            id="glue_update_prod_person_withprimarycredential",
            glue_job_name=environment
            + "-glue-update-prod-person-with-primarycredential",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB,
        )

        glue_task10 = tasks.GlueStartJobRun(
            self,
            id="glue_credentials_delta_to_Prodcredentials",
            glue_job_name=environment + "-glue-credentials-delta-to-Prodcredentials",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB,
        )

        glue_task11 = tasks.GlueStartJobRun(
            self,
            id="glue_doh_duedate",
            glue_job_name=environment + "-glue-doh-duedate",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB,
        )

        definition1 = glue_task1.next(
            glue_task2.next(
                glue_task3.next(
                    glue_task4.next(
                        glue_task5.next(
                            glue_task6.next(
                                glue_task7.next(
                                    glue_task8.next(
                                        glue_task9.next(glue_task10.next(glue_task11))
                                    )
                                )
                            )
                        )
                    )
                )
            )
        )

        # define state machine
        sfn.StateMachine(
            self,
            "StateMachine_businesslogic",
            definition=definition1,
            state_machine_name=environment + "-b2b-business-logic-workflow",
        )
