from db.study_models import Studies
from db.user_models import Admin
from pipeline.boto_helpers import get_aws_object_names, get_boto_client


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
    ssm_client = get_boto_client('ssm')
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


def create_one_job(freq, object_id, aws_object_names=None, client=None):
    """
    Create an AWS batch job
    The aws_object_names and client parameters are optional. They are provided in case
    that this function is run as part of a loop, to avoid an unnecessarily large number of
    file operations or API calls.
    :param freq: string e.g. 'daily', 'manually'
    :param object_id: string representing the Study object_id e.g. '56325d8297013e33a2e57736'
    :param aws_object_names: dict containing various parameters for the batch job or None
    :param client: a credentialled boto3 client or None
    """
    
    # Get the AWS parameters and client if not provided
    if aws_object_names is None:
        aws_object_names = get_aws_object_names()
    if client is None:
        client = get_boto_client('batch')

    client.submit_job(
        jobName=aws_object_names['job_name'].format(freq=freq),
        jobDefinition=aws_object_names['job_defn_name'],
        jobQueue=aws_object_names['queue_name'],
        containerOverrides={
            'environment': [
                {
                    'name': 'study_object_id',
                    'value': object_id,
                },
                {
                    'name': 'FREQ',
                    'value': freq,
                },
            ],
        },
    )


def create_all_jobs(freq):
    """
    Create one AWS batch job for each Study object
    :param freq: string e.g. 'daily', 'monthly'
    """
    
    # Boto3 version 1.4.8 has AWS Batch Array Jobs, which are extremely useful for the
    # task this function performs. We should switch to using them.
    # TODO switch to using Array Jobs ASAP
    
    aws_object_names = get_aws_object_names()
    
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
