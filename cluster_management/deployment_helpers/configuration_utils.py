import json

from deployment_helpers.general_utils import AWS_CREDENTIALS_FILE


def validate_config():
    # Pull all the JSON data
    with open(AWS_CREDENTIALS_FILE, 'r') as fn:
        aws_credentials_config = json.load(fn)
    
    # Validate the data
    host_string = aws_credentials_config['ip_address']
    
    # Put the data into one dict to be returned to the parent
    combined_config = {
        'host_string': host_string,
    }
    return combined_config


def write_config_to_file(config):
    print(config)
