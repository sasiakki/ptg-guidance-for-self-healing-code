import subprocess
import os
from aws_cdk import Stack, aws_s3 as s3, aws_s3_deployment as s3deploy
from constructs import Construct


class EligibilityCDKSAMBuild(Stack):
    def __init__(
        self, scope: Construct, id: str, environment: str, account_num: str, **kwargs
    ) -> None:
        super().__init__(scope, id, **kwargs)

        sam_build_prereq_commands = ["npm", "run", "compile"]

        sam_build_commands = [
            "sam",
            "build",
            "--template",
            "template.yaml",
            "--build-dir",
            ".aws-sam/build",
        ]

        # Run the SAM build
        eligibility_ms_prereq_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "eligibility-cdk-sam-workflow",
            "eligibility-ms-dev",
            "eligibility-ms",
        )
        eligibility_ms_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "eligibility-cdk-sam-workflow",
            "eligibility-ms-dev",
        )
        try:
            subprocess.run(["npm", "install", "--force"], cwd=eligibility_ms_prereq_dir,stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL, shell=True)
            subprocess.run(sam_build_prereq_commands, cwd=eligibility_ms_prereq_dir, stdout=subprocess.DEVNULL, shell=True)
            subprocess.run(sam_build_commands, cwd=eligibility_ms_dir,stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL, shell=True)
        except subprocess.CalledProcessError as e:
            print(f"Error occurred during SAM build: {e}")
            raise
