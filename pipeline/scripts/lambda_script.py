import json
import subprocess
from time import sleep

import boto3
from botocore.exceptions import ClientError

# Create a new IAM role for the lambdas
# TODO add --description to stuff


def run(lambda_role, function_name, rule_name):
    # Load JSON files to pass to the clients
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
        PolicyName='batch-submit-policy',  # This name isn't used anywhere else
        PolicyDocument=role_policy_json,
    )
    print('Lambda role created')
    
    # Zip up the code for the lambdas
    subprocess.check_call(['zip', 'lambda-upload.zip', 'index.py'])
    subprocess.check_call(['zip', 'lambda-upload.zip', 'aws-object-names.json'])
    with open('lambda-upload.zip', 'rb') as fn:
        lambda_code_bytes = fn.read()
    print('Lambda code zipped')
    
    # Create the lambdas
    lambda_client = boto3.client('lambda')
    events_client = boto3.client('events')
    # TODO add manual setup (probably direct API connection to batch w/o lambda)
    schedule_list = ('hourly', 'daily', 'weekly', 'monthly')
    cron_expr_list = ('19 * * * ? *', '36 4 * * ? *', '49 2 ? * SUN *', '2 1 19 * ? *')
    print('Creating lambda functions...')
    for schedule, cron_expr in zip(schedule_list, cron_expr_list):
        tries = 0
        while True:
            try:
                resp = lambda_client.create_function(
                    FunctionName=function_name.format(freq=schedule),
                    Runtime='python3.6',
                    Role=lambda_role_arn,
                    Handler='index.{}'.format(schedule),
                    Code={'ZipFile': lambda_code_bytes},
                )
            except ClientError:
                # TODO be more specific, this should only try again for that one weird error
                tries += 1
                if tries > 30:
                    raise
                sleep(1)
            else:
                break
        
        function_arn = resp['FunctionArn']
        resp = events_client.put_rule(
            Name=rule_name.format(freq=schedule),
            ScheduleExpression='cron({})'.format(cron_expr),
        )
        rule_arn = resp['RuleArn']
        lambda_client.add_permission(
            FunctionName=function_name.format(freq=schedule),
            StatementId='{}-events'.format(schedule),  # This name isn't used anywhere else
            Action='lambda:invokeFunction',
            Principal='events.amazonaws.com',
            SourceArn=rule_arn,
        )
        events_client.put_targets(
            Rule=rule_name.format(freq=schedule),
            Targets=[{'Id': '1', 'Arn': function_arn}],
        )
        print('Lambda {} function created'.format(schedule))
