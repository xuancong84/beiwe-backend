import json
import os.path
import subprocess

import boto3

# This is all cribbed from the django branch's cluster_management/deployment_helpers folder
# TODO once the branches are merged, use that code and NOT this code


def get_aws_object_names():
    configs_folder = get_configs_folder()
    with open(os.path.join(configs_folder, 'aws-object-names.json')) as fn:
        return json.load(fn)


def get_boto_client(client_type):
    from config.settings import AWS_SECRET_ACCESS_KEY, AWS_ACCESS_KEY_ID

    aws_object_names = get_aws_object_names()
    
    return boto3.client(
        client_type,
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=aws_object_names['region_name'],
    )


def get_pipeline_folder():
    return os.path.abspath(__file__).rsplit('/', 1)[0]


def get_configs_folder():
    return os.path.join(get_pipeline_folder(), 'configs')


def set_default_region():
    aws_object_names = get_aws_object_names()
    region_name = aws_object_names['region_name']
    subprocess.check_call(['aws', 'configure', 'set', 'default.region', region_name])
