#!/bin/bash
echo "Build docker image"
docker build --platform linux/arm64 -t aws_bedrock_image:latest .
docker tag aws_bedrock_image:latest 039612858415.dkr.ecr.us-west-1.amazonaws.com/aws_bedrock_repo:latest

echo "Authenticate docker and push image"
aws ecr get-login-password --region us-west-1 --profile takara-luckybasket-dev | docker login \
  --username AWS --password-stdin 039612858415.dkr.ecr.us-west-1.amazonaws.com
docker push 039612858415.dkr.ecr.us-west-1.amazonaws.com/aws_bedrock_repo:latest

echo "Update function docker image"
aws lambda update-function-code --function-name aws_bedrock_lambda \
  --image-uri 039612858415.dkr.ecr.us-west-1.amazonaws.com/aws_bedrock_repo:latest \
  --profile takara-luckybasket-dev

