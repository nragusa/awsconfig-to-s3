# Overview

This CDK application will create an AWS Lambda function that will query AWS Config
and store the results in an S3 bucket. It uses [AWS Config advanced query](https://docs.aws.amazon.com/config/latest/developerguide/querying-AWS-resources.html)
to get the results and will store them in either CSV or JSON format. The files can
then be downloaded from S3 for further modification.

## Prerequisites

The following is required:

* AWS Config enabled
* Python 3.9
* [AWS CDK](https://aws.amazon.com/cdk/) (version 2.67.0 was used at the time of creation)

To deploy this solution, you'll first need to install the python dependencies location in the [layers](layers/) directory.

```bash
sudo yum -y install gcc openssl-devel bzip2-devel libffi-devel
curl https://pyenv.run | bash
pyenv install 3.9.10
pyenv shell 3.9.10
git clone https://github.com/nragusa/awsconfig-to-s3.git
cd awsconfig-to-s3
pip3 install -t layers/pandas/python -r layers/pandas/requirements.txt
```

Next, install `pipenv`, a python package dependency manager, along with the dependencies. Finally, activate the environment:

```bash
pip3 install --user pipenv
pipenv install
pipenv shell
```

Next, you'll need to edit [cdk.context.json](cdk.context.json) and replace the values of `aggregator_name` and `aggregator_id`
with values from your environment. The `aggregator_name` is the name of an [AWS Config aggregator](https://docs.aws.amazon.com/config/latest/developerguide/aggregate-data.html)
which can be configured to query resources across multiple regions and multiple accounts. You can find the `aggregator_name`
and `aggregator_id` by running the following command:

```bash
aws configservice describe-configuration-aggregators   
{
    "ConfigurationAggregators": [
        {
            "ConfigurationAggregatorName": "aws-controltower-ConfigAggregatorForOrganizations",
            "ConfigurationAggregatorArn": "arn:aws:config:us-east-1:12345678910:config-aggregator/config-aggregator-abcd1234",
            "OrganizationAggregationSource": {
                "RoleArn": "arn:aws:iam::12345678910:role/service-role/AWSControlTowerConfigAggregatorRoleForOrganizations",
                "AllAwsRegions": true
            },
            "CreationTime": "2021-03-12T15:07:06.200000+00:00",
            "LastUpdatedTime": "2021-03-12T15:07:06.381000+00:00"
        }
    ]
    ...
}
```

The `aggregator_id` is the final string of the `ConfigurationAggregatorArn`. In the example above, the `aggregator_id` is
`config-aggregator-abcd1234`.

Next, make sure the appropriate version of the [AWS CDK](https://aws.amazon.com/cdk/) is installed:

```bash
sudo npm install -g aws-cdk@2.67.0
```

## Deployment

Use the [AWS CDK](https://aws.amazon.com/cdk/) to deploy the code. If not already done, you'll need to bootstrap your environment,
being sure to replace `ACCOUNT-NUMBER` and `REGION`.

```bash
cdk bootstrap aws://ACCOUNT-NUMBER/REGION
cdk deploy
```

## Operations

The Lambda function is scheduled to run daily. The reports will be stored in an S3 bucket. The name of the bucket
used is found in the `Outputs` tab in the CloudFormation console.
