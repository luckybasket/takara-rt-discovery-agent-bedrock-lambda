ECHO Build docker image
call docker build --platform linux/arm64 --provenance false -t qpcr_ge_analysis_image:latest .
call docker tag qpcr_ge_analysis_image:latest 039612858415.dkr.ecr.us-west-1.amazonaws.com/qpcr_ge_analysis_repo:latest

ECHO Authenticate docker to ECR
call aws ecr get-login-password --region us-west-1 --profile takara-luckybasket-admin | docker login ^
  --username AWS --password-stdin 039612858415.dkr.ecr.us-west-1.amazonaws.com

ECHO Create ECR repo
call aws ecr create-repository --repository-name qpcr_ge_analysis_repo --region us-west-1 ^
  --image-scanning-configuration scanOnPush=true --image-tag-mutability MUTABLE --profile takara-luckybasket-admin

ECHO Push docker image to ECR
call docker push 039612858415.dkr.ecr.us-west-1.amazonaws.com/qpcr_ge_analysis_repo:latest

ECHO Create Lambda function
call aws lambda create-function --function-name qpcr_ge_analysis_lambda --package-type Image ^
  --code ImageUri=039612858415.dkr.ecr.us-west-1.amazonaws.com/qpcr_ge_analysis_repo:latest ^
  --role arn:aws:iam::039612858415:role/takara_instrument_lambda_role ^
  --profile takara-luckybasket-admin ^
  --architectures arm64 ^
  --memory-size 4096 ^
  --timeout 60
