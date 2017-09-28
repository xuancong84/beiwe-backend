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
from deployment_helpers.general_utils import (
    log, APT_GET_INSTALLS, AWS_PEM_FILE, FILES_TO_PUSH, LOG_FILE,
    PUSHED_FILES_FOLDER, REMOTE_HOME_DIR,
)


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
    key_path = os.path.join(REMOTE_HOME_DIR, '.ssh/id_rsa')
    put(
        os.path.join(PUSHED_FILES_FOLDER, 'git_read_only_key'),
        remote_path=key_path,
    )
    run('chmod 600 {key_path}'.format(key_path=key_path))
    
    # Git clone the repository into the remote beiwe-backend folder
    # Note that here stderr is redirected to the log file, because git clone prints
    # to stderr rather than stdout.
    run('cd {home}; git clone git@github.com:onnela-lab/beiwe-backend.git 2>> {log}'
        .format(home=REMOTE_HOME_DIR, log=LOG_FILE))
    
    # Make sure the code is on the right branch
    # git checkout prints to both stderr *and* stdout, so redirect them both to the log file
    # AJK TODO for local testing this uses the django branch
    run('cd {home}/beiwe-backend; git checkout django 1>> {log} 2>> {log}'
        .format(home=REMOTE_HOME_DIR, log=LOG_FILE))


def push_files():
    # Push the other files in the pushed files folder
    for local_path, remote_path in FILES_TO_PUSH:
        put(
            os.path.join(PUSHED_FILES_FOLDER, local_path),
            remote_path=os.path.join(REMOTE_HOME_DIR, remote_path),
        )


def install_pyenv():
    """
    Install pyenv as well as the latest version of Python 2, accessible
    via REMOTE_HOME_DIR/.pyenv/shims/python.
    """
    
    # Copy the installation script from the local repository onto the
    # remote server, make it executable and execute it.
    script_path = os.path.join(REMOTE_HOME_DIR, 'install_pyenv.sh')
    put(
        os.path.join(PUSHED_FILES_FOLDER, 'install_pyenv.sh'),
        remote_path=script_path,
    )
    run('chmod +x {script_path}'.format(script_path=script_path))
    run(script_path)

    # Install the latest python 2 version and set pyenv to default to that version.
    # Note that this installation is slow, taking approximately a minute.
    # -f: Install even if the version appears to be installed already
    # AJK TODO temporary for repeated testing (+1-1)
    run('{home}/.pyenv/bin/pyenv install -s 2.7.14'.format(home=REMOTE_HOME_DIR))
    # run('{home}/.pyenv/bin/pyenv install -f 2.7.14'.format(home=REMOTE_HOME_DIR))
    run('{home}/.pyenv/bin/pyenv global 2.7.14'.format(home=REMOTE_HOME_DIR))
    
    # Display the version of python used by pyenv; this should print "Python 2.7.14".
    run('{home}/.pyenv/shims/python --version'.format(home=REMOTE_HOME_DIR))


def run_remote_code():
    
    # AJK TODO this presumably isn't necessary in reality?
    # Clear the log file if it already exists. This file will be used to redirect
    # output to, so that the local user isn't forced to see a mass of confusing
    # text.
    run('echo "" > {log}'.format(log=LOG_FILE))
    
    # Install things that need to be installed. Notes: apt-get install accepts
    # an arbitrary number of space-separated arguments. The -y flag answers
    # "yes" to all prompts, preventing the need for user interaction.
    installs_string = ' '.join(APT_GET_INSTALLS)
    sudo('apt-get -y install {installs} >> {log}'.format(log=LOG_FILE, installs=installs_string))
    
    # Download the git repository onto the remote server
    # AJK TODO temporary for repeated testing (+1)
    run('rm -fr {home}/beiwe-backend'.format(home=REMOTE_HOME_DIR))
    get_git_repo()
    
    # Put any files from the local pushed_files folder into
    # their corresponding remote locations.
    push_files()
    
    # Install pyenv and the latest Python 2 version
    install_pyenv()
    
    # Upgrade pip, because we don't know what version the server came with.
    # Install the python requirements for running the server code.
    # Note that we are using the pyenv pip to ensure that the python requirements
    # are installed into pyenv, rather than into the system python.
    run('{home}/.pyenv/shims/pip install --upgrade pip >> {log}'
        .format(home=REMOTE_HOME_DIR, log=LOG_FILE))
    run('{home}/.pyenv/shims/pip install -r {home}/beiwe-backend/Requirements.txt >> {log}'
        .format(home=REMOTE_HOME_DIR, log=LOG_FILE))


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
