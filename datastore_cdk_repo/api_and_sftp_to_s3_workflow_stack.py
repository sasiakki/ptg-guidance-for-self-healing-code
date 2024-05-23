from constructs import Construct
from aws_cdk import (
    Stack, 
    aws_stepfunctions as sfn,
)
import json
from bin.get_caller_identity import AccountNumberGetter
from bin.ec2_utils import EC2Utils

class ApiandSftpToS3WorkflowStack(Stack):

    def __init__(self,scope: Construct,id: str,environment: str, account_num: str, **kwargs) -> None:
        super().__init__(scope,id,**kwargs)

        state_machine_definition= {
            "Comment": "api and sftp to s3 workflow",
            "StartAt": "ParallelState",
            "States": {
                "ParallelState": {
                "Type": "Parallel",
                "Branches": [
                    {
                    "StartAt": "doh-sftp-workflow",
                    "States": {
                        "doh-sftp-workflow": {
                        "Type": "Task",
                        "Resource": "arn:aws:states:::states:startExecution.sync",
                        "Parameters": {
                            "StateMachineArn": f"arn:aws:states:us-west-2:{account_num}:stateMachine:{environment}-doh-sftp-workflow"
                        },
                        "End": True
                        }
                    }
                    },
                    {
                    "StartAt": "cdwa-sftp-workflow",
                    "States": {
                        "cdwa-sftp-workflow": {
                        "Type": "Task",
                        "Resource": "arn:aws:states:::states:startExecution.sync",
                        "Parameters": {
                            "StateMachineArn": f"arn:aws:states:us-west-2:{account_num}:stateMachine:{environment}-cdwa-sftp-workflow"
                        },
                        "End": True
                        }
                    }
                    },
                    {
                    "StartAt": "dshs-sftp-workflow",
                    "States": {
                        "dshs-sftp-workflow": {
                        "Type": "Task",
                        "Resource": "arn:aws:states:::states:startExecution.sync",
                        "Parameters": {
                            "StateMachineArn": f"arn:aws:states:us-west-2:{account_num}:stateMachine:{environment}-dshs-sftp-workflow"
                        },
                        "End": True
                        }
                    }
                    },
                    {
                    "StartAt": "api-to-s3-workflow",
                    "States": {
                        "api-to-s3-workflow": {
                        "Type": "Task",
                        "Resource": "arn:aws:states:::states:startExecution.sync",
                        "Parameters": {
                            "StateMachineArn": f"arn:aws:states:us-west-2:{account_num}:stateMachine:{environment}-api-to-s3-workflow" 
                        },
                        "End": True
                        }
                    }
                    }
                ],
                "End": True
                }
            }
        }
        
        state_machine = sfn.CfnStateMachine(self,"api-and-sftp-to-s3-workflow", 
            definition_string=json.dumps(state_machine_definition), 
            state_machine_name=environment+"-api-and-sftp-to-s3-workflow", 
            role_arn=f"arn:aws:iam::{account_num}:role/cdk-hnb659fds-cfn-exec-role-{account_num}-us-west-2"
        )