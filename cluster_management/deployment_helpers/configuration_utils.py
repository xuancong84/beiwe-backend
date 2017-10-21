import json
import re
from time import sleep

from deployment_helpers.aws.rds import get_full_db_credentials_by_name
from deployment_helpers.constants import (AWS_CREDENTIALS_FILE,
    get_local_instance_env_file_path, get_global_config, GLOBAL_CONFIGURATION_KEYS,
    GLOBAL_CONFIGURATION_FILE, get_aws_credentials, AWS_CREDENTIAL_KEYS,
    VALIDATE_GLOBAL_CONFIGURATION_MESSAGE, VALIDATE_AWS_CREDENTIALS_MESSAGE)
from deployment_helpers.general_utils import log, random_alphanumeric_string


def _simple_validate_required(getter_func, file_path, appropriate_keys):
    """ returns False if invalid, True if valid.  For use with fully required keys, prints useful messages."""
    # try and load, fail usefully.
    try:
        json_config = getter_func()
    except Exception:
        log.error("could not load the file '%s'." % file_path)
        sleep(0.1)
        return False  # could not load, did not pass
    
    # check for invalid values and keyserrors
    error_free = True
    for k, v in json_config.iteritems():
        if k not in appropriate_keys:
            log.error("a key '%s' is present, but was not expected.")
            error_free = False
        if not v:
            error_free = False
            log.error("'%s' must be present and have a value." % k)
    
    for key in appropriate_keys:
        if key not in json_config:
            log.error("the key '%s' was expected but not present.")
            error_free = False
    
    sleep(0.01) # python logging is dumb, wait so logs actually appear
    return error_free


def are_aws_credentials_present():
    ret = _simple_validate_required(get_aws_credentials, AWS_CREDENTIALS_FILE, AWS_CREDENTIAL_KEYS)
    if not ret:
        log.error(VALIDATE_AWS_CREDENTIALS_MESSAGE)
    return ret


def is_global_configuration_valid():
    ret = _simple_validate_required(get_global_config, GLOBAL_CONFIGURATION_FILE, GLOBAL_CONFIGURATION_KEYS)
    if not ret:
        log.error(VALIDATE_GLOBAL_CONFIGURATION_MESSAGE)
    return ret

    
def reference_default_environment_configuration(eb_environment_name):
    return {
        "DOMAIN": "studies.mywebsite.com",
        "SYSTEM_ADMINISTRATOR_EMAIL_LIST": ["researcher@institution.edu", "mypersonalemail@email.com"],
        "SENTRY_ELASTIC_BEANSTALK_DSN": "",
        "SENTRY_DATA_PROCESSING_DSN": "",
        "SENTRY_ANDROID_DSN": "",
        "SENTRY_JAVASCRIPT_DSN": "",
    }


def ensure_nonempty_string(value, value_name, errors_list):
    """
    Checks that an inputted value is a nonempty string
    :param value: A value to be checked
    :param value_name: The name of the value, to be used in the error string
    :param errors_list: The pass-by-reference list of error strings which we append to
    :return: Whether or not the value is in fact a nonempty string
    """
    if not isinstance(value, (str, unicode)):
        log.error(value_name + " encountered an error")
        errors_list.append('{} must be a string'.format(value))
        return False
    elif not value:
        log.error(value_name + " encountered an error")
        errors_list.append('{} cannot be empty'.format(value_name))
        return False
    else:
        return True


# AJK TODO annotate all
# basics: creates a whitelist of the aws_credentials file
def validate_config(eb_environment_name):
    # Pull all the JSON data
    with open(AWS_CREDENTIALS_FILE, 'r') as fn:
        aws_credentials_config = json.load(fn)
    
    # Validate the data
    errors = []
    s3_bucket = aws_credentials_config.get('S3_BUCKET_NAME', '')
    ensure_nonempty_string(s3_bucket, 'S3 bucket name', errors)
    
    sysadmin_emails = aws_credentials_config.get('SYSTEM_ADMINISTRATOR_EMAIL_LIST', [])
    if not hasattr(sysadmin_emails, '__iter__'):
        errors.append('System administrator email list must be a list')
    elif not sysadmin_emails:
        errors.append('System administrator email list cannot be empty')
    else:
        for email in sysadmin_emails:
            if not re.match('^[\S]+@[\S]+\.[\S]+$', email):
                errors.append('Invalid email address: {}'.format(email))
    
    # check sentry urls
    sentry_dsns = {
        "SENTRY_ELASTIC_BEANSTALK_DSN": aws_credentials_config.get('elastic_beanstalk_dsn', ''),
        "SENTRY_DATA_PROCESSING_DSN": aws_credentials_config.get('data_processing_dsn', ''),
        "SENTRY_ANDROID_DSN": aws_credentials_config.get('android_dsn', ''),
        # TODO: I thiink that the javascript dsn drops the FIRST section, check
        "SENTRY_JAVASCRIPT_DSN": aws_credentials_config.get('javascript_dsn', ''),
    }
    for name, dsn in sentry_dsns.iteritems():
        if ensure_nonempty_string(dsn, name, errors):
            if not re.match('^https://[\S]+:[\S]+@sentry\.io/[\S]+$', dsn):
                errors.append('Invalid DSN: {}'.format(dsn))
                
    domain_name = aws_credentials_config.get('DOMAIN', None)
    ensure_nonempty_string(domain_name, 'Domain name', errors)
            
    # Raise any errors
    if errors:
        log.error('\n'.join(errors))
        sleep(1)  # python logging has some issues if you exit too fast
        exit(1)  # forcibly exit, do not continue to run any code.
        
    # Put the data into one dict to be returned
    config = {
        's3_bucket': s3_bucket,
        'domain_name': domain_name,
        'sysadmin_emails': ','.join(sysadmin_emails),
        'SENTRY_ELASTIC_BEANSTALK_DSN': sentry_dsns['SENTRY_ELASTIC_BEANSTALK_DSN'],
        'SENTRY_DATA_PROCESSING_DSN': sentry_dsns['SENTRY_DATA_PROCESSING_DSN'],
        'SENTRY_ANDROID_DSN': sentry_dsns['SENTRY_ANDROID_DSN'],
        'SENTRY_JAVASCRIPT_DSN': sentry_dsns['SENTRY_JAVASCRIPT_DSN']
    }
    return config


def augment_config(config, eb_environment_name):
    # requires an rds server has been created for the environment.
    config.update(get_full_db_credentials_by_name(eb_environment_name))
    config['flask_secret_key'] = random_alphanumeric_string(80)
    # AJK TODO temporary while waiting on boto AWS credential generation
    config["S3_BUCKET_NAME"] = "my-unique-string"
    return config


def write_config_to_local_file(config, eb_environment_name):
    list_to_write = ['import os']
    for key, value in config.iteritems():
        next_line = "os.environ['{key}'] = '{value}'".format(key=key.upper(), value=value)
        list_to_write.append(next_line)
    string_to_write = '\n'.join(list_to_write) + '\n'
    with open(get_local_instance_env_file_path(eb_environment_name), 'w') as fn:
        fn.write(string_to_write)
