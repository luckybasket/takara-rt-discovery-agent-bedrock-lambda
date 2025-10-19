import boto3
from boto3.dynamodb.types import TypeDeserializer
import json


class TakaraAmplifyService:
  """Contains methods for managing the takara aws amplify s3 storage and dynamoDB.
  """

  def __init__(self):
    self.s3Client = boto3.client('s3')
    self.dynamodbClient = boto3.client('dynamodb')
    self.lambdaClient = boto3.client('lambda')
    self.authCode = r')j9ju\=+ui"WuQ]=7G8s'

  def download_file_content(self, bucketID, s3Path):
    response = self.s3Client.get_object(Bucket=bucketID, Key=s3Path)
    fileContent = response['Body'].read().decode('utf-8')
    return fileContent
  
  def download_file_bytes(self, bucket, s3Path):
    response = self.s3Client.get_object(Bucket=bucket, Key=s3Path)
    fileBytes = response['Body'].read()
    return fileBytes
  
  def upload_io_image(self, bucketID, image, s3Path, contentType='image/png'):
    response = self.s3Client.put_object(Body=image.getvalue(), Bucket=bucketID, Key=s3Path, ContentType=contentType)
    return response
  
  def upload_csv(self, bucketID, csvData, s3Path):
    response = self.s3Client.put_object(Body=csvData.getvalue(), Bucket=bucketID, Key=s3Path, ContentType='text/csv')
    return response
  
  def create_table_item(self, tableID, item):
    response = self.dynamodbClient.put_item(
      Item=item,
      ReturnConsumedCapacity='TOTAL',
      TableName=tableID,
    )
    return response
  
  def update_table_item(self, tableID, expressionAttributeNames, expressionAttributeValues, key):
    namesKeys = list(expressionAttributeNames.keys())
    valuesKeys = list(expressionAttributeValues.keys())
    updateExpression = 'SET '
    for i in range(len(namesKeys)):
      updateExpression += namesKeys[i] + ' = ' + valuesKeys[i] + ', '
    updateExpression = updateExpression[:-2]
    response = self.dynamodbClient.update_item(
      ExpressionAttributeNames=expressionAttributeNames,
      ExpressionAttributeValues=expressionAttributeValues,
      Key=key,
      ReturnValues='ALL_NEW',
      TableName=tableID,
      UpdateExpression=updateExpression,
    )
    return response
  

  def scan_table_item(self, tableID, expressionAttributeValues, filterExpression):
    response = self.dynamodbClient.scan(
      ExpressionAttributeValues=expressionAttributeValues,
      FilterExpression=filterExpression,
      TableName=tableID,
    )
    userData = None
    if 'Items' in response:
      userData = response['Items'][0]
      deserializer = TypeDeserializer()
      for key in userData:
        userData[key] = deserializer.deserialize(userData[key])
    return userData
  
  def get_item_key(self, tableID, expressionAttributeValues, filterExpression):
    userData = self.scan_table_item(tableID, expressionAttributeValues, filterExpression)
    itemKey = None
    if 'id' in userData:
      itemKey = userData['id']
    return itemKey
  

  def invoke_lambda(self, functionName, payload):
    payload.update({'auth_code': self.authCode})
    response = self.lambdaClient.invoke(
      FunctionName=functionName,
      InvocationType='RequestResponse',
      Payload=json.dumps(payload),
    )
    result = json.loads(response['Payload'].read())
    body = json.loads(result['body'])
    return body