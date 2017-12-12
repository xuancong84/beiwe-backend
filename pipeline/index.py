import json
import os

import boto3

from db.study_models import Studies
from db.user_models import Admin

# AJK TODO see about moving this out of the pipeline folder


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
    ssm_client = boto3.client('ssm', region_name='us-east-2')
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
        # Make a batch client in the Lambda's own region
        # AJK TODO get the region name for cron jobs (here and everywhere)
        client = boto3.client('batch', region_name='us-east-2')

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
            ]
        }
    )


def create_all_jobs(freq):
    """
    Create one AWS batch job for each Study object
    :param freq: string e.g. 'daily', 'manually'
    """
    
    # When this code was written (2017-12-11), AWS Lambda only provided boto3 version 1.4.7.
    # Version 1.4.8 has AWS Batch Array Jobs, which are extremely useful for the task this
    # functions performs. AWS Lambda now provides boto3 version 1.4.8, so we should switch to
    # using Array Jobs.
    # TODO switch to using Array Jobs ASAP
    print('Boto3 version: ' + boto3.__version__)
    
    # aws-object-names.json is in the same folder as index.py. This is meant to be run by an
    # AWS Lambda, so we can guarantee that fact.
    with open('aws-object-names.json') as fn:
        aws_object_names = json.load(fn)
    
    refresh_data_access_credentials(freq, aws_object_names)
    
    for study in Studies(deleted=False):
        # For each study, create a job
        object_id = study._id
        create_one_job(freq, object_id, aws_object_names)


def hourly(event, context):
    create_all_jobs('hourly')


def daily(event, context):
    create_all_jobs('daily')


def weekly(event, context):
    create_all_jobs('weekly')


def monthly(event, context):
    create_all_jobs('monthly')
