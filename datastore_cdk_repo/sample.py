from aws_cdk import (
    aws_cloudwatch as cloudwatch,
    aws_events as events,
    aws_events_targets as targets,
    aws_lambda as _lambda,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_events_rule_targets as rule_targets,
    aws_sns as sns,
    aws_sns_subscriptions as sns_subscriptions,
    Stack,
    Duration,
)
from constructs import Construct


class EC2CpuUtilizationMonitorStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Create a CloudWatch Dashboard
        dashboard = cloudwatch.Dashboard(
            self,
            "EC2CpuUtilizationDashboard",
            dashboard_name="EC2CpuUtilizationDashboard"
        )

        # Iterate through all AWS regions
        for region in ec2.AwsRegionList().get_all_regions():
            # Create an Event Rule to trigger at regular intervals (e.g., every 5 minutes)
            rule = events.Rule(
                self,
                f"EventRule-{region}",
                schedule=events.Schedule.rate(Duration.minutes(5)),
            )

            # Create a Lambda function to collect CPU utilization
            lambda_fn = _lambda.Function(
                self,
                f"EC2CpuUtilizationLambda-{region}",
                runtime=_lambda.Runtime.PYTHON_3_8,
                handler="cpu_utilization.handler",
                code=_lambda.Code.from_asset("lambda"),
                environment={
                    "REGION": region,
                }
            )

            # Grant necessary permissions to the Lambda function
            lambda_fn.add_to_role_policy(
                iam.PolicyStatement(
                    actions=["cloudwatch:GetMetricData", "cloudwatch:PutDashboard"],
                    resources=["*"],
                )
            )

            # Add the Lambda function as a target for the Event Rule
            rule.add_target(targets.LambdaFunction(lambda_fn))

            # Create an SNS topic for alarms
            alarm_topic = sns.Topic(
                self,
                f"AlarmTopic-{region}",
            )

            # Create an SNS subscription for email notifications
            alarm_topic.add_subscription(
                sns_subscriptions.EmailSubscription("your-email@example.com")
            )

            # Create a CloudWatch Alarm for CPU utilization
            cloudwatch.Alarm(
                self,
                f"EC2CpuUtilizationAlarm-{region}",
                alarm_description=f"EC2 CPU Utilization Alarm in {region}",
                evaluation_periods=1,
                threshold=90,  # Adjust the threshold as needed
                comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
                metric=cloudwatch.Metric(
                    metric_name="CPUUtilization",
                    namespace="AWS/EC2",
                    dimensions={
                        "AutoScalingGroupName": "YOUR-AUTO-SCALING-GROUP-NAME",
                    },
                    period=Duration.minutes(5),
                    statistic="Average",
                ),
                alarm_name=f"EC2CpuUtilizationAlarm-{region}",
                alarm_actions=[alarm_topic],
            )

app = App()
EC2CpuUtilizationMonitorStack(app, "EC2CpuUtilizationMonitorStack")
app.synth()
