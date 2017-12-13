import json

import boto3

from config.secure_settings import AWS_SECRET_ACCESS_KEY, AWS_ACCESS_KEY_ID
from db.study_models import Studies
from db.user_models import Admin


# AJK TODO annotate
def refresh_data_access_credentials(freq, aws_object_names):
    admin_name = 'BATCH USER {}'.format(freq)
    mock_admin = Admin(admin_name)
    if not mock_admin:
        mock_admin = Admin.create_without_password(admin_name)
        for study in Studies():
            study.add_admin(mock_admin._id)
    
    access_key, secret_key = mock_admin.reset_access_credentials()

    # Get the necessary credentials for pinging the Beiwe server
    ssm_client = boto3.client(
        'ssm',
        region_name='us-east-2',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )
    ssm_client.put_parameter(
        Name=aws_object_names['access_key_ssm_name'],
        Value=access_key,
        Type='SecureString',
        Overwrite=True,
    )
    ssm_client.put_parameter(
        Name=aws_object_names['secret_key_ssm_name'],
        Value=secret_key,
        Type='SecureString',
        Overwrite=True,
    )


def create_one_job(freq, object_id, aws_object_names, client=None):
    """
    Create an AWS batch job
    :param freq: string e.g. 'daily', 'manually'
    :param object_id: string representing the Study object_id e.g. '56325d8297013e33a2e57736'
    :param aws_object_names: dict containing names for the job, job definition and job queue
    :param client: A boto3 client or None; if None, one will be created with implicit credentials
    """
    
    if client is None:
        # AJK TODO get the region name for cron jobs (here and everywhere)
        client = boto3.client(
            'batch',
            region_name='us-east-2',
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        )

    client.submit_job(
        jobName=aws_object_names['job_name'].format(freq=freq),
        jobDefinition=aws_object_names['job_defn_name'],
        jobQueue=aws_object_names['queue_name'],
        containerOverrides={
            'command': [
                '/bin/bash',
                'runner.sh',
                freq,
            ],
            'environment': [
                # AJK TODO pass the server url also
                # AJK TODO maybe put these in the job definition?
                {
                    'name': 'access_key_ssm_name',
                    'value': aws_object_names['access_key_ssm_name'],
                },
                {
                    'name': 'secret_key_ssm_name',
                    'value': aws_object_names['secret_key_ssm_name'],
                },
                {
                    'name': 'study_object_id',
                    'value': object_id,
                },
                # AJK TODO softcode
                {
                    'name': 'region_name',
                    'value': 'us-east-2',
                },
                {
                    'name': 'server_url',
                    'value': 'https://staging.beiwe.org'
                }
            ]
        }
    )


def create_all_jobs(freq):
    """
    Create one AWS batch job for each Study object
    :param freq: string e.g. 'daily', 'manually'
    """
    
    # Boto3 version 1.4.8 has AWS Batch Array Jobs, which are extremely useful for the
    # task this function performs. We should switch to using them.
    # TODO switch to using Array Jobs ASAP
    print('Boto3 version: ' + boto3.__version__)
    
    with open('pipeline/configs/aws-object-names.json') as fn:
        aws_object_names = json.load(fn)
    
    refresh_data_access_credentials(freq, aws_object_names)
    
    for study in Studies(deleted=False):
        # For each study, create a job
        object_id = str(study._id)
        create_one_job(freq, object_id, aws_object_names)


# TODO establish cron jobs to call these
# I've been using ('19 * * * ? *', '36 4 * * ? *', '49 2 ? * SUN *', '2 1 1 * ? *') up til now
def hourly():
    create_all_jobs('hourly')


def daily():
    create_all_jobs('daily')


def weekly():
    create_all_jobs('weekly')


def monthly():
    create_all_jobs('monthly')
