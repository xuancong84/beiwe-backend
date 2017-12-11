import json

import boto3
import requests


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
    
    # TODO should /list-all-studies require permissions? If so, the lambda needs them.
    # TODO get the correct URL (https://beiwe-whatever.com)
    # Get the list of all Study object_ids to pass to the Batch job
    resp = requests.get('http://localhost:8080/list-all-study-ids')
    object_id_list = json.loads(resp.content)['study_ids']
    
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
