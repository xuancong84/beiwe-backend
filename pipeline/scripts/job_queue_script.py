"""
A script for creating a setup to run AWS Batch jobs: a compute environment, a job queue and a
job definition to use as a template for actual jobs.
"""

import json
import os.path
from time import sleep

import boto3

from boto_helpers import get_aws_object_names, get_configs_folder


def run(repo_uri, ami_id):
    """
    Run the code
    :param repo_uri: string, the URI of an existing AWS ECR repository.
    :param ami_id: string, the id of an existing AWS AMI.
    """
    
    # Load a bunch of JSON blobs containing policies and other things that boto3 clients
    # require as input.
    configs_folder = get_configs_folder()
    
    with open(os.path.join(configs_folder, 'assume-batch-role.json')) as fn:
        assume_batch_role_policy_json = json.dumps(json.load(fn))
    with open(os.path.join(configs_folder, 'batch-service-role.json')) as fn:
        batch_service_role_policy_json = json.dumps(json.load(fn))
    with open(os.path.join(configs_folder, 'assume-ec2-role.json')) as fn:
        assume_ec2_role_policy_json = json.dumps(json.load(fn))
    with open(os.path.join(configs_folder, 'batch-instance-role.json')) as fn:
        batch_instance_role_policy_json = json.dumps(json.load(fn))
    with open(os.path.join(configs_folder, 'compute-environment.json')) as fn:
        compute_environment_dict = json.load(fn)
    with open(os.path.join(configs_folder, 'container-props.json')) as fn:
        container_props_dict = json.load(fn)
    aws_object_names = get_aws_object_names()
    print('JSON loaded')
    
    # Grab the names from aws_object_names
    comp_env_role = aws_object_names['comp_env_role']
    comp_env_name = aws_object_names['comp_env_name']
    instance_profile = aws_object_names['instance_profile']
    
    # Create a new IAM role for the compute environment
    iam_client = boto3.client('iam')
    resp = iam_client.create_role(
        RoleName=comp_env_role,
        AssumeRolePolicyDocument=assume_batch_role_policy_json,
    )
    comp_env_role_arn = resp['Role']['Arn']
    iam_client.put_role_policy(
        RoleName=comp_env_role,
        PolicyName='aws-batch-service-policy',  # This name isn't used anywhere else
        PolicyDocument=batch_service_role_policy_json,
    )
    print('Batch role created')
    
    # Create an EC2 instance profile for the compute environment
    iam_client.create_role(
        RoleName=instance_profile,
        AssumeRolePolicyDocument=assume_ec2_role_policy_json,
    )
    iam_client.put_role_policy(
        RoleName=instance_profile,
        PolicyName='aws-batch-instance-policy',  # This name isn't used anywhere else
        PolicyDocument=batch_instance_role_policy_json,
    )
    resp = iam_client.create_instance_profile(
        InstanceProfileName=instance_profile,
    )
    instance_profile_arn = resp['InstanceProfile']['Arn']
    compute_environment_dict['instanceRole'] = instance_profile_arn
    iam_client.add_role_to_instance_profile(
        InstanceProfileName=instance_profile,
        RoleName=instance_profile,
    )
    print('Instance profile created')
    
    # Create the batch compute environment
    batch_client = boto3.client('batch')
    compute_environment_dict['imageId'] = ami_id
    batch_client.create_compute_environment(
        computeEnvironmentName=comp_env_name,
        type='MANAGED',
        computeResources=compute_environment_dict,
        serviceRole=comp_env_role_arn,
    )
    
    # The compute environment takes somewhere between 10 and 45 seconds to create. Until it
    # is created, we cannot create a job queue. So first, we wait until the compute environment
    # has finished being created.
    print('Waiting for compute environment...')
    while True:
        # Ping the AWS server for a description of the compute environment
        resp = batch_client.describe_compute_environments(
            computeEnvironments=[comp_env_name],
        )
        status = resp['computeEnvironments'][0]['status']
        
        if status == 'VALID':
            # If the compute environment is valid, we can proceed to creating the job queue
            break
        elif status == 'CREATING' or status == 'UPDATING':
            # If the compute environment is still being created (or has been created and is
            # now being modified), we wait one second and then ping the server again.
            sleep(1)
        else:
            # If the compute environment is invalid (or deleting or deleted), we cannot
            # continue with job queue creation. Raise an error and quit the script.
            raise RuntimeError('Compute Environment is Invalid')
    print('Compute environment created')
    
    # Create a batch job queue
    batch_client.create_job_queue(
        jobQueueName=aws_object_names['queue_name'],
        priority=1,
        computeEnvironmentOrder=[{'order': 0, 'computeEnvironment': comp_env_name}],
    )
    print('Job queue created')
    
    # Create a batch job definition
    container_props_dict['image'] = repo_uri
    container_props_dict['environment'] = [
        {
            'name': 'access_key_ssm_name',
            'value': aws_object_names['access_key_ssm_name'],
        },
        {
            'name': 'secret_key_ssm_name',
            'value': aws_object_names['secret_key_ssm_name'],
        },
        {
            'name': 'region_name',
            'value': aws_object_names['region_name'],
        },
        {
            'name': 'server_url',
            'value': aws_object_names['server_url'],
        },
    ]
    batch_client.register_job_definition(
        jobDefinitionName=aws_object_names['job_defn_name'],
        type='container',
        containerProperties=container_props_dict,
    )
    print('Job definition created')
