ECHO Build docker image
call docker build --platform linux/arm64 --provenance false -t qpcr_ge_analysis_image:latest .
call docker tag qpcr_ge_analysis_image:latest 039612858415.dkr.ecr.us-west-1.amazonaws.com/qpcr_ge_analysis_repo:latest

ECHO Authenticate docker and push image
call aws ecr get-login-password --region us-west-1 --profile takara-luckybasket-dev | docker login ^
  --username AWS --password-stdin 039612858415.dkr.ecr.us-west-1.amazonaws.com
call docker push 039612858415.dkr.ecr.us-west-1.amazonaws.com/qpcr_ge_analysis_repo:latest

ECHO Update function docker image
call aws lambda update-function-code --function-name qpcr_ge_analysis_lambda ^
  --image-uri 039612858415.dkr.ecr.us-west-1.amazonaws.com/qpcr_ge_analysis_repo:latest ^
  --profile takara-luckybasket-dev

