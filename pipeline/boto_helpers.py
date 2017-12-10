import json

import boto3

# This is all cribbed from the django branch's cluster_management/deployment_helpers folder
# TODO once the branches are merged, use that code and NOT this code


def get_aws_config():
    with open('pipeline/aws-config.json') as fn:
        return json.load(fn)


def get_boto_client(client_type):
    aws_config = get_aws_config()
    
    return boto3.client(
        client_type,
        aws_access_key_id=aws_config["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=aws_config["AWS_SECRET_ACCESS_KEY"],
        region_name=aws_config["AWS_REGION"],
    )
