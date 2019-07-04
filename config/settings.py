from os import getenv

"""
To customize any of these values, append a line to config/remote_db_env.py such as:
os.environ['S3_BUCKET'] = 'bucket_name'
"""

# This is the secret key for the website. Mostly it is used to sign cookies. You should provide a
#  cryptographically secure string to this value.
FLASK_SECRET_KEY = getenv("FLASK_SECRET_KEY")

# the name of the s3 bucket that will be used to store user generated data, and backups of local
# database information.
S3_BUCKET = getenv("S3_BUCKET")
S3_ENDPOINT_URL = getenv("S3_ENDPOINT_URL")

# Domain name for the server
DOMAIN_NAME = getenv("DOMAIN_NAME")

# A list of email addresses that will receive error emails. This value must be a
# comma separated list; whitespace before and after addresses will be stripped.
SYSADMIN_EMAILS = getenv("SYSADMIN_EMAILS")

# Sentry DSNs
SENTRY_ANDROID_DSN = getenv("SENTRY_ANDROID_DSN")
SENTRY_DATA_PROCESSING_DSN = getenv("SENTRY_DATA_PROCESSING_DSN")
SENTRY_ELASTIC_BEANSTALK_DSN = getenv("SENTRY_ELASTIC_BEANSTALK_DSN")
SENTRY_JAVASCRIPT_DSN = getenv("SENTRY_JAVASCRIPT_DSN")

# Production/Staging: set to "TRUE" if staging
IS_STAGING = getenv("IS_STAGING") or "PRODUCTION"

# S3 bucket access
S3_ACCESS_CREDENTIALS_USER = getenv("S3_ACCESS_CREDENTIALS_USER")
S3_ACCESS_CREDENTIALS_KEY = getenv("S3_ACCESS_CREDENTIALS_KEY")

S3_REGION_NAME = getenv("S3_REGION_NAME", "us-east-1")

# background color indicator for date elapse in seconds
DATE_ELAPSE_COLOR = [[30*3600, 'lime'], [72*3600, 'orange'], [float('inf'), 'red']]

SESSION_EXPIRE_IN_SECONDS = 9999