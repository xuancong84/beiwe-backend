"""
A script for setting up an AWS environment to run the Beiwe Data Access Pipeline
"""

import json
import os.path

from boto_helpers import get_configs_folder
from scripts import docker_script, job_queue_script


def run(ecr_repo_name, comp_env_role, instance_profile, comp_env_name, queue_name, job_defn_name, **_):
    """
    Run the actual code. The various arguments are passed to the sub-scripts. Note that the
    variable names MUST match the keys in aws-object-names.json, or else they will not be
    passed correctly as keyword arguments.
    """
    
    repo_uri = docker_script.run(ecr_repo_name)
    job_queue_script.run(
        comp_env_role, instance_profile, comp_env_name, queue_name, job_defn_name, repo_uri,
    )


if __name__ == '__main__':
    
    # Get the file containing the AWS object names
    configs_folder = get_configs_folder()
    aws_object_names_file = os.path.join(configs_folder, 'aws-object-names.json')
    
    # Get the AWS object names from the file
    with open(aws_object_names_file) as fn:
        aws_object_names_dict = json.load(fn)
    
    # Pass them to the scripts that need them
    run(**aws_object_names_dict)
