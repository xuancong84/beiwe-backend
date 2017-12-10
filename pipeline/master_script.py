import json

from scripts import docker_script, job_queue_script, lambda_script


# TODO annotate and docstring all files
# These argument names MUST match the keys in aws-object-names.json
def run(ecr_repo_name, comp_env_role, instance_profile, comp_env_name, queue_name, job_defn_name, lambda_role, function_name, rule_name, **_):
    repo_uri = docker_script.run(ecr_repo_name)
    job_queue_script.run(comp_env_role, instance_profile, comp_env_name, queue_name, job_defn_name, repo_uri)
    lambda_script.run(lambda_role, function_name, rule_name)


if __name__ == '__main__':
    # Get the AWS object names
    with open('aws-object-names.json') as fn:
        aws_object_names = json.load(fn)
    
    # Pass them to the scripts that need them
    run(**aws_object_names)
