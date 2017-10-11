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

# Files
AWS_PEM_FILE = path_join(USER_SPECIFIC_CONFIG_FOLDER, 'aws_deployment_key.pem')
AWS_CREDENTIALS_FILE = path_join(USER_SPECIFIC_CONFIG_FOLDER, 'aws_credentials.json')
BEIWE_ENVIRONMENT_FILE = path_join(USER_SPECIFIC_CONFIG_FOLDER, "beiwe_environment_variables.json")
ELASTICBEANSTALK_CONFIGURATION_FILE = path_join(USER_SPECIFIC_CONFIG_FOLDER, 'elastic_beanstalk_configuration.json')
OS_ENVIRON_SETTING_LOCAL_FILE = path_join(CLUSTER_MANAGEMENT_FOLDER, 'remote_db_env.py')


# other documents
ELASTICBEANSTALK_ASSUME_ROLE_POLICY_DOCUMENT_PATH = path_join(
        USER_SPECIFIC_CONFIG_FOLDER, "elasticbeanstalk_assume_role_policy_document.json")

INSTANCE_ASSUME_ROLE_POLICY_DOCUMENT_PATH = path_join(
        USER_SPECIFIC_CONFIG_FOLDER, "instance_assume_role_policy_document.json")


# IAM strings
OUR_CUSTOM_POLICY_ARN = 'arn:aws:iam::284616134063:policy/AutomationPolicy'
ELASTICBEANSTALK_SERVICE_ROLE = u"beiwetest-elasticbeanstalk-service-role"
ELASTICBEANSTALK_INSTANCE_PROFILE_ROLE = u"beiwetest-elasticbeanstalk-instance-profile-role"
ELASTICBEANSTALK_INSTANCE_PROFILE_NAME = u"beiwetest-elasticbeanstalk-instance-profile"

# Elastic Beanstalk strings
BEIWE_APPLICATION_NAME = "beiwe-application"
BEIWE_ENVIRONMENT_NAME = "beiwe-environment"

