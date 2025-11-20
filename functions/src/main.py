import logging
import json
import importlib
import os

from enum import Enum
class ActionID(Enum):
  NONE = 0
  AGENT_KB = 1
  CITATION = 2


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
LAMBDA_AUTH_CODE = os.environ['LAMBDA_AUTH_CODE']


def handler(event, context):
  # Extract headers from the event object
  if 'httpMethod' in event:
    if event['httpMethod'] == 'OPTIONS':
      return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': '*',
            'Access-Control-Allow-Headers': '*'
        } } # preflight cors issue
  isAuthorized = False
  if 'headers' in event:
    headers = event['headers']
    if 'Authorization' in headers:
      auth_header = headers['Authorization']
      if 'Bearer' in auth_header:
        authCode = auth_header.split('Bearer ')[1]
        if (authCode == LAMBDA_AUTH_CODE) and ('body' in event):
          isAuthorized = True
          body = json.loads(event['body'])
          actionID = body['action_id']
          payload = body['payload'] 
  else:
    if event['auth_code'] == LAMBDA_AUTH_CODE:
      actionID = event['action_id']
      payload = event['payload']
      isAuthorized = True
  
  if isAuthorized:
    output = processAction(actionID, payload)
    statusCode = 200
  else:
    statusCode = 401
    output = {
      'message': 'User is not signed in'
    }
  
  response = {
    'isBase64Encoded': False,
    'statusCode': statusCode,
    'body': json.dumps(output),
    'headers': {
      'Content-Type': 'application/json',
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, PUT, GET, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Access-Control-Allow-Headers, Authorization, X-Requested-With'
    }
  }
  return response


def processAction(actionID, payload):
  output = {}
  match (actionID):
    case ActionID.NONE.value:
      output['isSuccess'] = True
    case ActionID.AGENT_KB.value:
      bedrock = importlib.import_module("localpackage.takara_bedrock_agent_service")
      bucket = payload['amplify_s3_bucket']
      bedrockRegion = payload['bedrock_region']
      tmpTable = payload['dynamodb_rt_discovery_bedrock_agent_tmp_table']
      tables ={
        'tmp': tmpTable
      }
      statusIDKey = payload['status_id_key']
      userIdentityID = payload['user_identity_id']
      tmpFolderMain = payload['tmp_folder_main']
      s3Path = 'users/'+userIdentityID+'/'+tmpFolderMain+'/rt_discovery_agent/tmp/'
      agentId = payload['agent_id']
      aliasId = payload['alias_id']
      sessionId = payload['session_id']
      if sessionId:
        if not sessionId.strip():
          sessionId = None
      else:
        sessionId = None
      agentParams = {}
      agentParams['s3Path'] = s3Path
      agentParams['statusIDKey'] = statusIDKey
      agentParams['userIdentityID'] = userIdentityID
      agentParams['agentId'] = agentId
      agentParams['aliasId'] = aliasId
      agentParams['sessionId'] = sessionId
      agentParams['bedrockRegion'] = bedrockRegion
      tbrs = bedrock.TakaraBedrockAgentService(bucket, tables, logger, agentParams)
      queryText = payload['query_text']
      tbrs.query(queryText)
      if tbrs.aiResults['isSuccess']:
        output['isSuccess'] = True
        output['responseContent'] = tbrs.aiResults['responseContent']
        output['responseCitationsList'] = tbrs.aiResults['responseCitationsList']
        output['imgFileS3Path'] = tbrs.aiResults['imgFileS3Path']
        output['isCitationsFound'] = tbrs.aiResults['isCitationsFound']
        output['isFilesFound'] = tbrs.aiResults['isFilesFound']
        output['sessionId'] = tbrs.aiResults['sessionId']
      else:
        output['isSuccess'] = False
        output['errorMsg'] = tbrs.aiResults['responseContent']
    case ActionID.CITATION.value:
      takaraS3 = importlib.import_module("localpackage.takara_s3_service")
      region = payload['bedrock_region']
      bucketName = payload['bucket_name']
      citationKey = payload['citation_key']
      folderPath = payload['folder_path']
      s3Service = takaraS3.TakaraS3Service(region)
      expirationTime = 3600
      presignedURL = s3Service.get_presigned_url(bucketName, folderPath, citationKey, expirationTime)
      if presignedURL is not None:
        output['isSuccess'] = True
        output['presignedURL'] = presignedURL
      else:
        output['isSuccess'] = False
        output['errorMsg'] = "Invalid citation"
    case _:
      output['isSuccess'] = False
      output['errorMsg'] = "Invalid action ID"
  return output
