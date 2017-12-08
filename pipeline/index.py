import boto3

client = boto3.client('batch', region_name='us-east-2')


# TODO get a lot of these bits from other files
def createJob(freq):
    """
    Create a batch job on AWS
    :param freq: string e.g. 'daily', 'manually'
    """

    resp = client.submit_job(
        jobName='data-pipeline-{}-job'.format(freq),
        jobDefinition='data-pipeline-job-defn',
        jobQueue='data-pipeline-queue',
        containerOverrides={
            'command': [
                '/bin/bash',
                'runner.sh',
                'Beiwe-Analysis/Pipeline/{}'.format(freq),
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
