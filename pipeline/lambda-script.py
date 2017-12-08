# Create a new IAM role for the lambdas
# TODO add --description to stuff
import json
import subprocess

import boto3


lambda_role = 'data-pipeline-lambda-role'

with open('assume-lambda-role.json') as fn:
    assume_role_policy_json = json.dumps(json.load(fn))
with open('batch-access-role.json') as fn:
    role_policy_json = json.dumps(json.load(fn))

iam_client = boto3.client('iam')
resp = iam_client.create_role(
    RoleName=lambda_role,
    AssumeRolePolicyDocument=assume_role_policy_json,
)
lambda_role_arn = resp['Role']['Arn']
iam_client.put_role_policy(
    RoleName=lambda_role,
    PolicyName='batch-submit-policy',
    PolicyDocument=role_policy_json,
)
print('Lambda role created')
# TODO clean up batch-access.json, it has too much unnecessary stuff right now

# Zip up the code for the lambdas
subprocess.check_call(['zip', 'lambda-upload.zip', 'index.py'])
with open('lambda-upload.zip', 'rb') as fn:
   lambda_code_bytes = fn.read()
print('Lambda code zipped')

# Create the lambdas
lambda_client = boto3.client('lambda')
events_client = boto3.client('events')
# TODO add manual setup (probably direct API connection to batch w/o lambda)
schedule_list = ('hourly', 'daily', 'weekly', 'monthly')
cron_expr_list = ('19 * * * ? *', '36 4 * * ? *', '49 2 ? * SUN *', '2 1 19 * ? *')
for schedule, cron_expr in zip(schedule_list, cron_expr_list):
    resp = lambda_client.create_function(
        FunctionName='create-{}-batch-jobs'.format(schedule),
        Runtime='python3.6',
        Role=lambda_role_arn,
        Handler='index.{}'.format(schedule),
        Code={'ZipFile': lambda_code_bytes},
    )
    function_arn = resp['FunctionArn']
    resp = events_client.put_rule(
        Name='{}-trigger'.format(schedule),
        ScheduleExpression='cron({})'.format(cron_expr),
    )
    rule_arn = resp['RuleArn']
    lambda_client.add_permission(
        FunctionName='create-{}-batch-jobs'.format(schedule),
        StatementId='{}-events'.format(schedule),
        Action='lambda:invokeFunction',
        Principal='events.amazonaws.com',
        SourceArn=rule_arn,
    )
    events_client.put_targets(
        Rule='{}-trigger'.format(schedule),
        Targets=[{'Id': '1', 'Arn': function_arn}],
    )
    print('Lambda {} function created'.format(schedule))
