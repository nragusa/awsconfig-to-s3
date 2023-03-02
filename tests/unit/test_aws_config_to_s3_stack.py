import aws_cdk as core
import aws_cdk.assertions as assertions

from aws_config_to_s3.aws_config_to_s3_stack import AwsConfigToS3Stack

# example tests. To run these tests, uncomment this file along with the example
# resource in aws_config_to_s3/aws_config_to_s3_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = AwsConfigToS3Stack(app, "aws-config-to-s3")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
