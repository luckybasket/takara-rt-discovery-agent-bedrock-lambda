#!/usr/bin/python
import importlib
import sys
import json
import os
import boto3
from botocore.config import Config


if __name__ == "__main__":
  """ Takara AWS Bedrock s3 bucket access test demo
    Input arguments:
            
    Run command example:
      %python s3_test.py
  """
  
  ssoProfile = 'takara-instrument-admin'
  #ssoProfile = 'takara-luckybasket-dev'
  region = 'us-east-2'
  takaraS3 = importlib.import_module("localpackage.takara_s3_service")
  s3Service = takaraS3.TakaraS3Service(ssoProfile, region)
  objectKey = '(Maxima) - 2019 - US 10358670 B2- PRODUCTION OF NUCLEIC ACID-annotated.pdf'
  bucketName = 'takara-bedrock-rt-discovery'
  expirationTime = 3600
  presignedURL = s3Service.get_presigned_url(bucketName, objectKey, expirationTime)
  print(presignedURL)
  
  


  

