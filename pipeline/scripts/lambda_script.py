"""
A script for creating some AWS lambdas and some AWS CloudWatch event triggers to run the lambdas
"""

import json
import subprocess
from time import sleep

import boto3
from botocore.exceptions import ClientError


def run(lambda_role, function_name, rule_name):
    """
    Run the code.
    The lambda_role parameter can be an arbitrary string. The function_name and rule_name
    parameters are going to have .format called on them, so they should each be a string in
    which {freq} appears at least once. If they do not have {freq}, AWS will raise an error
    complaining that we are trying to create multiple lambdas with the same name.
    """
    
    # Load a bunch of JSON blobs containing policies, which boto3 clients require as input
    with open('assume-lambda-role.json') as fn:
        assume_lambda_role_policy_json = json.dumps(json.load(fn))
    with open('batch-access-role.json') as fn:
        batch_access_role_policy_json = json.dumps(json.load(fn))
    
    # Create a new IAM role for the lambdas
    iam_client = boto3.client('iam')
    resp = iam_client.create_role(
        RoleName=lambda_role,
        AssumeRolePolicyDocument=assume_lambda_role_policy_json,
    )
    lambda_role_arn = resp['Role']['Arn']
    iam_client.put_role_policy(
        RoleName=lambda_role,
        PolicyName='batch-submit-policy',  # This name isn't used anywhere else
        PolicyDocument=batch_access_role_policy_json,
    )
    print('Lambda role created')
    
    # Zip up the code for the lambdas. We use the command line zip executable to perform the
    # actual zipping, and then we open the zip file in memory to pass the BytesIO object to
    # the boto3 client.
    subprocess.check_call(['zip', 'lambda-upload.zip', 'index.py'])
    subprocess.check_call(['zip', 'lambda-upload.zip', 'aws-object-names.json'])
    with open('lambda-upload.zip', 'rb') as fn:
        lambda_code_bytes = fn.read()
    print('Lambda code zipped')
    
    # Create the lambdas
    lambda_client = boto3.client('lambda')
    events_client = boto3.client('events')
    # TODO add manual setup (probably direct API connection to batch w/o lambda)
    # We create one lambda for each for four schedules, as well as a trigger to run each
    # lambda. Each trigger has an associated cron expression that causes it to run at certain
    # times. See http://docs.aws.amazon.com/AmazonCloudWatch/latest/events/ScheduledEvents.html
    # for explanation and examples.
    schedule_list = ('hourly', 'daily', 'weekly', 'monthly')
    cron_expr_list = ('19 * * * ? *', '36 4 * * ? *', '49 2 ? * SUN *', '2 1 1 * ? *')
    print('Creating lambda functions...')
    for schedule, cron_expr in zip(schedule_list, cron_expr_list):
        tries = 0
        while True:
            # For some reason, there is a ~10-second interval between creating the lambda
            # role and being able to create the lambda successfully. During that interval,
            # attempting to create a lambda will raise an InvalidParameterValueException.
            # For that reason, we try creating the lambda repeatedly.
            try:
                resp = lambda_client.create_function(
                    FunctionName=function_name.format(freq=schedule),
                    Runtime='python3.6',
                    Role=lambda_role_arn,
                    Handler='index.{}'.format(schedule),
                    Code={'ZipFile': lambda_code_bytes},
                )
            except ClientError:
                # If the lambda is not created due to the timeout error, we wait one second
                # and try again. If there is some other error, this except clause will not
                # catch it, and it will be raised and stop the code from executing.
                tries += 1
                if tries > 30:
                    # If the lambda has not been successfully created after 30 seconds, give up
                    raise
                sleep(1)
            else:
                # Once we have successfully created the lambda, exit the loop and proceed
                break
        
        # Create a trigger (rule) and attach it to our lambda. This requires two actions: the
        # lambda must grant the trigger permission to invoke it, and the trigger must attach
        # itself to the lambda.
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
