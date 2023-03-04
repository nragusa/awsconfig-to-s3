#!/usr/bin/env python3
import aws_cdk as cdk

from aws_config_to_s3.aws_config_to_s3_stack import AwsConfigToS3Stack


app = cdk.App()
AwsConfigToS3Stack(app,
                   'AwsConfigToS3Stack',
                   description='This stack creates a Lambda function to query AWS Config advanced query and store the results in an S3 bucket'
                   )

app.synth()
