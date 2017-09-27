# TODO:
# import settings in an intelligent manner from some json config files
# code that validates and prints all parameters in the json files for review?
# write up a readme on how to use this script
# make a requirements file for the launch script
# python version? make it 2 because pycharm only lets you pick one.

# uh-oh - SSL settings - I guess we need to validate route53 DNS settings.

# major script components
# deploy new cluster
# update frontend?
# update data processing?
# stop data processing?
# deploy N data processing servers
# modify EB scaling settings?
# update rabbitmq/celery server


import argparse
import logging
import os

from fabric.api import env, put, run

from deployment_helpers.configuration_utils import validate_config, write_config_to_file
from deployment_helpers.general_utils import log, AWS_PEM_FILE, PUSHED_FILES_FOLDER


# Set logging levels
logging.basicConfig(level=logging.DEBUG)
logging.getLogger('boto3').setLevel(logging.WARNING)
logging.getLogger('botocore').setLevel(logging.WARNING)
logging.getLogger('paramiko.transport').setLevel(logging.WARNING)


# Fabric configuration
class FabricExecutionError(Exception): pass
env.abort_exception = FabricExecutionError
env.abort_on_prompts = True


def run_remote_code():
    # Install things that need to be installed
    run('sudo apt-get install git')
    
    # Push the files in the pushed files folder
    put(
        os.path.join(PUSHED_FILES_FOLDER, 'git_read_only_key'),
        remote_path='/home/ubuntu/.ssh/id_rsa'
    )
    run('chmod 600 /home/ubuntu/.ssh/id_rsa')
    put(
        os.path.join(PUSHED_FILES_FOLDER, 'bash_profile.sh'),
        remote_path='/home/ubuntu/.profile'
    )
    put(
        os.path.join(PUSHED_FILES_FOLDER, '.inputrc'),
        remote_path='/home/ubuntu/.inputrc'
    )
    put(
        os.path.join(PUSHED_FILES_FOLDER, 'install_pyenv.sh'),
        remote_path='/home/ubuntu/install_pyenv.sh'
    )
    
    # Get a local copy of the git repository, now that we have the read-only key
    run('git clone git@github.com:onnela-lab/beiwe-backend.git')


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="interactive script for managing a Beiwe Cluster")
    
    # Get the configuration values and make them environment variables
    combined_config = validate_config()
    write_config_to_file(combined_config)
    
    # More fabric configuration
    env.host_string = combined_config['host_string']
    env.user = 'ubuntu'
    env.key_filename = AWS_PEM_FILE
    
    # Run actual code
    run_remote_code()
