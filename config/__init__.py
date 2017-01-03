import secure_settings
provided_settings = vars(secure_settings)
provided_settings.pop("__builtins__")

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
                  'LOCAL_BACKUPS_DIRECTORY',
                  'MONGO_PASSWORD',
                  'MONGO_USERNAME',
                  'MONGODB_PORT',
                  'OTHER_EMAIL_ADDRESS',
                  'S3_BACKUPS_AWS_KEY_ID',
                  'S3_BACKUPS_AWS_SECRET_ACCESS_KEY',
                  'S3_BACKUPS_BUCKET',
                  'S3_BUCKET',
                  'SYSADMIN_EMAILS' }

#Check that all the mandatory variables exist...
for mandatory_var in MANDATORY_VARS:
    if mandatory_var not in provided_settings:
        raise ImportError(mandatory_var + " was not provided in your settings.")

# Environment might be unpredictable, so we sanitize the env variables that need to be numeric as ints
secure_settings.MONGO_PORT = int(secure_settings.MONGO_PORT)
secure_settings.ASYMMETRIC_KEY_LENGTH = int(secure_settings.ASYMMETRIC_KEY_LENGTH)
secure_settings.ITERATIONS = int(secure_settings.ITERATIONS)