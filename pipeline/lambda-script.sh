#!/bin/bash
# Ensure the stuff does not already exist
# TODO this is probably bad form in production?
# TODO get the deletion and detaching to work
#aws iam detach-role-policy \
#  --role-name data-pipeline-lambda-role \
#  --policy-arn
#aws iam delete-policy \
#  --policy-name batch-submit-policy
aws iam delete-role \
  --role-name data-pipeline-lambda-role
aws events remove-targets \
  --rule hourly \
  --ids "1"
aws events delete-rule \
  --name hourly
aws lambda delete-function \
  --function-name createHourlyBatchJobs

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
aws lambda create-function \
  --function-name createHourlyBatchJobs \
  --runtime python3.6 \
  --role arn:aws:iam::284616134063:role/data-pipeline-lambda-role \
  --handler index.hourly \
  --zip-file fileb://lambda-upload.zip
aws events put-rule \
  --name hourly \
  --schedule-expression "cron(19 * * * ? *)"
aws lambda add-permission \
  --function-name createHourlyBatchJobs \
  --statement-id hourly-events \
  --action lambda:invokeFunction \
  --principal events.amazonaws.com \
  --source-arn arn:aws:events:us-east-2:284616134063:rule/hourly
aws events put-targets \
  --rule hourly \
  --targets "Id"="1","Arn"="arn:aws:lambda:us-east-2:284616134063:function:createHourlyBatchJobs"
