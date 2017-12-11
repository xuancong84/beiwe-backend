import json
import os
import urllib

import boto3


def create_one_job(freq, object_id, aws_object_names, client=None):
    """
    Create an AWS batch job
    :param freq: string e.g. 'daily', 'manually'
    :param object_id: string representing the Study object_id e.g. '56325d8297013e33a2e57736'
    :param aws_object_names: dict containing names for the job, job definition and job queue
    :param client: A boto3 client or None; if None, one will be created with implicit credentials
    """
    
    if client is None:
        # TODO pass region in via .json as well
        client = boto3.client('batch', region_name='us-east-2')

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
    
    # Get the list of all Study object_ids to pass to the Batch job
    keys = {'access_key': os.environ['access_key'], 'secret_key': os.environ['secret_key']}
    url = '{}/get-studies/v1'.format(os.environ['server_url'])
    data = urllib.urlencode(keys)
    resp = urllib.urlopen(url, data=data).read()
    object_id_list = list(json.loads(resp).keys())
    
    # aws-object-names.json is in the same folder as index.py. This is meant to be run by an
    # AWS lambda, so we can guarantee that.
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
