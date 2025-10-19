ECHO Build docker image
call docker build --platform linux/arm64 --provenance false -t gostix_agent_bedrock_image:latest .
call docker tag gostix_agent_bedrock_image:latest 160885287007.dkr.ecr.us-east-2.amazonaws.com/gostix_agent_bedrock_repo:latest

ECHO Authenticate docker and push image
call aws ecr get-login-password --region us-east-2 --profile takara-instrument-admin | docker login ^
  --username AWS --password-stdin 160885287007.dkr.ecr.us-east-2.amazonaws.com
call docker push 160885287007.dkr.ecr.us-east-2.amazonaws.com/gostix_agent_bedrock_repo:latest

ECHO Update function docker image
call aws lambda update-function-code --function-name gostix_agent_bedrock_lambda ^
  --image-uri 160885287007.dkr.ecr.us-east-2.amazonaws.com/gostix_agent_bedrock_repo:latest ^
  --profile takara-instrument-admin

