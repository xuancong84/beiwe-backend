from os.path import join as path_join, abspath

##
## Strings
##

REMOTE_USERNAME = 'ubuntu'


##
## File Paths
##

## Remote files
REMOTE_HOME_DIR = path_join('/home', REMOTE_USERNAME)
LOG_FILE = path_join(REMOTE_HOME_DIR, 'server_setup.log')
OS_ENVIRON_SETTING_REMOTE_FILE = path_join(REMOTE_HOME_DIR, 'beiwe-backend/config/remote_db_env.py')

## Local files
# Folders
CLUSTER_MANAGEMENT_FOLDER = abspath(__file__).rsplit('/', 2)[0]
PUSHED_FILES_FOLDER = path_join(CLUSTER_MANAGEMENT_FOLDER, 'pushed_files')
USER_SPECIFIC_CONFIG_FOLDER = path_join(CLUSTER_MANAGEMENT_FOLDER, 'my_cluster_configuration')

def db_credentials_file_path(database_name):
    return path_join(USER_SPECIFIC_CONFIG_FOLDER,
                     "database_credentials_for_%s" % database_name + ".json")

# Files
AWS_PEM_FILE = path_join(USER_SPECIFIC_CONFIG_FOLDER, 'aws_deployment_key.pem')
AWS_CREDENTIALS_FILE = path_join(USER_SPECIFIC_CONFIG_FOLDER, 'aws_credentials.json')
BEIWE_ENVIRONMENT_FILE = path_join(USER_SPECIFIC_CONFIG_FOLDER, "beiwe_environment_variables.json")
ELASTICBEANSTALK_CONFIGURATION_FILE = path_join(USER_SPECIFIC_CONFIG_FOLDER, 'elastic_beanstalk_configuration.json')
OS_ENVIRON_SETTING_LOCAL_FILE = path_join(CLUSTER_MANAGEMENT_FOLDER, 'remote_db_env.py')
GLOBAL_CONFIGURATION_FILE = path_join(USER_SPECIFIC_CONFIG_FOLDER, 'global_configuration.json')

# other documents
ELASTICBEANSTALK_ASSUME_ROLE_POLICY_DOCUMENT_PATH = path_join(
        USER_SPECIFIC_CONFIG_FOLDER, "elasticbeanstalk_assume_role_policy_document.json")

INSTANCE_ASSUME_ROLE_POLICY_DOCUMENT_PATH = path_join(
        USER_SPECIFIC_CONFIG_FOLDER, "instance_assume_role_policy_document.json")

def get_elasticbeanstalk_assume_role_policy_document():
    with open(ELASTICBEANSTALK_ASSUME_ROLE_POLICY_DOCUMENT_PATH) as document:
        return document.read()

def get_instance_assume_role_policy_document():
    with open(INSTANCE_ASSUME_ROLE_POLICY_DOCUMENT_PATH) as document:
        return document.read()

# IAM strings
# OUR_CUSTOM_POLICY_ARN = 'arn:aws:iam::284616134063:policy/AutomationPolicy'
OUR_CUSTOM_POLICY_ARN = "AutomationPolicy"
EB_SERVICE_ROLE = "beiwetest-elasticbeanstalk-service-role"
EB_INSTANCE_PROFILE_ROLE = "beiwetest-elasticbeanstalk-instance-profile-role"
EB_INSTANCE_PROFILE_NAME = "beiwetest-elasticbeanstalk-instance-profile"

# Elastic Beanstalk strings
BEIWE_APPLICATION_NAME = "beiwe-application"
# eb service role arns
AWS_EB_SERVICE = "arn:aws:iam::aws:policy/service-role/AWSElasticBeanstalkService"
AWS_EB_ENHANCED_HEALTH = "arn:aws:iam::aws:policy/service-role/AWSElasticBeanstalkEnhancedHealth"
# eb instance profile arns
AWS_EB_MULTICONTAINER_DOCKER = "arn:aws:iam::aws:policy/AWSElasticBeanstalkMulticontainerDocker"
AWS_EB_WEB_TIER = "arn:aws:iam::aws:policy/AWSElasticBeanstalkWebTier"
AWS_EB_WORKER_TIER = "arn:aws:iam::aws:policy/AWSElasticBeanstalkWorkerTier"

# ERRORS
class DBInstanceNotFound(Exception): pass

EB_SEC_GRP_COUNT_ERROR = "%s has had multiple security groups associated with it.  This action is not supported by this console tool."