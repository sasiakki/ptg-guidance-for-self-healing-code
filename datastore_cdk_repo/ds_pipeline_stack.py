from constructs import Construct
from aws_cdk import (
    Stack,
    aws_codecommit as codecommit,
    pipelines as pipelines,
    aws_sns as sns,
    aws_sns_subscriptions as subscriptions,
    aws_iam as iam,
    aws_lambda as _lambda,
    aws_sns as sns,
    aws_sns_subscriptions as subscriptions,
    aws_codepipeline_actions as actions,
    aws_codebuild as codebuild,
    triggers,
    aws_iam,
    Duration as duration,
    aws_ec2,
)



import aws_cdk as cdk
from aws_cdk.pipelines import CodePipeline, CodePipelineSource, ShellStep
from aws_cdk.pipelines import ManualApprovalStep
from constructs import Construct
from aws_cdk import aws_stepfunctions as sfn
from aws_cdk import aws_stepfunctions_tasks as tasks
import boto3

from bin.ec2_utils import EC2Utils

from datastore_cdk_repo.ds_pipeline_stage import B2BBusinesslogicPipelineStage
from datastore_cdk_repo.ds_pipeline_stage import BenefitsContinuationPipelineStage
from datastore_cdk_repo.ds_pipeline_stage import CDWAPipelineStage
from datastore_cdk_repo.ds_pipeline_stage import CredentialPipelineStage
from datastore_cdk_repo.ds_pipeline_stage import DSCheckIteratorPipelineStage
from datastore_cdk_repo.ds_pipeline_stage import DOHPipelineStage
from datastore_cdk_repo.ds_pipeline_stage import ExamPipelineStage
from datastore_cdk_repo.ds_pipeline_stage import QualtricsPipelineStage
from datastore_cdk_repo.ds_pipeline_stage import QuarantinePipelineStage
from datastore_cdk_repo.ds_pipeline_stage import ApitoS3PipelineStage
from datastore_cdk_repo.ds_pipeline_stage import SalesforcePipelineStage
from datastore_cdk_repo.ds_pipeline_stage import TrainingCompletionsPipelineStage
from datastore_cdk_repo.ds_pipeline_stage import TrainingTransfersPipelineStage
from datastore_cdk_repo.ds_pipeline_stage import E2EPipelineStage
from datastore_cdk_repo.ds_pipeline_stage import CdwaSftpPipelineStage
from datastore_cdk_repo.ds_pipeline_stage import ApiandSFTPtoS3PipelineStage
from datastore_cdk_repo.ds_pipeline_stage import DohSftpPipelineStage
from datastore_cdk_repo.ds_pipeline_stage import DohOutboundPipelineStage
from datastore_cdk_repo.ds_pipeline_stage import DshsOutboundPipelineStage
from datastore_cdk_repo.ds_pipeline_stage import CDWAOutboundPipelineStage
from datastore_cdk_repo.ds_pipeline_stage import DWHOutboundPipelineStage
from datastore_cdk_repo.ds_pipeline_stage import DoceboOutboundPipelineStage
from datastore_cdk_repo.ds_pipeline_stage import RDSPipelineStage
from datastore_cdk_repo.ds_pipeline_stage import EligibilityCDKSAMBuildStage
from datastore_cdk_repo.ds_pipeline_stage import MigrationScriptsPipelineStage
from datastore_cdk_repo.rds_deployment_stack import RDSStack
from datastore_cdk_repo.ds_pipeline_stage import TranscriptsRetractionStage
from datastore_cdk_repo.ds_pipeline_stage import DshsSftpPipelineStage
from datastore_cdk_repo.ds_pipeline_stage import EligibilityCalculationWorkflowStage


class DSPipelineStack(Stack):
    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        repository_name = "datastore-cdk-repo-devops"
        repository = codecommit.Repository.from_repository_name(
            self, "datastore-cdk-repo-devops", repository_name
        )
        pipeline = pipelines.CodePipeline(
            self,
            "Pipeline",
            cross_account_keys=True,
            pipeline_name="DSPipeline",
            synth=pipelines.ShellStep(
                "Synth",
                input=pipelines.CodePipelineSource.code_commit(
                    repository, "main"
                ),
                commands=[
                    "npm install -g aws-cdk",  # Installs the cdk cli on Codebuild
                    "npm install typescript --force",
                    "pip install -r requirements.txt",  # Instructs Codebuild to install required packages
                    "pip install aws_cdk.aws_glue_alpha",
                    "cdk synth",
                ],
            ),
        )

        envs = {"dev": "529350069891", "stage": "571950455257", "prod": "259367569391"}
        aws_region = "us-west-2"
        for envType, account_num in envs.items():
            deploy_b2b_business = B2BBusinesslogicPipelineStage(
                self,
                f"{envType}-deploy-b2b-business",
                envType,
                account_num,
                env=cdk.Environment(account=account_num, region=aws_region),
            )

            deploy_benefits = BenefitsContinuationPipelineStage(
                self,
                f"{envType}-deploy-benefits",
                envType,
                account_num,
                env=cdk.Environment(account=account_num, region=aws_region),
            )

            deploy_cdwa = CDWAPipelineStage(
                self,
                f"{envType}-deploy-cdwa",
                envType,
                account_num,
                env=cdk.Environment(account=account_num, region=aws_region),
            )

            deploy_credentials = CredentialPipelineStage(
                self,
                f"{envType}-deploy-credentials",
                envType,
                account_num,
                env=cdk.Environment(account=account_num, region=aws_region),
            )

            deploy_ds_s3_iterator = DSCheckIteratorPipelineStage(
                self,
                f"{envType}-deploy-ds-s3-iterator",
                envType,
                account_num,
                env=cdk.Environment(account=account_num, region=aws_region),
            )

            deploy_doh = DOHPipelineStage(
                self,
                f"{envType}-deploy-doh",
                envType,
                account_num,
                env=cdk.Environment(account=account_num, region=aws_region),
            )

            deploy_exam = ExamPipelineStage(
                self,
                f"{envType}-deploy-exam",
                envType,
                account_num,
                env=cdk.Environment(account=account_num, region=aws_region),
            )

            deploy_qualtrics = QualtricsPipelineStage(
                self,
                f"{envType}-deploy-qualtrics",
                envType,
                account_num,
                env=cdk.Environment(account=account_num, region=aws_region),
            )

            deploy_quarantine = QuarantinePipelineStage(
                self,
                f"{envType}-deploy-quarantine",
                envType,
                account_num,
                env=cdk.Environment(account=account_num, region=aws_region),
            )

            deploy_api_to_s3 = ApitoS3PipelineStage(
                self,
                f"{envType}-deploy-api-to-s3i",
                envType,
                account_num,
                env=cdk.Environment(account=account_num, region=aws_region),
            )

            deploy_api_and_sftp_to_s3 = ApiandSFTPtoS3PipelineStage(
                self,
                f"{envType}-deploy-api-and-sftp-to-s3",
                envType,
                account_num,
                env=cdk.Environment(account=account_num, region=aws_region),
            )

            deploy_dshs_sftp = DshsSftpPipelineStage(
                self,
                f"{envType}-deploy-dshs-sftp",
                envType,
                account_num,
                env=cdk.Environment(account=account_num, region=aws_region),
            )

            

            deploy_salesforce = SalesforcePipelineStage(
                self,
                f"{envType}-deploy-salesforce",
                envType,
                account_num,
                env=cdk.Environment(account=account_num, region=aws_region),
            )

            deploy_training_completion = TrainingCompletionsPipelineStage(
                self,
                f"{envType}-deploy-training-completion",
                envType,
                account_num,
                env=cdk.Environment(account=account_num, region=aws_region),
            )

            deploy_training_transfer = TrainingTransfersPipelineStage(
                self,
                f"{envType}-deploy-training-transfers",
                envType,
                account_num,
                env=cdk.Environment(account=account_num, region=aws_region),
            )

            deploy_cdwa_sftp = CdwaSftpPipelineStage(
                self,
                f"{envType}-deploy-cdwa-sftp",
                envType,
                account_num,
                env=cdk.Environment(account=account_num, region=aws_region),
            )

            deploy_doh_sftp = DohSftpPipelineStage(
                self,
                f"{envType}-deploy-doh-sftp",
                envType,
                account_num,
                env=cdk.Environment(account=account_num, region=aws_region),
            )


            deploy_transcripts_retraction = TranscriptsRetractionStage(
                self,
                f"{envType}-deploy-transcripts-retraction",
                envType,
                account_num,
                env=cdk.Environment(account=account_num, region="us-west-2"),
            )

            e2e_stack = E2EPipelineStage(
                self,
                f"{envType}-e2e-stack",
                envType,
                account_num,
                env=cdk.Environment(account=account_num, region=aws_region),
            )

            deploy_doh_outbound = DohOutboundPipelineStage(
                self,
                f"{envType}-deploy-doh-outbound",
                envType,
                account_num,
                env=cdk.Environment(account=account_num, region=aws_region),
            )

            deploy_dshs_outbound = DshsOutboundPipelineStage(
                self,
                f"{envType}-deploy-dshs-outbound",
                envType,
                account_num,
                env=cdk.Environment(account=account_num, region=aws_region),
            )

            deploy_cdwa_outbound = CDWAOutboundPipelineStage(
                self,
                f"{envType}-deploy-cdwa-outbound",
                envType,
                account_num,
                env=cdk.Environment(account=account_num, region=aws_region),
            )

            deploy_dwh_outbound = DWHOutboundPipelineStage(
                self,
                f"{envType}-deploy-dwh-outbound",
                envType,
                account_num,
                env=cdk.Environment(account=account_num, region=aws_region),
            )

            deploy_docebo_outbound = DoceboOutboundPipelineStage(
                self,
                f"{envType}-deploy-docebo-outbound",
                envType,
                account_num,
                env=cdk.Environment(account=account_num, region=aws_region),
            )

            # deploy_rds = RDSPipelineStage(
            #     self,
            #     f"{envType}-deploy-rds",
            #     envType,
            #     account_num,
            #     env=cdk.Environment(account=account_num, region=aws_region),
            # )

            deploy_eligibility_sam = EligibilityCDKSAMBuildStage(
                self,
                f"{envType}-deploy-eligibility-sam",
                envType,
                account_num,
                env=cdk.Environment(account=account_num, region=aws_region),
            )

            deploy_migration_scripts = MigrationScriptsPipelineStage(
                self,
                f"{envType}-deploy-migration-scripts-jobs",
                envType,
                account_num,
                env=cdk.Environment(account=account_num, region=aws_region),
            )

            deploy_eligibility_calculation_workflow = EligibilityCalculationWorkflowStage(
                self,
                f"{envType}-deploy-eligibility-calculation-workflow",
                envType,
                account_num,
                env=cdk.Environment(account=account_num, region=aws_region),
            )
            
            # if envType == "dev":
            #     lambda_vpc = None
            #     lambda_security_group = None
            # else:
            #     ec2_utils = EC2Utils("us-west-2", account_num)
            #     (
            #     vpc_id_from_boto,
            #     subnet_ids,
            #     route_table_ids,
            #     sg_group_id,
            #     sg_group_name,
            #     ) = ec2_utils.get_vpc_subnets_and_security_group(envType)

            #     lambda_vpc = aws_ec2.Vpc.from_vpc_attributes(
            #         self,
            #         "lambda_vpc",
            #         vpc_id=vpc_id_from_boto,
            #         region="us-west-2",
            #         availability_zones=[
            #             "us-west-2a",
            #             "us-west-2b",
            #             "us-west-2c",
            #             "us-west-2d",
            #         ],
            #         private_subnet_ids=subnet_ids,
            #         private_subnet_route_table_ids=route_table_ids,
            #     )
            #     lambda_security_group_object = (
            #         aws_ec2.SecurityGroup.from_security_group_id(
            #             self, sg_group_name, sg_group_id
            #         )
            #     )
            #     lambda_security_group = [lambda_security_group_object]

            # lambda_function = _lambda.Function(
            #     self,
            #     f"{envType}-lambda-execute-db-scripts",
            #     runtime=_lambda.Runtime.PYTHON_3_9,
            #     code=_lambda.Code.from_asset(
            #         "rds-workflow/lambda/lambda-execute-db-scripts/"
            #     ),
            #     handler="lambda_function.lambda_handler",
            #     function_name=envType + "-lambda-execute-db-scripts",
            #     role=aws_iam.Role.from_role_name(
            #         self, f"{envType}-LambdaRoleDBScripts", "role-d-lambda-execute"
            #     ),
            #     timeout=duration.minutes(15),
            #     environment={
            #         "account_number": account_num,
            #         "environment_type": envType,
            #     },
            #     vpc=lambda_vpc,
            #     security_groups=lambda_security_group,
            # )
            # triggers.Trigger(self, f"{envType}-MyTrigger", handler=lambda_function)

            if envType == "dev":
                wave = pipeline.add_wave(f"{envType}-deployment-parallel")
            else:
                wave = pipeline.add_wave(
                    f"{envType}-deployment-parallel",
                    pre=[pipelines.ManualApprovalStep(f"promote-to-{envType}")],
                )
            wave.add_stage(deploy_b2b_business)
            wave.add_stage(deploy_benefits)
            wave.add_stage(deploy_cdwa)
            wave.add_stage(deploy_credentials)
            wave.add_stage(deploy_ds_s3_iterator)
            wave.add_stage(deploy_doh)
            wave.add_stage(deploy_exam)
            wave.add_stage(deploy_qualtrics)
            wave.add_stage(deploy_quarantine)
            wave.add_stage(deploy_api_to_s3)
            wave.add_stage(deploy_api_and_sftp_to_s3)
            wave.add_stage(deploy_salesforce)
            wave.add_stage(deploy_training_completion)
            wave.add_stage(deploy_training_transfer)
            wave.add_stage(deploy_cdwa_sftp)
            wave.add_stage(deploy_doh_sftp)
            wave.add_stage(deploy_dshs_sftp)
            wave.add_stage(deploy_doh_outbound)
            wave.add_stage(deploy_dshs_outbound)
            wave.add_stage(deploy_cdwa_outbound)
            wave.add_stage(deploy_dwh_outbound)
            wave.add_stage(deploy_docebo_outbound)
            #wave.add_stage(deploy_rds)
            wave.add_stage(deploy_eligibility_sam)
            wave.add_stage(deploy_migration_scripts)
            wave.add_stage(deploy_transcripts_retraction)
            wave.add_stage(deploy_eligibility_calculation_workflow)
            deploy_e2e = pipeline.add_stage(e2e_stack)
            
