import boto3
import botocore
import json
import logging
import os
import pandas as pd
from datetime import date

#####
# Configuration
#####
AGGREGATOR_NAME = os.environ['AGGREGATOR_NAME']
S3_OUTPUT_BUCKET = os.environ['S3_OUTPUT_BUCKET']
LOG_LEVEL = os.environ['LOG_LEVEL']
OUTPUT_FORMAT = os.environ['OUTPUT_FORMAT']
EXPRESSION = """
SELECT
  resourceId,
  resourceType,
  supplementaryConfiguration.BucketVersioningConfiguration.status,
  resourceCreationTime,
  awsRegion,
  supplementaryConfiguration.ServerSideEncryptionConfiguration.rules.applyServerSideEncryptionByDefault.sseAlgorithm,
  tags
WHERE
  resourceType = 'AWS::S3::Bucket'
"""
#####

logger = logging.getLogger()
logging_level = logging.getLevelName(LOG_LEVEL)
logger.setLevel(logging_level)


def query_config(paged_results) -> list:
    """Gets the results from AWS Config and returns a list of the results

    Keyword arguments:
    paged_results -- iterable of PageIterator

    Returns:
    results -- list of the results
    """
    results = list()
    for page in paged_results:
        data = page['Results']
        results += [json.loads(x) for x in data]
    return results


def handler(event, context):
    """Queries AWS Config advanced query functionality and stores the results
    in an S3 bucket. The query (expression) and S3 output bucket are environment
    variables.
    """
    # Create the boto3 clients
    config_client = boto3.client('config')
    paginator = config_client.get_paginator('select_aggregate_resource_config')
    s3 = boto3.resource('s3')

    # Make sure we have a proper file output defined
    output_format = OUTPUT_FORMAT.lower()
    if output_format not in ['json', 'csv']:
        logger.warning('Output format must be CSV or JSON. Setting to JSON.')
        output_format = 'json'
    logger.debug(f'File output format set to {output_format}')

    # Set the name of the output file
    output_file = f'/tmp/{date.today().isoformat()}.{output_format}'

    try:
        logger.info('Calling AWS Config advanced query')
        logger.debug(
            f'Aggregator name {AGGREGATOR_NAME} and query {EXPRESSION}'
        )
        # Call the select_aggregate_resource_config API and get the results
        paged_results = paginator.paginate(
            Expression=EXPRESSION,
            ConfigurationAggregatorName=AGGREGATOR_NAME,
            Limit=50
        )
        response = query_config(paged_results)

        # Format the results into the proper output format
        if output_format == 'csv':
            logger.info('Writing results to CSV file')
            formatted_response = pd.json_normalize(response)
            formatted_response.to_csv(output_file, index=False)
        else:
            # JSON
            logger.info('Writing results to JSON file')
            with open(output_file, 'w') as f:
                json.dump({'Results': response}, f)

        # Upload the output file to S3
        logger.info('Uploading output to S3')
        logger.debug(
            f'Uploading {output_file} to S3 bucket {S3_OUTPUT_BUCKET}'
        )
        s3.meta.client.upload_file(
            output_file,
            S3_OUTPUT_BUCKET,
            f'{date.today().isoformat().replace("-","/")}/config-output.{output_format}'
        )
        logger.info('Success')
    except botocore.exceptions.ClientError as error:
        logger.error(f'Problem calling AWS APIs: {error}')
        raise
