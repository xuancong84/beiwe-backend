import json
import os.path

from boto_helpers import get_configs_folder
from scripts import docker_script

if __name__ == '__main__':
    
    # Get the file containing the AWS object names
    configs_folder = get_configs_folder()
    aws_object_names_file = os.path.join(configs_folder, 'aws-object-names.json')
    
    # Get the AWS object names from the file
    with open(aws_object_names_file) as fn:
        aws_object_names_dict = json.load(fn)
    
    # Pass them to the scripts that need them
    docker_script.run(aws_object_names_dict['ecr_repo_name'])

