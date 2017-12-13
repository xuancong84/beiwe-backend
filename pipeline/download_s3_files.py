#!/usr/bin/python3
import os

import boto3
import requests


# Grab environment variables
access_key_ssm_name = os.getenv('access_key_ssm_name')
secret_key_ssm_name = os.getenv('secret_key_ssm_name')
study_object_id = os.getenv('study_object_id')
region_name = os.getenv('region_name')
server_url = os.getenv('server_url')

# Get the necessary credentials for pinging the Beiwe server
ssm_client = boto3.client('ssm', region_name=region_name)
resp = ssm_client.get_parameters(
    Names=(access_key_ssm_name, secret_key_ssm_name),
    WithDecryption=True,
)['Parameters']
access_key, secret_key = [p['Value'] for p in resp]

# TODO softcode this
data_access_api_url = '{}/get-data/v1'.format(server_url)

payload = {
    'access_key': access_key,
    'secret_key': secret_key,
    'study_id': study_object_id,
}
requests.post(data_access_api_url, data=payload)
# TODO save the .zip file
