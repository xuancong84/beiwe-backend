import json

import boto3
import requests

client = boto3.client('batch', region_name='us-east-2')
# TODO this is getting relocated to somewhere that the normal frontend can access it
with open('aws-object-names.json') as fn:
    object_names = json.load(fn)


def createJob(freq):
    """
    Create a batch job on AWS
    :param freq: string e.g. 'daily', 'manually'
    """
    
    # TODO should /list-all-studies require permissions? If so, the lambda needs them.
    # TODO get the correct URL (https://beiwe-whatever.com)
    resp = requests.get('http://localhost:8080/list-all-study-ids')
    object_id_list = json.loads(resp.content)['study_ids']
    
    for object_id in object_id_list:
        # TODO make a function common between this and run_manual_code to reduce redundancy
        client.submit_job(
            jobName=object_names['job_name'].format(freq=freq),
            jobDefinition=object_names['job_defn_name'],
            jobQueue=object_names['queue_name'],
            containerOverrides={
                'command': [
                    '/bin/bash',
                    'runner.sh',
                    'Beiwe-Analysis/Pipeline/{}'.format(freq),
                    object_id,
                ]
            }
        )


def hourly(event, context):
    createJob('hourly')


def daily(event, context):
    createJob('daily')


def weekly(event, context):
    createJob('weekly')


def monthly(event, context):
    createJob('monthly')


def manually(event, context):
    createJob('manually')
