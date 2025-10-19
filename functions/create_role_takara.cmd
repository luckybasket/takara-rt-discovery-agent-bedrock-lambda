ECHO Setup Lambda IAM role
call aws iam create-role ^
  --role-name takara_instrument_lambda_role ^
  --assume-role-policy-document file://trust_policy.json ^
  --profile takara-instrument-admin
ECHO Attach basic lambda policy to role
call aws iam attach-role-policy ^
  --role-name takara_instrument_lambda_role ^
  --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole ^
  --profile takara-instrument-admin
ECHO Add takara instrument policy to role
call aws iam put-role-policy ^
  --role-name takara_instrument_lambda_role ^
  --policy-name takara_instrument_lambda_policy ^
  --policy-document file://takara_instrument_lambda_policy_takara.json ^
  --profile takara-instrument-admin




