"""Deploys the AWS Config to S3 Lambda function and a daily event to invoke it."""

from aws_cdk import BundlingOptions, CfnOutput, Duration, Stack
from aws_cdk import aws_events as events
from aws_cdk import aws_events_targets as events_targets
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as lambda_
from aws_cdk import aws_s3 as s3
from aws_cdk import aws_sam as sam
from constructs import Construct


class AwsConfigToS3Stack(Stack):
    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        s3_bucket = s3.Bucket(
            self,
            'AWSConfigOutputBucket',
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            bucket_name=f'aws-config-output-{self.region}-{self.account}',
            enforce_ssl=True,
            versioned=True,
        )
        config_to_s3 = lambda_.Function(
            self,
            'AWSConfigToS3Function',
            code=lambda_.Code.from_asset(
                path='functions/',
                bundling=BundlingOptions(
                    image=lambda_.Runtime.PYTHON_3_13.bundling_image,
                    command=[
                        'bash',
                        '-c',
                        'pip install --no-cache -r requirements.txt -t /asset-output && cp -au . /asset-output',
                    ],
                ),
            ),
            handler='aws_config_to_s3.handler',
            runtime=lambda_.Runtime.PYTHON_3_12,
            description='Queries AWS Config advanced query to get the state of resources',
            environment={
                'AGGREGATOR_NAME': self.node.try_get_context('aggregator_name'),
                'S3_OUTPUT_BUCKET': s3_bucket.bucket_name,
                'OUTPUT_FORMAT': self.node.try_get_context('output_format'),
                'LOG_LEVEL': self.node.try_get_context('log_level'),
            },
            timeout=Duration.seconds(60),
        )

        lambda_target = events_targets.LambdaFunction(config_to_s3)
        events.Rule(
            self,
            'InvokeAWSConfigToS3Lambda',
            enabled=True,
            schedule=events.Schedule.rate(duration=Duration.days(1)),
            targets=[lambda_target],
            description='Invokes the AWS Config to S3 Lambda function daily',
        )

        s3_bucket.grant_write(config_to_s3.role)
        config_to_s3.role.attach_inline_policy(
            iam.Policy(
                self,
                'AWSConfigAdvanceQueryAccess',
                document=iam.PolicyDocument(
                    statements=[
                        iam.PolicyStatement(
                            sid='AWSConfigAdvanceQueryAccess',
                            actions=['config:SelectAggregateResourceConfig'],
                            effect=iam.Effect.ALLOW,
                            resources=[
                                f'arn:aws:config:{self.region}:{self.account}:config-aggregator/{self.node.try_get_context("aggregator_id")}'
                            ],
                        )
                    ]
                ),
            )
        )

        CfnOutput(
            self,
            'S3BucketName',
            description='Name of the S3 bucket where the output is stored',
            value=s3_bucket.bucket_name,
        )
        CfnOutput(
            self,
            'ReportOutputFormat',
            description='The format the reports will be stored in',
            value=self.node.try_get_context('output_format'),
        )
