#!/bin/bash
echo "Build docker image"
docker build --platform linux/arm64 -t rt_discovery_agent_bedrock_image:latest .
docker tag rt_discovery_agent_bedrock_image:latest 160885287007.dkr.ecr.us-east-2.amazonaws.com/rt_discovery_agent_bedrock_repo:latest

echo "Authenticate docker to ECR"
aws ecr get-login-password --region us-east-2 --profile takara-instrument-admin | \
  docker login --username AWS --password-stdin 160885287007.dkr.ecr.us-east-2.amazonaws.com

echo "Create ECR repo"
aws ecr create-repository --repository-name rt_discovery_agent_bedrock_repo --region us-east-2 \
  --image-scanning-configuration scanOnPush=true --image-tag-mutability MUTABLE --profile takara-instrument-admin

echo "Push docker image to ECR"
docker push 160885287007.dkr.ecr.us-east-2.amazonaws.com/rt_discovery_agent_bedrock_repo:latest

echo "Create Lambda function"
aws lambda create-function --function-name rt_discovery_agent_bedrock_lambda --package-type Image \
  --code ImageUri=160885287007.dkr.ecr.us-east-2.amazonaws.com/rt_discovery_agent_bedrock_repo:latest \
  --role arn:aws:iam::160885287007:role/takara_instrument_lambda_role \
  --profile takara-instrument-admin \
  --architectures arm64 \
  --memory-size 2048 \
  --timeout 60

