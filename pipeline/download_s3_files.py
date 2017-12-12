import os

# TODO put these in the Dockerfile
import boto3
import requests


access_key_ssm_name = os.getenv('access_key_ssm_name')
secret_key_ssm_name = os.getenv('secret_key_ssm_name')
study_object_id = os.getenv('study_object_id')

# Get the necessary credentials for pinging the Beiwe server
ssm_client = boto3.client('ssm', region_name=os.environ['AWS_REGION'])
access_key = ssm_client.get_parameter(
    Name=access_key_ssm_name,
    WithDecryption=True,
)['Parameter']['Value']
secret_key = ssm_client.get_parameter(
    Name=secret_key_ssm_name,
    WithDecryption=True,
)['Parameter']['Value']

# TODO softcode this
base_url = 'https://staging.beiwe.org'
data_access_api_url = '{}/get-data/v1'.format(base_url)

payload = {
    'access_key': access_key,
    'secret_key': secret_key,
    'study_id': study_object_id,
}
requests.post(data_access_api_url, data=payload)
# TODO save the .zip file
