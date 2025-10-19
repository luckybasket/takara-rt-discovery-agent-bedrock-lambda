#!/usr/bin/python
import importlib
import sys
import json
import os
import boto3



if __name__ == "__main__":
  """ Takara AWS Bedrock RT knowledge base test demo
    Input arguments:
            
    Run command example:
      %python bedrock_rt_knowledge_base.py
  """
  
  """
  ssoProfile = 'takara-instrument-admin'
  knowledgeBaseID = "KTSGN8EZBA"
  modelARN = "arn:aws:bedrock:us-east-2:160885287007:inference-profile/us.anthropic.claude-3-5-sonnet-20240620-v1:0" # Example model ARN
  """
  ssoProfile = 'takara-luckybasket-dev'
  knowledgeBaseID = "MHQS4NNTSJ"
  modelARN = "arn:aws:bedrock:us-east-2:039612858415:inference-profile/us.anthropic.claude-3-5-sonnet-20240620-v1:0" # Example model ARN
  
  bedrock = importlib.import_module("localpackage.bedrock_service")
  bedrockService = bedrock.BedrockService(ssoProfile)
  sessionID = None
  queryText = "List known RT mutants"
  responseContent, responseCitationsList, newSessionID = bedrockService.rag_query(knowledgeBaseID, modelARN, sessionID, queryText)
  print(responseContent)
  print(responseCitationsList)
  print(newSessionID)
  


  

