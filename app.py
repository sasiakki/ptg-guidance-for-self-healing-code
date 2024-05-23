#!/usr/bin/env python3
import os
import aws_cdk as cdk
from datastore_cdk_repo.ds_pipeline_stack import DSPipelineStack
from bin.get_caller_identity import AccountNumberGetter
from aws_cdk.aws_sam import CfnApplication
import aws_cdk as cdk
from datastore_cdk_repo.ds_pipeline_stack import DSPipelineStack

app = cdk.App()

# Create an instance of AccountNumberGetter
account_number = AccountNumberGetter()

# Call the get_account_number method
account_num = account_number.get_account_number()

environment = cdk.Environment(account=account_num, region="us-west-2")

DSPipelineStack(app, "DSWorkflowStacks", env=environment)

app.synth()