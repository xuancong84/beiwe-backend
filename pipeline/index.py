import boto3

client = boto3.client('batch', region_name='us-east-2')

def createJob(freq):
    """
    Create a batch job on AWS
    :param freq: string e.g. 'daily', 'manually'
    """

    resp = client.submit_job(
        jobName='beiwe-test-batch-1-3',
        jobDefinition='beiwe-test-batch-0:2',
        jobQueue='beiwe-test-batch-2',
        containerOverrides={
            'command': [
                '/bin/bash',
                'runner.sh',
                'Beiwe-Analysis/Pipeline/{}'.format(freq),
            ]
        }
    )


def hourly():
    createJob('hourly')


def daily():
    createJob('daily')


def weekly():
    createJob('weekly')


def monthly():
    createJob('monthly')


def manually():
    createJob('manually')
