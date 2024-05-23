import builtins
import typing
from constructs import Construct
from aws_cdk import (
    Environment,
    PermissionsBoundary,
    Stage
)
from .b2b_business_logic_workflow_stack import B2BBusinesslogicStack
from .benefits_continuation_workflow_stack import BenefitsContinuationStack
from .cdwa_workflow_stack import CDWAWorkflowStack
from .credential_workflow_stack import CredentialWorkflowStack
from .datastore_s3_check_iterator_workflow_stack import DSCheckIteratorWorkflowStack
from .doh_workflow_stack import DOHWorkflowStack
from .exam_workflow_stack import ExamWorkflowStack
from .qualtrics_workflow_stack import QualtricsWorkflowStack
from .quarantine_workflow_stack import QuarantineWorkflowStack
from .salesforce_outbound_workflow_stack import SalesforceoutboundWorkflowStack
from .training_completions_workflow_stack import TrainingCompletionsWorkflowStack
from .training_transfers_workflow_stack import TrainingTransfersWorkflowStack
from .e2e_workflow_stack import E2EWorkflowStack
from .doh_sftp_workflow_stack import DohSftpWorkflowstack
from .cdwa_sftp_workflow_stack import CdwaSftpWorkflowstack
from .dshs_sftp_workflow_stack import DshsSftpWorkflowstack
from .doh_outbound_workflow_stack import DohOutboundWorkflowStack
from .dwh_outbound_workflow_stack import DWHOutboundWorkflowStack
from .cdwa_outbound_workflow_stack import CDWAOutboundWorkflowStack
from .dshs_outbound_workflow_stack import DshsOutboundWorkflowStack
from .docebo_outbound_workflow_stack import DoceboOutboundWorkflowStack
from .rds_deployment_stack import RDSStack
from .eligibility_sam_build import EligibilityCDKSAMBuild
from .migration_scripts_workflow_stack import MigrationWorkflowStack
from .api_and_sftp_to_s3_workflow_stack import ApiandSftpToS3WorkflowStack
from .api_to_s3_workflow_stack import ApiToS3WorkflowStack
from .transcripts_retraction_workflow_stack import TranscriptRetractionsWorkflowStack
from .eligibility_workflow_stack import EligibilityCalculationWorkflowStack

class BenefitsContinuationPipelineStage(Stage):

    def __init__(self, scope: Construct, id: str, environment: str, account_num: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        service = BenefitsContinuationStack(self, 'benefits-continuation-workflow', environment, account_num)

class B2BBusinesslogicPipelineStage(Stage):

    def __init__(self, scope: Construct, id: str, environment: str, account_num: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        service = B2BBusinesslogicStack(self, 'b2b-business-logic-workflow', environment, account_num)

class CDWAPipelineStage(Stage):

    def __init__(self, scope: Construct, id: str, environment: str, account_num: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        service = CDWAWorkflowStack(self, 'cdwa-workflow-stack', environment, account_num)

class CredentialPipelineStage(Stage):

    def __init__(self, scope: Construct, id: str, environment: str, account_num: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        service = CredentialWorkflowStack(self, 'credential-workflow-stack', environment, account_num)

class DshsSftpPipelineStage(Stage):

    def __init__(self, scope: Construct, id: str, environment: str, account_num: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        service = DshsSftpWorkflowstack(self, 'dshs-sftp-workflow-stack', environment, account_num)

class DSCheckIteratorPipelineStage(Stage):

    def __init__(self, scope: Construct, id: str, environment: str, account_num: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        service = DSCheckIteratorWorkflowStack(self, 'datastore-s3-check-iterator-workflow-stack', environment, account_num)

class DOHPipelineStage(Stage):

    def __init__(self, scope: Construct, id: str, environment: str, account_num: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        service = DOHWorkflowStack(self, 'doh-workflow-stack', environment, account_num)

class ExamPipelineStage(Stage):

    def __init__(self, scope: Construct, id: str, environment: str, account_num: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        service = ExamWorkflowStack(self, 'exam-workflow-stack', environment, account_num)

class QualtricsPipelineStage(Stage):

    def __init__(self, scope: Construct, id: str, environment: str, account_num: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        service = QualtricsWorkflowStack(self, 'qualtrics-workflow-stack', environment, account_num)

class QuarantinePipelineStage(Stage):

    def __init__(self, scope: Construct, id: str, environment: str, account_num: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        service = QuarantineWorkflowStack(self, 'quarantine-workflow-stack', environment, account_num)

class ApitoS3PipelineStage(Stage):

    def __init__(self, scope: Construct, id: str, environment: str, account_num: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        service = ApiToS3WorkflowStack(self, 'raw-to-s3-api-workflow-stack', environment, account_num)

class ApiandSFTPtoS3PipelineStage(Stage):

    def __init__(self, scope: Construct, id: str, environment: str, account_num:str, **kwargs):
        super().__init__(scope, id, **kwargs)

        service = ApiandSftpToS3WorkflowStack(self, 'raw-to-s3-sftp-api-workflow-stack', environment, account_num)

class SalesforcePipelineStage(Stage):

    def __init__(self, scope: Construct, id: str, environment: str, account_num: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        service = SalesforceoutboundWorkflowStack(self, 'salesforce-outbound-workflow-stack', environment, account_num)

class TrainingCompletionsPipelineStage(Stage):

    def __init__(self, scope: Construct, id: str, environment: str, account_num: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        service = TrainingCompletionsWorkflowStack(self, 'training-completions-workflow-stack', environment, account_num)

class TrainingTransfersPipelineStage(Stage):

    def __init__(self, scope: Construct, id: str, environment: str, account_num: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        service = TrainingTransfersWorkflowStack(self, 'training-transfers-workflow-stack', environment, account_num)

class CdwaSftpPipelineStage(Stage):

    def __init__(self, scope: Construct, id: str, environment: str, account_num: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        service = CdwaSftpWorkflowstack(self, 'cdwa-sftp-workflow-stack', environment, account_num)

class DohSftpPipelineStage(Stage):

    def __init__(self, scope: Construct, id: str, environment: str, account_num: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        service = DohSftpWorkflowstack(self, 'doh-sftp-workflow-stack', environment, account_num)


class E2EPipelineStage(Stage):
    def __init__(self, scope: Construct, id: str, environment: str, account_num: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        service = E2EWorkflowStack(self, 'e2e-workflow-stack', environment, account_num)

class DohOutboundPipelineStage(Stage):
    def __init__(self, scope: Construct, id: str, environment: str, account_num: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        service = DohOutboundWorkflowStack(self, 'doh-outbound-workflow-stack', environment, account_num)

class CDWAOutboundPipelineStage(Stage):
    def __init__(self, scope: Construct, id: str, environment: str, account_num: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        service = CDWAOutboundWorkflowStack(self, 'cdwa-outbound-workflow-stack', environment, account_num)

class DshsOutboundPipelineStage(Stage):
    def __init__(self, scope: Construct, id: str, environment: str, account_num: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        service = DshsOutboundWorkflowStack(self, 'dshs-outbound-workflow-stack', environment, account_num)

class DWHOutboundPipelineStage(Stage):
    def __init__(self, scope: Construct, id: str, environment: str, account_num: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        service = DWHOutboundWorkflowStack(self, 'dwh-outbound-workflow-stack', environment, account_num)

class DoceboOutboundPipelineStage(Stage):
    def __init__(self, scope: Construct, id: str, environment: str, account_num: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        service = DoceboOutboundWorkflowStack(self, 'docebo-outbound-workflow-stack', environment, account_num)

class RDSPipelineStage(Stage):
    def __init__(self, scope: Construct, id: str, environment: str, account_num: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        service = RDSStack(self, 'rds-deployment-stack', environment, account_num)

class EligibilityCDKSAMBuildStage(Stage):
    def __init__(self, scope: Construct, id: str, environment: str, account_num: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        service = EligibilityCDKSAMBuild(self, 'Eligibility-CDK-SAM-Build', environment, account_num)

class MigrationScriptsPipelineStage(Stage):
    def __init__(self, scope: Construct, id: str, environment: str, account_num: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        service = MigrationWorkflowStack(self, 'migration-scripts-workflow-stack', environment, account_num)
class TranscriptsRetractionStage(Stage):

    def __init__(self, scope: Construct, id: str, environment: str, account_num: str, **kwargs):
        super().__init__(scope, id, **kwargs)
        service = TranscriptRetractionsWorkflowStack(self, 'transcripts-retraction-workflow-stack',environment, account_num)


class EligibilityCalculationWorkflowStage(Stage):
    def __init__(self, scope: Construct, id: str,environment: str, account_num: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        service = EligibilityCalculationWorkflowStack(self, 'Eligibility-Calculation-workflow-stack',environment, account_num)


