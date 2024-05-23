
from constructs import Construct
from aws_cdk import (
    Stack, 
    aws_lambda as _lambda, 
)

class LambdaLayer(Construct):
    def __init__(self, scope: Construct, id: str):
        super().__init__(scope, id)

        # Create the local Lambda layer
        local_layer = _lambda.LayerVersion(
            self,
            "custom-layer",
            code=_lambda.Code.from_asset("lambda_layer/custom-layer/"),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_9]
        )

        # Add another layer using an ARN
        arn_layer_arn = "arn:aws:lambda:us-west-2:345057560386:layer:AWS-Parameters-and-Secrets-Lambda-Extension:4"
        arn_layer = _lambda.LayerVersion.from_layer_version_arn(
            self,
            "AWS-Parameters-and-Secrets-Lambda-Extension",
            arn_layer_arn
        )

        # Store the layers in a list
        self.layers = [local_layer, arn_layer]