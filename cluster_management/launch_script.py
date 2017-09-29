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

from deployment_helpers.configuration_utils import (
    augment_config, validate_config, write_config_to_local_file
)
from deployment_helpers.general_utils import (
    APT_GET_INSTALLS, AWS_PEM_FILE, FILES_TO_PUSH, LOG_FILE, OS_ENVIRON_SETTING_LOCAL_FILE,
    OS_ENVIRON_SETTING_REMOTE_FILE, PUSHED_FILES_FOLDER, REMOTE_HOME_DIR, REMOTE_USER
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


def setup_profile():
    for local_relative_file, remote_relative_file in FILES_TO_PUSH:
        local_file = os.path.join(PUSHED_FILES_FOLDER, local_relative_file)
        remote_file = os.path.join(REMOTE_HOME_DIR, remote_relative_file)
        put(local_file, remote_file)


def get_git_repo():
    """
    Get a local copy of the git repository
    """
    
    # Grab the read-only key from the local repository
    key_local_path = os.path.join(PUSHED_FILES_FOLDER, 'git_read_only_key')
    key_remote_path = os.path.join(REMOTE_HOME_DIR, '.ssh/id_rsa')
    put(key_local_path, key_remote_path)
    run('chmod 600 {key_path}'.format(key_path=key_remote_path))
    
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


def setup_python():
    """
    Install pyenv as well as the latest version of Python 2, accessible
    via REMOTE_HOME_DIR/.pyenv/shims/python.
    """
    
    # Copy the installation script from the local repository onto the
    # remote server, make it executable and execute it.
    pyenv_installer_local_file = os.path.join(PUSHED_FILES_FOLDER, 'install_pyenv.sh')
    pyenv_installer_remote_file = os.path.join(REMOTE_HOME_DIR, 'install_pyenv.sh')
    put(pyenv_installer_local_file, pyenv_installer_remote_file)
    run('chmod +x {file}'.format(file=pyenv_installer_remote_file))
    run(pyenv_installer_remote_file)

    # Install the latest python 2 version and set pyenv to default to that version.
    # Note that this installation is slow, taking approximately a minute.
    # -f: Install even if the version appears to be installed already
    pyenv_exec = os.path.join(REMOTE_HOME_DIR, '.pyenv/bin/pyenv')
    # AJK TODO temporary for repeated testing (+1-1)
    run('{pyenv} install -s 2.7.14'.format(pyenv=pyenv_exec))
    # run('{home}/.pyenv/bin/pyenv install -f 2.7.14'.format(home=REMOTE_HOME_DIR))
    run('{pyenv} global 2.7.14'.format(pyenv=pyenv_exec))
    
    # Display the version of python used by pyenv; this should print "Python 2.7.14".
    pyenv_shims_dir = os.path.join(REMOTE_HOME_DIR, '.pyenv/shims')
    run('{shims}/python --version'.format(shims=pyenv_shims_dir))

    # Upgrade pip, because we don't know what version the server came with.
    run('{shims}/pip install --upgrade pip >> {log}'.format(log=LOG_FILE, shims=pyenv_shims_dir))
    
    # Install the python requirements for running the server code.
    # Note that we are using the pyenv pip to ensure that the python requirements
    # are installed into pyenv, rather than into the system python.
    run('{shims}/pip install -r {home}/beiwe-backend/Requirements.txt >> {log}'
        .format(home=REMOTE_HOME_DIR, log=LOG_FILE, shims=pyenv_shims_dir))


def setup_celery():
    celery_local_file = os.path.join(PUSHED_FILES_FOLDER, 'install_celery_worker.sh')
    celery_remote_file = os.path.join(REMOTE_HOME_DIR, 'install_celery_worker.sh')
    
    # Copy the script from the local repository onto the remote server,
    # make it executable and execute it.
    put(celery_local_file, celery_remote_file)
    run('chmod +x {file}'.format(file=celery_remote_file))
    run('{file} >> {log}'.format(file=celery_remote_file, log=LOG_FILE))


def setup_cron():
    cronjob_local_file = os.path.join(PUSHED_FILES_FOLDER, 'celery_periodic_restart_cronjob.txt')
    cronjob_remote_file = os.path.join(REMOTE_HOME_DIR, 'cronjob.txt')
    
    # Copy the cronjob file onto the remote server and add it to the remote crontab
    put(cronjob_local_file, cronjob_remote_file)
    run('crontab -u {user} {file}'.format(file=cronjob_remote_file, user=REMOTE_USER))


def run_remote_code():
    
    # AJK TODO not everything is getting logged, even when I redirect---figure out why
    # Clear the log file if it already exists. This file will be used to redirect
    # output to, so that the local user isn't forced to see a mass of confusing
    # text.
    run('echo "" > {log}'.format(log=LOG_FILE))
    
    # Set up the bash profile and terminal interactions
    setup_profile()
    
    # Install things that need to be installed. Notes: apt-get install accepts
    # an arbitrary number of space-separated arguments. The -y flag answers
    # "yes" to all prompts, preventing the need for user interaction.
    installs_string = ' '.join(APT_GET_INSTALLS)
    sudo('apt-get -y update >> {log}'.format(log=LOG_FILE))
    sudo('apt-get -y install {installs} >> {log}'.format(installs=installs_string, log=LOG_FILE))
    
    # Download the git repository onto the remote server
    # AJK TODO temporary for repeated testing (+1)
    run('rm -fr {home}/beiwe-backend'.format(home=REMOTE_HOME_DIR))
    get_git_repo()
    
    # Install and set up python, celery and cron
    setup_python()
    setup_celery()
    setup_cron()
    
    # Put the environment-setting file to the remote server, in order to set
    # all the user-defined values from validate_config.
    put(OS_ENVIRON_SETTING_LOCAL_FILE, OS_ENVIRON_SETTING_REMOTE_FILE)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="interactive script for managing a Beiwe Cluster")
    
    # Get the configuration values and make them environment variables
    combined_config = validate_config()
    augmented_config = augment_config(combined_config)
    write_config_to_local_file(augmented_config)
    
    # More fabric configuration
    # AJK TODO temporary hardcode, this is going to be derived from boto
    env.host_string = '54.88.7.29'
    env.user = REMOTE_USER
    env.key_filename = AWS_PEM_FILE
    
    # Run actual code
    run_remote_code()
