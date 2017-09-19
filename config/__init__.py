from config import settings, constants
provided_settings = vars(settings)

#check that all values provided actually contain something
for attr_name, attr_value in provided_settings.items():
    if not attr_value and attr_name[0] != '_':
        raise ImportError(attr_name + " was not provided with a value.")

MANDATORY_VARS = {'ASYMMETRIC_KEY_LENGTH',
                  'AWS_ACCESS_KEY_ID',
                  'AWS_SECRET_ACCESS_KEY',
                  'E500_EMAIL_ADDRESS',
                  'FLASK_SECRET_KEY',
                  'ITERATIONS',
                  'IS_STAGING',
                  'LOCAL_BACKUPS_DIRECTORY',
                  'MONGO_PASSWORD',
                  'MONGO_USERNAME',
                  'MONGO_PORT',
                  'MONGO_IP',
                  'OTHER_EMAIL_ADDRESS',
                  'S3_BACKUPS_AWS_KEY_ID',
                  'S3_BACKUPS_AWS_SECRET_ACCESS_KEY',
                  'S3_BACKUPS_BUCKET',
                  'S3_BUCKET',
                  'SENTRY_DSN',
                  'SENTRY_JAVASCRIPT_DSN',
                  'SYSADMIN_EMAILS'}

#Check that all the mandatory variables exist...
for mandatory_var in MANDATORY_VARS:
    if mandatory_var not in provided_settings:
        raise ImportError(mandatory_var + " was not provided in your settings.")

# Environment variables might be unpredictable, so we sanitize the numerical ones as ints.
settings.MONGO_PORT = int(settings.MONGO_PORT)
settings.ASYMMETRIC_KEY_LENGTH = int(settings.ASYMMETRIC_KEY_LENGTH)
settings.ITERATIONS = int(settings.ITERATIONS)

constants.DEFAULT_S3_RETRIES = int(constants.DEFAULT_S3_RETRIES)
constants.CONCURRENT_NETWORK_OPS = int(constants.CONCURRENT_NETWORK_OPS)
constants.FILE_PROCESS_PAGE_SIZE = int(constants.FILE_PROCESS_PAGE_SIZE)
constants.CELERY_EXPIRY_MINUTES = int(constants.CELERY_EXPIRY_MINUTES)

# email addresses are parsed from a comma separated list
# whitespace before and after addresses are stripped
settings.SYSADMIN_EMAILS = [_email_address.strip() for _email_address in settings.SYSADMIN_EMAILS.split(",")]

# IS_STAGING needs to resolve to False except under specific settings; the default needs to be production.
if (settings.IS_STAGING is True or settings.IS_STAGING.upper() == "TRUE"):
    settings.IS_STAGING = True
else:
    settings.IS_STAGING = False
    
    
