import boto3

client = boto3.client('batch', region_name='us-east-2')

def hourly(*args, **kwargs):
    resp = client.submit_job(
        jobName='beiwe-test-batch-0-1',
        jobDefinition='beiwe-test-batch-0:1',
        jobQueue='beiwe-test-batch-0',
        containerOverrides={
            'command': [
                'echo',
                '\'hello world\'',
            ]
        }
    )
