from constructs import Construct
from aws_cdk import (
    Stack, 
    aws_stepfunctions as sfn, 
)

import json
from bin.get_caller_identity import AccountNumberGetter

class E2EWorkflowStack(Stack):

    def __init__(self,scope: Construct,id: str,environment: str, account_num: str, **kwargs) -> None:
        super().__init__(scope,id,**kwargs)

        

        state_machine_definition = {
            "Comment": "The State machine Orchestrated the execution of the E2E Integration ", 
            "StartAt": "Approve for person quarantine", 
            "States": {
                "Approve for person quarantine": {
                    "Type": "Task", 
                    "Resource": "arn:aws:states:::glue:startJobRun.sync", 
                    "Parameters": {
                        "JobName": f"{environment}-glue-approve-personquarantine-records"
                    }, 
                    "Next": "Post Approval for person quarantine"
                },
                "Post Approval for person quarantine": {
                    "Type": "Task", 
                    "Resource": "arn:aws:states:::glue:startJobRun.sync", 
                    "Parameters": {
                        "JobName": f"{environment}-glue-quarantine-personmastering"
                    }, 
                    "Next": "API and SFTP to S3"
                }, 
                "API and SFTP to S3": {
                    "Type": "Task", 
                    "Resource": "arn:aws:states:::states:startExecution.sync:2", 
                    "Parameters": {
                        "StateMachineArn": f"arn:aws:states:us-west-2:{account_num}:stateMachine:{environment}-api-and-sftp-to-s3-workflow"
                    }, 
                    "Next": "Datastore S3 Check", 
                    "Catch": [
                        {
                            "ErrorEquals": [
                            "States.ALL"
                            ], 
                            "Next": "Datastore S3 Check"
                        }
                    ]
                }, 
                "Datastore S3 Check": {
                    "Type": "Task", 
                    "Resource": f"arn:aws:lambda:us-west-2:{account_num}:function:{environment}-lambda_check_files", 
                    "ResultPath": "$.lambda_handler_all", 
                    "Next": "Has SFTP Files", 
                    "Retry": [
                        {
                            "ErrorEquals": [
                                "States.ALL"
                            ], 
                            "BackoffRate": 1, 
                            "IntervalSeconds": 30, 
                            "MaxAttempts": 3, 
                            "Comment": "Retry lambda on error"
                        }
                    ]
                }, 
                "End E2E Process": {
                    "Type": "Pass", 
                    "End": True
                    }, 
                "Has SFTP Files": {
                    "Type": "Choice", 
                    "Choices": [
                        {
                            "Variable": "$.lambda_handler_all.objects", 
                            "BooleanEquals": True, 
                            "Next": "CDWA-Workflow"
                        }
                    ], 
                    "Default": "End E2E Process"
                },
                "CDWA-Workflow": {
                    "Type": "Task", 
                    "Resource": "arn:aws:states:::states:startExecution.sync:2", 
                    "Parameters": {
                        "StateMachineArn": f"arn:aws:states:us-west-2:{account_num}:stateMachine:{environment}-cdwa-workflow"
                    }, 
                    "Next": "Qualtrics-Workflow", 
                    "Catch": [
                        {
                            "ErrorEquals": [
                                "States.ALL"
                            ], 
                            "Next": "Qualtrics-Workflow"
                        }
                    ]
                }, 
                "Qualtrics-Workflow": {
                    "Type": "Task", 
                    "Resource": "arn:aws:states:::states:startExecution.sync:2", 
                    "Parameters": {
                        "StateMachineArn": f"arn:aws:states:us-west-2:{account_num}:stateMachine:{environment}-qualtrics-workflow"
                    }, 
                    "Next": "Credential-Workflow", 
                    "Catch": [
                        {
                            "ErrorEquals": [
                                "States.ALL"
                            ], 
                            "Next": "Credential-Workflow"
                        }
                    ]
                }, 
                "Credential-Workflow": {
                    "Type": "Task", 
                    "Resource": "arn:aws:states:::states:startExecution.sync:2", 
                    "Parameters": {
                        "StateMachineArn": f"arn:aws:states:us-west-2:{account_num}:stateMachine:{environment}-credential-workflow"
                    }, 
                    "Next": "DOH- Workflow", 
                    "Catch": [
                        {
                            "ErrorEquals": [
                                "States.ALL"
                            ], 
                            "Next": "DOH- Workflow"
                        }
                    ]
                }, 
                "DOH- Workflow": {
                    "Type": "Task", 
                    "Resource": "arn:aws:states:::states:startExecution.sync:2", 
                    "Parameters": {
                        "StateMachineArn": f"arn:aws:states:us-west-2:{account_num}:stateMachine:{environment}-doh-workflow"
                    }, 
                    "Next": "EXAM - Workflow", 
                    "Catch": [
                        {
                            "ErrorEquals": [
                                "States.ALL"
                            ], 
                            "Next": "EXAM - Workflow"
                        }
                    ]
                }, 
                "EXAM - Workflow": {
                    "Type": "Task", 
                    "Resource": "arn:aws:states:::states:startExecution.sync:2", 
                    "Parameters": {
                        "StateMachineArn": f"arn:aws:states:us-west-2:{account_num}:stateMachine:{environment}-exam-workflow"
                    }, 
                    "Next": "B2B-BusinessLogic-Workflow", 
                    "Catch": [
                        {
                            "ErrorEquals": [
                                "States.ALL"
                            ], 
                            "Next": "B2B-BusinessLogic-Workflow"
                        }
                    ]
                }, 
                "B2B-BusinessLogic-Workflow": {
                    "Type": "Task", 
                    "Resource": "arn:aws:states:::states:startExecution.sync:2", 
                    "Parameters": {
                        "StateMachineArn": f"arn:aws:states:us-west-2:{account_num}:stateMachine:{environment}-b2b-business-logic-workflow"
                    }, 
                    "Next": "Eligibility-Calculation-Workflow-State-1"
                },
                "Eligibility-Calculation-Workflow-State-1": {
                    "Type": "Task", 
                    "Resource": "arn:aws:states:::states:startExecution.sync:2", 
                    "Parameters": {
                        "StateMachineArn": f"arn:aws:states:us-west-2:{account_num}:stateMachine:{environment}-eligibility-calculation-workflow"
                    }, 
                    "Next": "Benefits Continuation workflow"
                }, 
                "Benefits Continuation workflow": {
                    "Type": "Task", 
                    "Resource": "arn:aws:states:::states:startExecution.sync:2", 
                    "Parameters": {
                        "StateMachineArn": f"arn:aws:states:us-west-2:{account_num}:stateMachine:{environment}-benefits-continuation-workflow"
                    }, 
                    "Next": "Trainingtransfers Workflow"
                }, 
                "Trainingtransfers Workflow": {
                    "Type": "Task", 
                    "Resource": "arn:aws:states:::states:startExecution.sync:2", 
                    "Parameters": {
                        "StateMachineArn": f"arn:aws:states:us-west-2:{account_num}:stateMachine:{environment}-training-transfers-workflow"
                    }, 
                    "Next": "Training Completions Workflow"
                }, 
                "Training Completions Workflow": {
                    "Type": "Task", 
                    "Resource": "arn:aws:states:::states:startExecution.sync:2", 
                    "Parameters": {
                        "StateMachineArn": f"arn:aws:states:us-west-2:{account_num}:stateMachine:{environment}-training-completions-workflow"
                    }, 
                    "Next": "Eligibility-Calculation-Workflow-State-2"
                },
                "Eligibility-Calculation-Workflow-State-2": {
                    "Type": "Task", 
                    "Resource": "arn:aws:states:::states:startExecution.sync:2", 
                    "Parameters": {
                        "StateMachineArn": f"arn:aws:states:us-west-2:{account_num}:stateMachine:{environment}-eligibility-calculation-workflow"
                    }, 
                    "Next": "SalesForce Outbound Workflow"
                }, 
                "SalesForce Outbound Workflow": {
                    "Type": "Task", 
                    "Resource": "arn:aws:states:::states:startExecution.sync:2", 
                    "Parameters": {
                        "StateMachineArn": f"arn:aws:states:us-west-2:{account_num}:stateMachine:{environment}-salesforce-outbound-workflow"
                    }, 
                    "Next": "Datastore S3 Check 2"
                }, 
                "Datastore S3 Check 2": {
                    "Type": "Task", 
                    "Resource": f"arn:aws:lambda:us-west-2:{account_num}:function:{environment}-lambda_check_files", 
                    "ResultPath": "$.lambda_handler_all2", 
                    "Next": "Has SFTP Files 2", 
                    "Retry": [
                        {
                            "ErrorEquals": [
                                "States.ALL"
                            ], 
                            "BackoffRate": 1, 
                            "IntervalSeconds": 30, 
                            "MaxAttempts": 3, 
                            "Comment": "Retry lambda on error"
                        }
                    ]
                }, 
                "Has SFTP Files 2": {
                    "Type": "Choice",
                    "Choices": [
                        {
                            "Variable": "$.lambda_handler_all2.objects",
                            "BooleanEquals": True,
                            "Next": "CDWA-Workflow"
                        }
                    ],
                    "Default": "End E2E Process"
                }
            }
        }

        state_machine = sfn.CfnStateMachine(self,"E2EStateMachine", 
            definition_string=json.dumps(state_machine_definition), 
            state_machine_name=environment+"-E2EStateMachine", 
            role_arn=f"arn:aws:iam::{account_num}:role/cdk-hnb659fds-cfn-exec-role-{account_num}-us-west-2"
        )
