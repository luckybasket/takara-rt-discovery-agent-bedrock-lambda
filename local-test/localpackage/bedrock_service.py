import importlib
import json
import boto3

from enum import Enum
class ActionID(Enum):
  NONE = 0
  CONVERSE = 1
  RAG = 2
  CITATION = 3


class BedrockService:
  """Contains methods for processing the AWS Bedrock service.
  """

  def __init__(self, ssoProfile):
    self.tams = importlib.import_module("localpackage.takara_amplify_service")
    self.takaraAmplify = self.tams.TakaraAmplifyService(ssoProfile)
    session = boto3.Session(profile_name=ssoProfile)
    self.lambdaClient = session.client('lambda')
    self.authCode = r')j9ju\=+ui"WuQ]=7G8s'

  
  def converse(self, userMessage):
    payload = {
      'auth_code': self.authCode,
      'action_id': ActionID.CONVERSE.value,
      'payload': {
        'user_message': userMessage,
      }
    }
    response = self.lambdaClient.invoke(
      FunctionName='aws_bedrock_lambda',
      InvocationType='RequestResponse',
      Payload=json.dumps(payload),
    )
    result = json.loads(response['Payload'].read())
    output = json.loads(result['body'])
    responseText = None
    if output['isSuccess']:
      responseText = output['responseText']
    return responseText


  def rag_query(self, knowledgeBaseID, modelARN, sessionID, queryText):
    payload = {
      'auth_code': self.authCode,
      'action_id': ActionID.RAG.value,
      'payload': {
        'knowledge_base_id': knowledgeBaseID,
        'model_arn': modelARN,
        'session_id': sessionID,
        'query_text': queryText,
      }
    }
    response = self.lambdaClient.invoke(
      FunctionName='aws_bedrock_lambda',
      InvocationType='RequestResponse',
      Payload=json.dumps(payload),
    )
    result = json.loads(response['Payload'].read())
    output = json.loads(result['body'])
    responseText = None
    if output['isSuccess']:
      responseContent = output['responseContent']
      responseCitationsList = output['responseCitationsList']
      newSessionID = output['sessionID']
    return responseContent, responseCitationsList, newSessionID
  

  def citaion_source(self, citationKey):
    payload = {
      'auth_code': self.authCode,
      'action_id': ActionID.CITATION.value,
      'payload': {
        'citation_key': citationKey,
      }
    }
    response = self.lambdaClient.invoke(
      FunctionName='aws_bedrock_lambda',
      InvocationType='RequestResponse',
      Payload=json.dumps(payload),
    )
    result = json.loads(response['Payload'].read())
    output = json.loads(result['body'])
    presignedURL = None
    if output['isSuccess']:
      presignedURL = output['presignedURL']
    return presignedURL