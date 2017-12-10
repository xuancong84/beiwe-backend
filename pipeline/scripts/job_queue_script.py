import json
from time import sleep

import boto3


def run(comp_env_role, comp_env_name, queue_name, job_defn_name):
    # Create a new IAM role for the compute environment
    with open('assume-batch-role.json') as fn:
        assume_batch_role_policy_json = json.dumps(json.load(fn))
    with open('batch-service-role.json') as fn:
        batch_role_policy_json = json.dumps(json.load(fn))
    with open('assume-ec2-role.json') as fn:
        assume_ec2_role_policy_json = json.dumps(json.load(fn))
    with open('batch-instance-role.json') as fn:
        ec2_role_policy_json = json.dumps(json.load(fn))
    with open('compute-env.json') as fn:
        compute_resources_dict = json.load(fn)
    with open('container-props.json') as fn:
        container_props_dict = json.load(fn)
    print('JSON loaded')
    
    iam_client = boto3.client('iam')
    resp = iam_client.create_role(
        RoleName=comp_env_role,
        AssumeRolePolicyDocument=assume_batch_role_policy_json,
    )
    comp_env_role_arn = resp['Role']['Arn']
    iam_client.put_role_policy(
        RoleName=comp_env_role,
        PolicyName='aws-batch-service-policy',  # This name isn't used anywhere else
        PolicyDocument=batch_role_policy_json,
    )
    print('Batch role created')
    
    instance_role = 'ecsInstanceRole'
    resp = iam_client.create_role(
        RoleName=instance_role,
        AssumeRolePolicyDocument=assume_ec2_role_policy_json,
    )
    instance_role_arn = resp['Role']['Arn']
    compute_resources_dict['instanceRole'] = instance_role_arn
    iam_client.put_role_policy(
        RoleName=instance_role,
        PolicyName='aws-ec2-service-policy',  # This name isn't used anywhere else
        PolicyDocument=ec2_role_policy_json,
    )
    print('Instance role created')
    
    # Create the batch compute environment
    batch_client = boto3.client('batch')
    batch_client.create_compute_environment(
        computeEnvironmentName=comp_env_name,
        type='MANAGED',
        computeResources=compute_resources_dict,
        serviceRole=comp_env_role_arn,
    )
    
    # Wait for the compute environment to be valid. If it is deemed invalid, exit
    print('Waiting for compute environment...')
    while True:
        resp = batch_client.describe_compute_environments(
            computeEnvironments=[comp_env_name],
        )
        status = resp['computeEnvironments'][0]['status']
        if status == 'VALID':
            break
        elif status == 'CREATING' or status == 'UPDATING':
            sleep(1)
            continue
        else:
            raise RuntimeError('Compute Environment is Invalid')
    print('Compute environment created')
    
    # Create the batch job queue
    batch_client.create_job_queue(
        jobQueueName=queue_name,
        priority=1,
        computeEnvironmentOrder=[{'order': 0, 'computeEnvironment': comp_env_name}],
    )
    print('Job queue created')
    
    # Define a job definition
    batch_client.register_job_definition(
        jobDefinitionName=job_defn_name,
        type='container',
        # TODO ensure the stuff in the JSON that is repo-specific is auto-generated (e.g. "image" here)
        containerProperties=container_props_dict,
    )
    print('Job definition created')


# For debugging only
if __name__ == '__main__':
    _comp_env_role = 'AWSBatchServiceRole'
    _comp_env_name = 'data-pipeline-env'
    _queue_name = 'data-pipeline-queue'
    _job_defn_name = 'data-pipeline-job-defn'
    run(
        _comp_env_role,
        _comp_env_name,
        _queue_name,
        _job_defn_name,
    )
