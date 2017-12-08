# Create a new IAM role for the lambdas
# TODO add --description to stuff
import subprocess

import boto3


lambda_role = 'data-pipeline-lambda-role'

iam_client = boto3.client('iam')
resp = iam_client.create_role(
    RoleName=lambda_role,
    AssumeRolePolicyDocument='file://assume-lambda-role.json',
)
lambda_role_arn = resp['Role']['Arn']
iam_client.put_role_policy(
    RoleName=lambda_role,
    PolicyName='batch-submit-policy',
    PolicyDocument='file://batch-access.json',
)
# TODO running into issues here (12/07)
# TODO clean up batch-access.json, it has too much unnecessary stuff right now

# Create the lambdas
subprocess.check_call('zip lambda-upload.zip index.py')
lambda_client = boto3.client('lambda')
events_client = boto3.client('events')
# TODO see if this can be done in only two or one lambdas instead of five
# TODO add manual setup (probably direct API connection to batch w/o lambda)
schedule_list = ('hourly', 'daily', 'weekly', 'monthly')
cron_expr_list = ('19 * * * ? *', '36 4 * * ? *', '49 2 ? * SUN *', '2 1 19 * ? *')
for schedule, cron_expr in zip(schedule_list, cron_exp_list):
    resp = lambda_client.create_function(
        FunctionName='create-{}-batch-jobs'.format(schedule),
        Runtime='python3.6',
        Role=lambda_role_arn,
        Handler='index.{}'.format(schedule),
        Code={'ZipFile': 'fileb://lambda-upload.zip'},
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
