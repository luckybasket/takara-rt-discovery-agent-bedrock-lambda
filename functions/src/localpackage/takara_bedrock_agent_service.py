import boto3
import uuid
import importlib
import io


class TakaraBedrockAgentService:
  """Contains methods for managing the takara aws Bedrock agent api.
  """

  def __init__(self, bucket, tables, logger, agentParams):
    self.bedrockClient = boto3.client(service_name='bedrock-agent-runtime', region_name=agentParams['bedrockRegion'])
    self.tams = importlib.import_module("localpackage.takara_amplify_service")
    self.takaraAmplify = self.tams.TakaraAmplifyService()
    self.authCode = r')j9ju\=+ui"WuQ]=7G8s'
    self.bucketID = bucket
    self.tmpTableID = tables['tmp']
    self.payloadCount = 1
    self.agentId = agentParams['agentId']
    self.aliasId = agentParams['aliasId']
    self.s3Path = agentParams['s3Path']
    self.sessionId = agentParams['sessionId']
    self.logger = logger
    self.statusIDKey = agentParams['statusIDKey']
    self.userIdentityID = agentParams['userIdentityID']
    self.statusData = {
      'status_id': 0,
      'progress_id': 0,
      'progress_max': 0,
      'payload': self.payloadCount*['']
    }
    self.statusDataLast = self.statusData.copy()
    self.aiResults = {}

  
  def update_status(self):
    payloadList = []
    for payloadItem in self.statusData['payload']:
      payloadList.append({'S': payloadItem})
    if self.statusData != self.statusDataLast:
      expressionAttributeNames={
          '#PID': 'progress_id',
          '#PMAX': 'progress_max',
          '#SID': 'status_id',
          '#PAYLOAD': 'payload'
        }
      expressionAttributeValues={
        ':pid': {
          'N': str(self.statusData['progress_id'])
        },
        ':pmax': {
          'N': str(self.statusData['progress_max'])
        },
        ':sid': {
          'N': str(self.statusData['status_id'])
        },
        ':payload': {
          'L': payloadList
        },
      }
      key = {
        'id': {
          'S': self.statusIDKey
        }
      }
      self.takaraAmplify.update_table_item(self.tmpTableID, expressionAttributeNames, expressionAttributeValues, key)
      self.statusDataLast = self.statusData.copy()
    return
  
  
  def reset_status(self):
    self.statusData = {
      'status_id': 0,
      'progress_id': 0,
      'progress_max': 0,
      'payload': self.payloadCount*['']
    }
    self.update_status()
    return
  



  def invoke_agent(self, prompt):
    response = self.bedrockClient.invoke_agent(
      agentId=self.agentId,
      agentAliasId=self.aliasId,
      enableTrace=True,
      sessionId = self.sessionId,
      inputText=prompt,
      streamingConfigurations = { 
        "applyGuardrailInterval" : 20,
        "streamFinalResponse" : False
      })
    responseContent = None
    responseCitationsList = []
    imgFileS3Path = None
    isCitationsFound = False
    isFilesFound = False
    completion = ""
    for event in response.get("completion"):
      #Collect agent output.
      if 'chunk' in event:
          chunk = event["chunk"]
          completion += chunk["bytes"].decode()
      
      # Log trace output.
      if 'trace' in event:
        trace_event = event.get("trace")
        trace = trace_event['trace']
        for key, value in trace.items():
          if 'observation' in value:
            if 'knowledgeBaseLookupOutput' in value['observation']:
              if 'retrievedReferences' in value['observation']['knowledgeBaseLookupOutput']:
                retrievedReferences = value['observation']['knowledgeBaseLookupOutput']['retrievedReferences']
                for reference in retrievedReferences:
                  if 'location' in reference:
                    if 's3Location' in reference['location']:
                      responseCitationsList.append(reference['location']['s3Location']['uri'])
                      isCitationsFound = True
      if 'files' in event:
        files = event['files']['files']
        for file in files:
          name = file['name']
          type = file['type']
          bytes_data = file['bytes']
          if type == 'image/png':
            imgdata = io.BytesIO(bytes_data)
            imgFileS3Path = self.s3Path + name
            self.takaraAmplify.upload_io_image(self.bucketID, imgdata, imgFileS3Path, 'image/png')
            self.statusData['payload'][0] = imgFileS3Path
            self.statusData['status_id'] = 1
            self.statusData['progress_id'] = 1
            self.statusData['progress_max'] = 1
            self.update_status()
            isFilesFound = True
    responseContent = completion
    self.aiResults.update({'responseContent': responseContent, 'responseCitationsList': responseCitationsList, 
      'imgFileS3Path': imgFileS3Path, 'isCitationsFound': isCitationsFound, 'isFilesFound': isFilesFound, 'sessionId': self.sessionId})
    return

  def query(self, queryText):
    self.reset_status()
    try:
      if self.sessionId is None:
        self.sessionId = str(uuid.uuid4())
      self.invoke_agent(queryText)
      self.aiResults.update({'isSuccess': True})
      return
    except Exception as e:
      responseContent = f"Error querying Bedrock: {e}"
      self.aiResults.update({'isSuccess': False, 'responseContent': responseContent})
      return