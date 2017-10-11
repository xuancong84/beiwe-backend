# Todo:
# we are not making them a vpc, they have to provide it.  regular vpc.  Regular internet gateways.
# create eb
# create sec groups for data processing servers
# create rabbitmq servers
# create data processing servers
from copy import deepcopy
from pprint import pprint, pformat
from time import sleep

from deployment_helpers.aws.iam import (iam_find_role, IamEntityMissingError, iam_create_role,
    iam_attach_role_policy, iam_find_instance_profile, PythonPlatformDiscoveryError,
    EnvironmentDeploymentFailure)

from deployment_helpers.aws.boto_helpers import (create_ec2_client, create_iam_client,
    create_eb_client)
from deployment_helpers.constants import (ELASTICBEANSTALK_ASSUME_ROLE_POLICY_DOCUMENT_PATH,
    OUR_CUSTOM_POLICY_ARN, ELASTICBEANSTALK_SERVICE_ROLE,
    ELASTICBEANSTALK_INSTANCE_PROFILE_ROLE, BEIWE_ENVIRONMENT_NAME, BEIWE_APPLICATION_NAME,
    INSTANCE_ASSUME_ROLE_POLICY_DOCUMENT_PATH, ELASTICBEANSTALK_INSTANCE_PROFILE_NAME)
from deployment_helpers.general_utils import retry, log


##
## Local data accessors
##


def construct_eb_environment_variables():
    """ get and return a _copy_ of the evironment variables for elastic beanstalk. """
    # We don't want these as global variables, and we don't want to modify references.
    from deployment_helpers.aws.elastic_beanstalk_configuration import configuration
    # environment_variables = []
    # environment_variables.extend(deepcopy(raw_environment_variables))
    # environment_variables.extend(deepcopy(deployment_configuration))
    environment_variables = deepcopy(configuration)
    for env_var in environment_variables:
        if env_var["OptionName"] == "ServiceRole":
            env_var['Value'] = get_or_create_eb_service_role()['Arn']
        elif env_var["OptionName"] == "IamInstanceProfile":
            env_var['Value'] = get_or_create_eb_instance_profile()['Arn']
    return environment_variables

def get_elasticbeanstalk_assume_role_policy_document():
    with open(ELASTICBEANSTALK_ASSUME_ROLE_POLICY_DOCUMENT_PATH) as document:
        return document.read()

def get_instance_assume_role_policy_document():
    with open(INSTANCE_ASSUME_ROLE_POLICY_DOCUMENT_PATH) as document:
        return document.read()


##
## AWS Accessors
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
    first_hit = None
    for environment in environments:
        environment_name = environment.get('EnvironmentName', None)
        if environment_name and BEIWE_ENVIRONMENT_NAME.lower() in environment_name.lower():
            log.info('Found Elastic Beanstalk environment named "%s..."' % environment_name)
            if environment['Health'] == 'Grey':
                log.info("but it is terminated")
                continue
            if first_hit is None:
                first_hit = environment
            else:
                log.warn("encountered multiple valid beiwe environments, using first one.")
                
    if first_hit is None:
        log.warn("could not find any Beiwe Elastic Beanstalk environments")
    return first_hit


##
## creation functions
##



def get_or_create_eb_service_role():
    """ This function creates the appropriate roles that apply to the elastic beanstalk environment,
    based of of the roles created when using the online AWS console. """
    iam_client = create_iam_client()
    
    try:
        iam_find_role(iam_client, ELASTICBEANSTALK_SERVICE_ROLE)
    except IamEntityMissingError:
        iam_create_role(iam_client, ELASTICBEANSTALK_SERVICE_ROLE,
                        get_elasticbeanstalk_assume_role_policy_document())
    
    iam_attach_role_policy(iam_client, ELASTICBEANSTALK_SERVICE_ROLE,
                           "arn:aws:iam::aws:policy/service-role/AWSElasticBeanstalkService")
    iam_attach_role_policy(iam_client, ELASTICBEANSTALK_SERVICE_ROLE,
                           "arn:aws:iam::aws:policy/service-role/AWSElasticBeanstalkEnhancedHealth")
    
    return iam_find_role(iam_client, ELASTICBEANSTALK_SERVICE_ROLE)


def get_or_create_eb_instance_profile_role():
    """ This function creates the appropriate roles that apply to the instances in an elastic
    beanstalk environment, based of of the roles created when using the online AWS console. """
    iam_client = create_iam_client()
    try:
        iam_find_role(iam_client, ELASTICBEANSTALK_INSTANCE_PROFILE_ROLE)
    except IamEntityMissingError:
        iam_create_role(iam_client, ELASTICBEANSTALK_INSTANCE_PROFILE_ROLE,
                        get_instance_assume_role_policy_document())
    
    # This is in the original role, but it is almost definitely not required.`
    iam_attach_role_policy(iam_client, ELASTICBEANSTALK_INSTANCE_PROFILE_ROLE,
                           "arn:aws:iam::aws:policy/AWSElasticBeanstalkMulticontainerDocker")
    iam_attach_role_policy(iam_client, ELASTICBEANSTALK_INSTANCE_PROFILE_ROLE,
                           "arn:aws:iam::aws:policy/AWSElasticBeanstalkWebTier")
    iam_attach_role_policy(iam_client, ELASTICBEANSTALK_INSTANCE_PROFILE_ROLE,
                           "arn:aws:iam::aws:policy/AWSElasticBeanstalkWorkerTier")
    
    return iam_find_role(iam_client, ELASTICBEANSTALK_INSTANCE_PROFILE_ROLE)


def get_or_create_eb_instance_profile():
    #     """ This function creates the appropriate roles that apply to the instances in an elastic
    #     beanstalk environment, based of of the roles created when using the online AWS console. """
    iam_client = create_iam_client()
    try:
        return iam_find_instance_profile(iam_client, ELASTICBEANSTALK_INSTANCE_PROFILE_NAME)
    except IamEntityMissingError:
        iam_client.create_instance_profile(
            InstanceProfileName=ELASTICBEANSTALK_INSTANCE_PROFILE_NAME)
        _ = iam_client.add_role_to_instance_profile(
                InstanceProfileName=ELASTICBEANSTALK_INSTANCE_PROFILE_NAME,
                RoleName=get_or_create_eb_service_role()['RoleName']
        )
    return iam_find_instance_profile(iam_client, ELASTICBEANSTALK_INSTANCE_PROFILE_NAME)


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
    pprint(construct_eb_environment_variables())
    if env is None:
        print "creating new environment"
        
        env = eb_client.create_environment(
                ApplicationName=BEIWE_APPLICATION_NAME,
                EnvironmentName=BEIWE_ENVIRONMENT_NAME,
                Description='elastic beanstalk beiwe cluster',
                PlatformArn=get_python27_platform_arn(),
                OptionSettings=construct_eb_environment_variables(),
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
        
    env_id = env['EnvironmentId']
    # eb_client.describe_environment_health is only supported on enhanced health monitoring systems
    # print eb_client.describe_environment_health(
    #         EnvironmentName=env['EnvironmentName'],
    #         EnvironmentId=env['EnvironmentId'],
    #         AttributeNames=["All"])
    good_eb_environment_states = ["Launching", "Updating"]
    bad_eb_environment_states = ["Terminating", "Terminated"]
    while True:
        envs = retry(eb_client.describe_environments, EnvironmentIds=[env_id])['Environments']
        log.info("Status is %s, waiting." % env['Status'])
        if len(envs) != 1:
            raise Exception("describe_environments is broken, %s environments returned" % len(envs))
        env = envs[0]
        if env['Status'] in bad_eb_environment_states:
            log.error("environment deployment failed:\n%s" % pformat(env))
            raise EnvironmentDeploymentFailure
        if env['Status'] in good_eb_environment_states:
            sleep(1)
            
            continue
        if env['Status'] == "Ready":
            return env
        
        
