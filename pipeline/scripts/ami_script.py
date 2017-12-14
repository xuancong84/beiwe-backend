# TODO annotate all

import json
import os
from time import sleep

import boto3
from botocore.exceptions import ClientError

from boto_helpers import get_aws_object_names, get_configs_folder


def run():
    configs_folder = get_configs_folder()
    
    with open(os.path.join(configs_folder, 'ami-ec2-instance-props.json')) as fn:
        ami_ec2_instance_props_dict = json.load(fn)
    aws_object_names = get_aws_object_names()
    print('JSON loaded')
    
    ec2_client = boto3.client('ec2')
    resp = ec2_client.run_instances(**ami_ec2_instance_props_dict)
    ec2_instance_id = resp['Instances'][0]['InstanceId']
    print('EC2 instance created')

    print('Waiting for unencrypted AMI...')
    tries = 0
    while True:
        try:
            resp = ec2_client.create_image(
                InstanceId=ec2_instance_id,
                Name=aws_object_names['ami_name'] + '-unencrypted',
            )
        except ClientError:
            # In case the EC2 instance isn't ready yet
            tries += 1
            if tries > 10:
                raise
            sleep(1)
        else:
            break
    unencrypted_ami_id = resp['ImageId']
    print('Unencrypted AMI created')
    
    # TODO this doesn't work right away, put a try-except around it
    region_name = boto3.session.Session().region_name
    print('Waiting to encrypt AMI...')
    tries = 0
    while True:
        try:
            resp = ec2_client.copy_image(
                SourceImageId=unencrypted_ami_id,
                SourceRegion=region_name,
                Encrypted=True,
                Name=aws_object_names['ami_name'],
            )
        except ClientError:
            # In case the unencrypted AMI isn't ready yet
            tries += 1
            if tries > 10:
                raise
            sleep(1)
        else:
            break
    ami_id = resp['ImageId']
    print('Encrypted AMI created')
    
    ec2_client.terminate_instances(InstanceIds=[ec2_instance_id])
    ec2_client.deregister_image(ImageId=unencrypted_ami_id)
    
    return ami_id
