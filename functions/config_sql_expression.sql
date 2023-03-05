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