import json
import os.path

from boto_helpers import get_configs_folder
from scripts import docker_script, job_queue_script, lambda_script


# TODO annotate and docstring this file
# These argument names MUST match the keys in aws-object-names.json
def run(ecr_repo_name, comp_env_role, instance_profile, comp_env_name, queue_name, job_defn_name, lambda_role, function_name, rule_name, **_):
    repo_uri = docker_script.run(ecr_repo_name)
    job_queue_script.run(comp_env_role, instance_profile, comp_env_name, queue_name, job_defn_name, repo_uri)
    lambda_script.run(lambda_role, function_name, rule_name)


if __name__ == '__main__':
    configs_folder = get_configs_folder()
    aws_object_names_file = os.path.join(configs_folder, 'aws-object-names.json')
    
    # Get the AWS object names
    with open(aws_object_names_file) as fn:
        aws_object_names_dict = json.load(fn)
    
    # Pass them to the scripts that need them
    run(**aws_object_names_dict)
