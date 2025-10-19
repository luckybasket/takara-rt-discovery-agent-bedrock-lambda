import boto3
import uuid


class TakaraBedrockAgentService:
  """Contains methods for managing the takara aws Bedrock agent api.
  """

  def __init__(self, agentId, aliasId, sessionId, logger):
    self.bedrockClient = boto3.client(service_name='bedrock-agent-runtime', region_name='us-east-2')
    self.authCode = r')j9ju\=+ui"WuQ]=7G8s'
    self.agentId = agentId
    self.aliasId = aliasId
    self.sessionId = sessionId
    self.responseContent = None
    self.responseCitationsList = []
    self.logger = logger
    self.isSuccess = False

  
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
                      self.responseCitationsList.append(reference['location']['s3Location']['uri'])
    self.responseContent = completion
    return

  def query(self, queryText):
    try:
      if self.sessionId is None:
        self.sessionId = str(uuid.uuid4())
      self.invoke_agent(queryText)
      self.isSuccess = True
      return
    except Exception as e:
      self.responseContent = f"Error querying Bedrock: {e}"
      self.isSuccess = False
      return