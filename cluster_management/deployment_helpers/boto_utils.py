# Todo:
# we are not making them a vpc, they have to provide it.  regular vpc.  Regular internet gateways.
# create eb
# create sec groups for data processing servers
# create rabbitmq servers
# create data processing servers
from logging import DEBUG

import boto3
from deployment_helpers.general_utils import retry, log
from deployment_helpers.eb_server_configuration import *

log.setLevel(DEBUG)

OUR_CUSTOM_POLICY_ARN= 'arn:aws:iam::284616134063:policy/AutomationPolicy'

BEIWE_APPLICATION_NAME = "beiwe-application"
BEIWE_ENVIRONMENT_NAME = "beiwe-environment"

class PythonPlatformDiscoveryError(Exception): pass

##
## Boto3 accessors
##

def create_ec2_client():
    """ connect to a boto3 ec2 CLIENT in the appropriate region. """
    return boto3.resource(
            "ec2",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
    )


def create_ec2_resource():
    """ connect to a boto3 ec2 CLIENT in the appropriate region. """
    return boto3.resource(
            "ec2",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION
    )


def create_eb_client():
    return boto3.client(
           'elasticbeanstalk',
           aws_access_key_id=AWS_ACCESS_KEY_ID,
           aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
           region_name=AWS_REGION
    )

##
## Data Accessors
##

def get_python27_platform_arn():
    """ gets the most recent platform arm for a python 2.7 elastic beanstalk cluster. """
    eb_client = create_eb_client()
    platforms = []
    for platform in eb_client.list_platform_versions()['PlatformSummaryList']:
        if (platform.get('PlatformCategory', None) == 'Python' and
                    "2.7" in platform.get('PlatformArn', [])):
            platforms.append(platform['PlatformArn'])
    
    if len(platforms) == 0:
        raise PythonPlatformDiscoveryError("could not find python 2.7 platform")
    if len(platforms) > 1:
        raise PythonPlatformDiscoveryError(
            "encountered multiple python 2.7 platforms: %s" % platforms)
    if len(platforms) == 1:
        return platforms[0]


def get_running_environment():
    eb_client = create_eb_client()
    environments = eb_client.describe_environments()['Environments']
    for environment in environments:
        environment_name = environment.get('EnvironmentName', None)
        print "found environment", environment_name
        print BEIWE_ENVIRONMENT_NAME.lower()
        if environment_name and BEIWE_ENVIRONMENT_NAME.lower() in environment_name.lower():
            log.info('Using Elastic Beanstalk environment named "%s."' % environment_name)
            if environment['Health'] == 'Grey':
                log.info("but it was not running")
                continue
            return environment
    return None
##
## creation functions
##

def create_sec_groups():
    pass
    """
    celery workers need to connect to rabbitmq, postgres
    postgres needs to allow rabbitmq server, celery workers, eb servers
    rabbitmq needs to allow workers
    """
 

def get_or_create_eb_application():
    """
    doc:
    https://docs.aws.amazon.com/elasticbeanstalk/latest/api/API_CreateApplication.html
    """
    eb_client = create_eb_client()
    
    applications = eb_client.describe_applications().get('Applications', None)
    for app in applications:
        app_name = app.get('ApplicationName', None)
        if app_name and BEIWE_APPLICATION_NAME in app_name.lower():
            log.info('Using Elastic Beanstalk application named "%s."' % app_name)
            return app_name
        
    # raise Exception("no beiwe applications found")
    return eb_client.create_application(
            ApplicationName=BEIWE_APPLICATION_NAME,
            Description='Your Beiwe Application',
            ResourceLifecycleConfig={
                'ServiceRole': OUR_CUSTOM_POLICY_ARN,
                # The ARN of an IAM service role that Elastic Beanstalk has permission to assume
                'VersionLifecycleConfig': {
                    'MaxCountRule': {
                        'Enabled': False,
                        'MaxCount': 1000,  # should be ignored
                        'DeleteSourceFromS3': True
                    },
                    'MaxAgeRule': {
                        'Enabled': False,
                        'MaxAgeInDays': 1000,  # should be ignored
                        'DeleteSourceFromS3': True
                    }
                }
            }
    )





    
def get_or_create_eb_environment():
    """
    
    documentation:
    https://docs.aws.amazon.com/elasticbeanstalk/latest/api/API_CreateEnvironment.html
    """
    eb_client = create_eb_client()
    
    app = get_or_create_eb_application()
    env = get_running_environment()
    if env is None:
        print "creating new environment"
        options = []
        # options.extend(aws_credentials)
        # options.extend(db_credentials)
        # options.extend(env_variables)
        # options.extend(sentry_dsns)
        # options.extend(generated_by_us)
        # options.extend(optional)
        # discovered
        
        env = eb_client.create_environment(
                ApplicationName=BEIWE_APPLICATION_NAME,
                EnvironmentName=BEIWE_ENVIRONMENT_NAME,
                Description='elastic beanstalk beiwe cluster',
                PlatformArn=get_python27_platform_arn(),
                OptionSettings=options
                # VersionLabel='string',  # this will probably be required later
            
                # OptionSettings=[  # appears to be configuration settings
                #     {
                #         'ResourceName': 'string',
                #         'Namespace': 'string',
                #         'OptionName': 'string',
                #         'Value': 'string'
                #     },
                # ],
                
                # OptionsToRemove=[  # a different form of configuration management
                #     {
                #         'ResourceName': 'string',
                #         'Namespace': 'string',
                #         'OptionName': 'string'
                #     },
                # ]
                
                # Tags=[ # optional
                #     {
                #         'Key': 'string',
                #         'Value': 'string'
                #     },
                # ],
                
                # GroupName='string',  # for use in other methods of eb configuration
                
                # CNAMEPrefix='string',  # not required
                # Tier={  # optional
                #     'Name': 'string',
                #     'Type': 'string',
                #     'Version': 'string'
                # },
                
                # TemplateName='string',  # nope
                # SolutionStackName='string', # more about templates
        )
        
    from pprint import pprint
    pprint (env)