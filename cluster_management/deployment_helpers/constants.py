## Ignore line length limits in this file.

from os.path import join as path_join, abspath

from flask import json

####################################################################################################
##################################### General Constants ############################################
####################################################################################################

REMOTE_USERNAME = 'ubuntu'
RABBIT_MQ_PORT = 50000

GLOBAL_CONFIGURATION_KEYS = ("DEPLOYMENT_KEY_NAME", "VPC_ID", "AWS_REGION")
AWS_CREDENTIAL_KEYS = ("AWS_ACCESS_KEY_ID","AWS_SECRET_ACCESS_KEY")

## EC2 Instance Deployment Variables
APT_GET_INSTALLS = [
    'ack-grep',  # Search within files
    'build-essential',  # Includes a C compiler for compiling python
    'htop',
    'libbz2-dev',
    'libreadline-gplv2-dev',
    'libsqlite3-dev',
    'libssl-dev',
    # AJK TODO do I need this? github says I do
    # 'mailutils',  # Necessary for cronutils
    'moreutils',  # Necessary for cronutils
    'nload',
    'rabbitmq-server',  # Queue tasks to run using celery
    'sendmail',  # Necessary for cronutils
    'silversearcher-ag',  # Search within files
]

# Files to push from the local server before the rest of launch
# This is a list of 2-tuples of (local_path, remote_path) where local_path is located in
# PUSHED_FILES_FOLDER and remote_path is located in REMOTE_HOME_DIRECTORY.
FILES_TO_PUSH = [
    ('bash_profile.sh', '.profile'),  # standard bash profile
    ('.inputrc', '.inputrc'),  # modifies what up-arrow, tab etc. do
    ('known_hosts', '.ssh/known_hosts'),  # allows git clone without further prompting
]


## Errors
class DBInstanceNotFound(Exception): pass


## ERROR_MESSAGES
EB_SEC_GRP_COUNT_ERROR = "%s has had multiple security groups associated with it.  This action is not supported by this console tool."

VALIDATE_GLOBAL_CONFIGURATION_MESSAGE = "before you can take any action with this tool you must fill out the contents of the global_configuration.json file in the general_configuration folder."

VALIDATE_AWS_CREDENTIALS_MESSAGE = "before you can take any action with this tool you must fill out the contents of the aws_credentials.json file in the general_configuration folder."
####################################################################################################
######################################## Static Files ##############################################
####################################################################################################

# Local folder paths
CLUSTER_MANAGEMENT_FOLDER = abspath(__file__).rsplit('/', 2)[0]
PUSHED_FILES_FOLDER = path_join(CLUSTER_MANAGEMENT_FOLDER, 'pushed_files')
USER_SPECIFIC_CONFIG_FOLDER = path_join(CLUSTER_MANAGEMENT_FOLDER, 'environment_configuration')
GENERAL_CONFIG_FOLDER = path_join(CLUSTER_MANAGEMENT_FOLDER, 'general_configuration')


## Global EC2 Instance __remote__ folder paths
REMOTE_HOME_DIR = path_join('/home', REMOTE_USERNAME)

## Global EC2 Instance remote file paths
DEPLOYMENT_ENVIRON_SETTING_REMOTE_FILE_PATH = path_join(REMOTE_HOME_DIR, 'beiwe-backend/config/remote_db_env.py')
LOG_FILE = path_join(REMOTE_HOME_DIR, 'server_setup.log')


## Management Tool Configuration Files
AWS_CREDENTIALS_FILE = path_join(GENERAL_CONFIG_FOLDER, 'aws_credentials.json')
GLOBAL_CONFIGURATION_FILE = path_join(GENERAL_CONFIG_FOLDER, 'global_configuration.json')
AWS_PEM_FILE = path_join(USER_SPECIFIC_CONFIG_FOLDER, 'aws_deployment_key.pem')

## Management Tool Configuration Loaders
def get_global_config():
    with open(GLOBAL_CONFIGURATION_FILE, 'r') as f:
        return json.load(f)


## EC2 Instance Configuration Files
def get_aws_credentials():
    with open(AWS_CREDENTIALS_FILE, 'r') as f:
        return json.load(f)


## Elastic Beanstalk Environment Files
ELASTICBEANSTALK_CONFIGURATION_FILE = path_join(USER_SPECIFIC_CONFIG_FOLDER,'elastic_beanstalk_configuration.json')
ELASTICBEANSTALK_ASSUME_ROLE_POLICY_DOCUMENT_PATH = path_join(USER_SPECIFIC_CONFIG_FOLDER, "elasticbeanstalk_assume_role_policy_document.json")
INSTANCE_ASSUME_ROLE_POLICY_DOCUMENT_PATH = path_join(USER_SPECIFIC_CONFIG_FOLDER, "instance_assume_role_policy_document.json")

## Elastic Beanstalk File Loaders
def get_elasticbeanstalk_assume_role_policy_document():
    with open(ELASTICBEANSTALK_ASSUME_ROLE_POLICY_DOCUMENT_PATH) as document:
        return document.read()

def get_instance_assume_role_policy_document():
    with open(INSTANCE_ASSUME_ROLE_POLICY_DOCUMENT_PATH) as document:
        return document.read()


####################################################################################################
####################################### Dynamic Files ##############################################
####################################################################################################

## EC2 Instance Configuration Files
def get_db_credentials_file_path(database_name):
    return path_join(USER_SPECIFIC_CONFIG_FOLDER, "database_credentials_for_%s" % database_name + ".json")

def get_local_instance_env_file_path(eb_environment_name):
    return path_join(USER_SPECIFIC_CONFIG_FOLDER, eb_environment_name + '_remote_db_env.py')

## Beiwe Environment Files
def get_beiwe_environment_file_path(eb_environment_name):
    return path_join(USER_SPECIFIC_CONFIG_FOLDER, eb_environment_name + "_beiwe_environment_variables.json")

## Elastic Beanstalk Files
def get_environment_credentials_for_eb_deployment_path(eb_environment_name):
    return path_join(USER_SPECIFIC_CONFIG_FOLDER, eb_environment_name + '_environment_settings.json')


####################################################################################################
########################################## Strings #################################################
####################################################################################################

OUR_CUSTOM_POLICY_ARN = "AutomationPolicy"
EB_SERVICE_ROLE = "beiwetest-elasticbeanstalk-service-role"
EB_INSTANCE_PROFILE_ROLE = "beiwetest-elasticbeanstalk-instance-profile-role"
EB_INSTANCE_PROFILE_NAME = "beiwetest-elasticbeanstalk-instance-profile"

# Elastic Beanstalk strings
BEIWE_APPLICATION_NAME = "beiwe-application"

# EB service role arns
AWS_EB_SERVICE = "arn:aws:iam::aws:policy/service-role/AWSElasticBeanstalkService"
AWS_EB_ENHANCED_HEALTH = "arn:aws:iam::aws:policy/service-role/AWSElasticBeanstalkEnhancedHealth"

# EB instance profile arns
AWS_EB_MULTICONTAINER_DOCKER = "arn:aws:iam::aws:policy/AWSElasticBeanstalkMulticontainerDocker"
AWS_EB_WEB_TIER = "arn:aws:iam::aws:policy/AWSElasticBeanstalkWebTier"
AWS_EB_WORKER_TIER = "arn:aws:iam::aws:policy/AWSElasticBeanstalkWorkerTier"
