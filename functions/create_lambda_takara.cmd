ECHO Build docker image
call docker build --platform linux/arm64 --provenance false -t gostix_agent_bedrock_image:latest .
call docker tag gostix_agent_bedrock_image:latest 160885287007.dkr.ecr.us-east-2.amazonaws.com/gostix_agent_bedrock_repo:latest

ECHO Authenticate docker to ECR
call aws ecr get-login-password --region us-east-2 --profile takara-instrument-admin | docker login ^
  --username AWS --password-stdin 160885287007.dkr.ecr.us-east-2.amazonaws.com

ECHO Create ECR repo
call aws ecr create-repository --repository-name gostix_agent_bedrock_repo --region us-east-2 ^
  --image-scanning-configuration scanOnPush=true --image-tag-mutability MUTABLE --profile takara-instrument-admin

ECHO Push docker image to ECR
call docker push 160885287007.dkr.ecr.us-east-2.amazonaws.com/gostix_agent_bedrock_repo:latest

ECHO Create Lambda function
call aws lambda create-function --function-name gostix_agent_bedrock_lambda --package-type Image ^
  --code ImageUri=160885287007.dkr.ecr.us-east-2.amazonaws.com/gostix_agent_bedrock_repo:latest ^
  --role arn:aws:iam::160885287007:role/takara_instrument_lambda_role ^
  --profile takara-instrument-admin ^
  --architectures arm64 ^
  --memory-size 2048 ^
  --timeout 60
