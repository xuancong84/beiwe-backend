import json
import os
import urllib

import boto3

from datetime import datetime


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
        client = boto3.client('batch', region_name=os.environ['AWS_REGION'])

    client.submit_job(
        jobName=aws_object_names['job_name'].format(freq=freq),
        jobDefinition=aws_object_names['job_defn_name'],
        jobQueue=aws_object_names['queue_name'],
        containerOverrides={
            'command': [
                '/bin/bash',
                'runner.sh',
                'Beiwe-Analysis/Pipeline/{}'.format(freq),
                object_id,
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
    # functions performs. As such, this print statement is here to alert the user if AWS
    # Lambda has upgraded to version 1.4.8, at which time we should switch to using Array Jobs.
    # TODO switch to using Array Jobs when possible
    print('Boto3 version: ' + boto3.__version__)
    
    # Get the list of all Study object_ids to pass to the Batch job
    keys = {'access_key': os.environ['access_key'], 'secret_key': os.environ['secret_key']}
    url = '{}/get-studies/v1'.format(os.environ['server_url'])
    data = urllib.urlencode(keys)
    resp = urllib.urlopen(url, data=data).read()
    object_id_list = list(json.loads(resp).keys())
    
    # aws-object-names.json is in the same folder as index.py. This is meant to be run by an
    # AWS Lambda, so we can guarantee that fact.
    with open('aws-object-names.json') as fn:
        aws_object_names = json.load(fn)
    
    for object_id in object_id_list:
        # For each object_id, create a job
        create_one_job(freq, object_id, aws_object_names)


def hourly(event, context):
    create_all_jobs('hourly')


def daily(event, context):
    create_all_jobs('daily')


def weekly(event, context):
    create_all_jobs('weekly')


def monthly(event, context):
    create_all_jobs('monthly')
