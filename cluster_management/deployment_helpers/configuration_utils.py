import json
import re

from deployment_helpers.general_utils import AWS_CREDENTIALS_FILE


def validate_config():
    # Pull all the JSON data
    with open(AWS_CREDENTIALS_FILE, 'r') as fn:
        aws_credentials_config = json.load(fn)
    
    # Validate the data
    errors = []
    host_string = aws_credentials_config['ip_address']
    if not re.match('^(?:(?:[0-9]|[1-9][0-9]|1[0-9]{2}|2[0-4][0-9]|25[0-5])\.){4}$',
                    host_string + '.'):
        errors.append('Invalid IP address')
    
    # Raise any errors
    if errors:
        print('\n'.join(errors))
        exit(1)
    
    # Put the data into one dict to be returned to the parent
    combined_config = {
        'host_string': host_string,
    }
    return combined_config


def write_config_to_file(config):
    print(config)
