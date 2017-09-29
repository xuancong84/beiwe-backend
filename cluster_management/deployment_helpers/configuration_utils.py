import json
import random
import re

from deployment_helpers.general_utils import AWS_CREDENTIALS_FILE, OS_ENVIRON_SETTING_LOCAL_FILE


def ensure_nonempty_string(value, value_name, errors_list):
    """
    Checks that an inputted value is a nonempty string
    :param value: A value to be checked
    :param value_name: The name of the value, to be used in the error string
    :param errors_list: The pass-by-reference list of error strings which we append to
    :return: Whether or not the value is in fact a nonempty string
    """
    
    if not isinstance(value, (str, unicode)):
        errors_list.append('{} must be a string'.format(value))
        return False
    elif not value:
        errors_list.append('{} cannot be empty'.format(value_name))
        return False
    else:
        return True


# AJK TODO annotate all
def validate_config():
    # Pull all the JSON data
    with open(AWS_CREDENTIALS_FILE, 'r') as fn:
        aws_credentials_config = json.load(fn)
    
    # Validate the data
    errors = []
    s3_bucket = aws_credentials_config.get('s3_bucket_name', '')
    ensure_nonempty_string(s3_bucket, 'S3 bucket name', errors)
    
    sysadmin_emails = aws_credentials_config.get('system_administrator_email_list', [])
    if not hasattr(sysadmin_emails, '__iter__'):
        errors.append('System administrator email list must be a list')
    elif not sysadmin_emails:
        errors.append('System administrator email list cannot be empty')
    else:
        for email in sysadmin_emails:
            if not re.match('^[\S]+@[\S]+\.[\S]+$', email):
                errors.append('Invalid email address: {}'.format(email))
    
    sentry_elastic_beanstalk_dsn = aws_credentials_config.get('elastic_beanstalk_dsn', '')
    sentry_data_processing_dsn = aws_credentials_config.get('data_processing_dsn', '')
    sentry_android_dsn = aws_credentials_config.get('android_dsn', '')
    sentry_javascript_dsn = aws_credentials_config.get('javascript_dsn', '')
    all_dsns = [
        sentry_elastic_beanstalk_dsn, sentry_data_processing_dsn,
        sentry_android_dsn, sentry_javascript_dsn,
    ]
    for dsn in all_dsns:
        if ensure_nonempty_string(dsn, 'DSN', errors):
            if not re.match('^https://[\S]+:[\S]+@sentry\.io/[\S]+$', dsn):
                errors.append('Invalid DSN: {}'.format(dsn))
    
    domain_name = aws_credentials_config.get('website_name')
    ensure_nonempty_string(domain_name, 'Domain name', errors)
    
    rds_db_name = aws_credentials_config.get('database_name')
    ensure_nonempty_string(rds_db_name, 'Database name', errors)
    rds_username = aws_credentials_config.get('database_username')
    ensure_nonempty_string(rds_username, 'Database username', errors)
    rds_password = aws_credentials_config.get('database_password')
    ensure_nonempty_string(rds_password, 'Database password', errors)
    
    rds_hostname = aws_credentials_config.get('database_host_name')
    if ensure_nonempty_string(rds_hostname, 'Database host name', errors):
        if not re.match('^[\S]+\.rds\.amazonaws\.com$', rds_hostname):
            errors.append('Invalid database host name')
    
    # Raise any errors
    if errors:
        print('\n'.join(errors))
        exit(1)
    
    # Put the data into one dict to be returned
    combined_config = {
        's3_bucket': s3_bucket,
        'domain_name': domain_name,
        'sysadmin_emails': ','.join(sysadmin_emails),
        'sentry_elastic_beanstalk_dsn': sentry_elastic_beanstalk_dsn,
        'sentry_data_processing_dsn': sentry_data_processing_dsn,
        'sentry_android_dsn': sentry_android_dsn,
        'sentry_javascript_dsn': sentry_javascript_dsn,
        'rds_db_name': rds_db_name,
        'rds_hostname': rds_hostname,
        'rds_username': rds_username,
        'rds_password': rds_password,
    }
    return combined_config


def augment_config(config):
    config['flask_secret_key'] = ''.join([random.choice('0123456789abcdef') for _ in xrange(80)])
    
    # AJK TODO temporary while waiting on boto AWS credential generation
    config['aws_access_key_id'] = 'default'
    config['aws_secret_access_key'] = 'default'
    
    config['s3_backups_bucket'] = '{}-backup'.format(config['s3_bucket'])
    
    config['e500_email_address'] = 'e500_error@{}'.format(config['domain_name'])
    config['other_email_address'] = 'telegram_service@{}'.format(config['domain_name'])
    return config


def write_config_to_local_file(config):
    list_to_write = ['import os']
    for key, value in config.iteritems():
        next_line = "os.environ['{key}'] = '{value}'".format(key=key.upper(), value=value)
        list_to_write.append(next_line)
    
    string_to_write = '\n'.join(list_to_write) + '\n'
    with open(OS_ENVIRON_SETTING_LOCAL_FILE, 'w') as fn:
        fn.write(string_to_write)
