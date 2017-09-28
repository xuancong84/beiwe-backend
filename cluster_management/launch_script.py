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

from fabric.api import env, put, run, sudo

from deployment_helpers.configuration_utils import validate_config, write_config_to_file
from deployment_helpers.general_utils import log, APT_GET_INSTALLS, AWS_PEM_FILE, PUSHED_FILES_FOLDER


# Set logging levels
logging.basicConfig(level=logging.DEBUG)
logging.getLogger('boto3').setLevel(logging.WARNING)
logging.getLogger('botocore').setLevel(logging.WARNING)
logging.getLogger('paramiko.transport').setLevel(logging.WARNING)


# Fabric configuration
class FabricExecutionError(Exception): pass
env.abort_exception = FabricExecutionError
env.abort_on_prompts = True


def get_git_repo():
    """
    Get a local copy of the git repository
    """
    
    # Grab the read-only key from the local repository
    put(
        os.path.join(PUSHED_FILES_FOLDER, 'git_read_only_key'),
        remote_path='/home/ubuntu/.ssh/id_rsa'
    )
    run('chmod 600 /home/ubuntu/.ssh/id_rsa')
    
    # Git clone the repository into the remote beiwe-backend folder
    run('git clone git@github.com:onnela-lab/beiwe-backend.git')
    
    # Make sure the code is on the right branch
    # AJK TODO right now this is django, obviously this will change on prod
    run('cd /home/ubuntu/beiwe-backend; git checkout django')


def install_pyenv():
    """
    Install pyenv as well as the latest version of Python 2, accessible
    via /home/ubuntu/.pyenv/shims/python.
    """
    
    # Copy the installation script from the local repository onto the
    # remote server, make it executable and execute it.
    put(
        os.path.join(PUSHED_FILES_FOLDER, 'install_pyenv.sh'),
        remote_path='/home/ubuntu/install_pyenv.sh'
    )
    run('chmod +x /home/ubuntu/install_pyenv.sh')
    run('/home/ubuntu/install_pyenv.sh')

    # Install the latest python 2 version and set pyenv to default to that version.
    # Note that this installation is slow, taking approximately a minute.
    # -f: Install even if the version appears to be installed already
    run('/home/ubuntu/.pyenv/bin/pyenv install -f 2.7.14')
    run('/home/ubuntu/.pyenv/bin/pyenv global 2.7.14')
    
    # Display the version of python used by pyenv; this should print "Python 2.7.14".
    run('/home/ubuntu/.pyenv/shims/python --version')


def run_remote_code():
    
    # Install things that need to be installed. Notes: apt-get install accepts
    # an arbitrary number of space-separated arguments. The -y flag answers
    # "yes" to all prompts, preventing the need for user interaction.
    sudo('apt-get -qy install ' + ' '.join(APT_GET_INSTALLS))
    
    # Download the git repository onto the remote server
    get_git_repo()

    # Push the other files in the pushed files folder
    # AJK TODO understand this better and block and document more fully
    put(
        os.path.join(PUSHED_FILES_FOLDER, 'bash_profile.sh'),
        remote_path='/home/ubuntu/.profile'
    )
    put(
        os.path.join(PUSHED_FILES_FOLDER, '.inputrc'),
        remote_path='/home/ubuntu/.inputrc'
    )
    
    # Install pyenv and the latest Python 2 version
    install_pyenv()
    
    # Upgrade pip, because we don't know what version the server came with.
    # Install the python requirements for running the server code.
    # AJK TODO point out that we are using the pyenv pip. make sure this works properly
    run('/home/ubuntu/.pyenv/shims/pip install --upgrade pip')
    run('/home/ubuntu/.pyenv/shims/pip install -r /home/ubuntu/beiwe-backend/Requirements.txt')


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
