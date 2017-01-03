from os import getenv
import json

# These are the credentials used to access the MongoDB that contains website
# usernames and passwords.  If you are configuring your server see the comment
# at the end of this document.
MONGO_USERNAME = getenv("MONGO_USERNAME")
MONGO_PASSWORD = getenv("MONGO_PASSWORD")

# This is the secret key for the website. Mostly it is used to sign cookies.
# You should provide a cryptographically secure string to this value.
FLASK_SECRET_KEY = getenv("FLASK_SECRET_KEY")

# These are your AWS (Amazon Web Services) access credentials.
# (Amazon provides you with these credentials, you do not generate them.)
AWS_ACCESS_KEY_ID = getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = getenv("AWS_SECRE`T_ACCESS_KEY")

S3_BACKUPS_AWS_KEY_ID = getenv("S3_BACKUPS_AWS_KEY_ID")
S3_BACKUPS_AWS_SECRET_ACCESS_KEY = getenv("S3_BACKUPS_AWS_SECRET_ACCESS_KEY")
LOCAL_BACKUPS_DIRECTORY = getenv("LOCAL_BACKUPS_DIRECTORY") or "/tmp/beiwe_backups/"

# the name of the s3 bucket that will be used to store user generated data, and
# backups of local database information.
S3_BUCKET = getenv("S3_BUCKET")
S3_BACKUPS_BUCKET = getenv("S3_BACKUPS_BUCKET")

# Email addresses used on the server.
E500_EMAIL_ADDRESS = getenv("E500_EMAIL_ADDRESS")
OTHER_EMAIL_ADDRESS = getenv("OTHER_EMAIL_ADDRESS")
SYSADMIN_EMAILS = json.loads(getenv("SYSADMIN_EMAILS"))

# MongoDB port number
MONGO_PORT = getenv("MONGDB_PORT") or 27017

ASYMMETRIC_KEY_LENGTH = getenv("ASYMMETRIC_KEY_LENGTH") or 2048

# The number of iterations used in password hashing. You CANNOT change this
# value once people have created passwords, because then the hashes won't match!
ITERATIONS = getenv("ITERATIONS") or 1000
