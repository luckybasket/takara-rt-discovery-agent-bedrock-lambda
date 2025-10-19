#!/usr/bin/python
import importlib
import sys
import json
import os
import boto3



if __name__ == "__main__":
  """ Takara AWS Bedrock test demo
    Input arguments:
            
    Run command example:
      %python bedrock_test.py
  """
  
  #ssoProfile = 'takara-instrument-admin'
  ssoProfile = 'takara-luckybasket-dev'
  bedrock = importlib.import_module("localpackage.bedrock_service")
  bedrockService = bedrock.BedrockService(ssoProfile)
  responseText = bedrockService.converse("What is the capital of Taiwan?")
  print(responseText)
  


  

