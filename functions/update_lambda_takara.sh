#!/bin/bash
echo "Build docker image"
docker build --platform linux/arm64 -t rt_discovery_agent_bedrock_image:latest .
docker tag rt_discovery_agent_bedrock_image:latest 160885287007.dkr.ecr.us-east-2.amazonaws.com/rt_discovery_agent_bedrock_repo:latest

echo "Authenticate docker and push image"
aws ecr get-login-password --region us-east-2 --profile takara-instrument-admin | docker login \
  --username AWS --password-stdin 160885287007.dkr.ecr.us-east-2.amazonaws.com
docker push 160885287007.dkr.ecr.us-east-2.amazonaws.com/rt_discovery_agent_bedrock_repo:latest

echo "Update function docker image"
aws lambda update-function-code --function-name rt_discovery_agent_bedrock_lambda \
  --image-uri 160885287007.dkr.ecr.us-east-2.amazonaws.com/rt_discovery_agent_bedrock_repo:latest \
  --profile takara-instrument-admin

