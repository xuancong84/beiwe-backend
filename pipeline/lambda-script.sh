#!/bin/bash
# Create a new IAM role for the lambdas
# TODO add --description to stuff
aws iam create-role \
  --role-name data-pipeline-lambda-role \
  --assume-role-policy-document file://assume-lambda-role.json
# TODO clean up batch-access.json, it has too much unnecessary stuff right now
aws iam put-role-policy \
  --role-name data-pipeline-lambda-role \
  --policy-name batch-submit-policy \
  --policy-document file://batch-access.json


# Create the lambdas
zip lambda-upload.zip index.py
# TODO see if this can be done in only two or one lambdas instead of five
# TODO autogenerate the ARN
SCHEDULES='hourly daily weekly monthly'
for sch in $SCHEDULES; do
  aws lambda create-function \
    --function-name create-$sch-batch-jobs \
    --runtime python3.6 \
    --role arn:aws:iam::284616134063:role/data-pipeline-lambda-role \
    --handler index.$sch \
    --zip-file fileb://lambda-upload.zip
  aws events put-rule \
    --name $sch-trigger \
    --schedule-expression "cron(19 * * * ? *)"
  # TODO fix the schedule expression
  aws lambda add-permission \
    --function-name create-$sch-batch-jobs \
    --statement-id $sch-events \
    --action lambda:invokeFunction \
    --principal events.amazonaws.com \
    --source-arn arn:aws:events:us-east-2:284616134063:rule/$sch
  aws events put-targets \
    --rule $sch-trigger \
    --targets "Id"="1","Arn"="arn:aws:lambda:us-east-2:284616134063:function:create-$sch-batch-jobs"
done
