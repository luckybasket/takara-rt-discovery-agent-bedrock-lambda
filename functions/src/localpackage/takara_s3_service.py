import boto3
from botocore.config import Config


class TakaraS3Service:
  """Contains methods for managing the takara aws s3 storage.
  """

  def __init__(self, region):
    s3Config = Config(signature_version='s3v4')
    self.s3Client = boto3.client(service_name='s3', region_name=region, config=s3Config)
    

  def get_presigned_url(self, bucketName, folderPath, objectKey, expirationTime):
    presignedURL = None
    if folderPath:
      objectPath = folderPath+'/'+objectKey
    else:
      objectPath = objectKey
    try:
      presignedURL = self.s3Client.generate_presigned_url(
        ClientMethod='get_object',  # Method to presign for (e.g., get_object, put_object)
        Params={
            'Bucket': bucketName,
            'Key': objectPath
        },
        ExpiresIn=expirationTime
      )
    except Exception as e:
      print(f"Error generating presigned URL: {e}")
    return presignedURL
  
  