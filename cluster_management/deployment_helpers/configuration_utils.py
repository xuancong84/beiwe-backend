import json
import re

from deployment_helpers.general_utils import AWS_CREDENTIALS_FILE, OS_ENVIRON_SETTING_LOCAL_FILE


# AJK TODO annotate
def validate_config():
    # Pull all the JSON data
    with open(AWS_CREDENTIALS_FILE, 'r') as fn:
        aws_credentials_config = json.load(fn)
    
    # Validate the data
    errors = []
    s3_bucket_name = aws_credentials_config.get('s3_bucket_name', '')
    if not isinstance(s3_bucket_name, (str, unicode)):
        errors.append('S3 bucket name must be a string')
    elif not s3_bucket_name:
        errors.append('S3 bucket name cannot be empty')
    
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
        if not isinstance(dsn, (str, unicode)):
            errors.append('DSN must be a string')
        elif not re.match('^https://[\S]+:[\S]+@sentry\.io/[\S]+$', dsn):
            errors.append('Invalid DSN: {}'.format(dsn))
    
    domain_name = aws_credentials_config.get('website_name')
    if not isinstance(domain_name, (str, unicode)):
        errors.append('Domain name must be a string')
    elif not domain_name:
        errors.append('Domain name cannot be empty')
    
    # Raise any errors
    if errors:
        print('\n'.join(errors))
        exit(1)
    
    # Put the data into one dict to be returned
    combined_config = {
        's3_bucket_name': s3_bucket_name,
        'domain_name': domain_name,
        'sysadmin_emails': ','.join(sysadmin_emails),
        'sentry_elastic_beanstalk_dsn': sentry_elastic_beanstalk_dsn,
        'sentry_data_processing_dsn': sentry_data_processing_dsn,
        'sentry_android_dsn': sentry_android_dsn,
        'sentry_javascript_dsn': sentry_javascript_dsn,
    }
    return combined_config


# AJK TODO annotate
def write_config_to_local_file(config):
    list_to_write = ['import os']
    for key, value in config.iteritems():
        next_line = "os.environ['{key}'] = '{value}'".format(key=key.upper(), value=value)
        list_to_write.append(next_line)
    
    string_to_write = '\n'.join(list_to_write) + '\n'
    with open(OS_ENVIRON_SETTING_LOCAL_FILE, 'w') as fn:
        fn.write(string_to_write)
