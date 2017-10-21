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
import os
import sys
from time import sleep

from fabric.api import env, put, run, sudo

from deployment_helpers.configuration_utils import (
    are_aws_credentials_present, is_global_configuration_valid)
from deployment_helpers.constants import (
    APT_GET_INSTALLS, FILES_TO_PUSH, LOG_FILE,
    PUSHED_FILES_FOLDER, REMOTE_HOME_DIR, REMOTE_USERNAME,
    DEPLOYMENT_ENVIRON_SETTING_REMOTE_FILE_PATH, get_beiwe_environment_file_path)
from deployment_helpers.general_utils import log, EXIT


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
    # FIXME: for local testing this uses the django branch
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
    run('{pyenv} install -f 2.7.14'.format(pyenv=pyenv_exec))
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
    run('crontab -u {user} {file}'.format(file=cronjob_remote_file, user=REMOTE_USERNAME))


def run_remote_code(eb_environment_name):
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
    get_git_repo()
    
    # Install and set up python, celery and cron
    setup_python()
    setup_celery()
    setup_cron()
    
    # Put the environment-setting file to the remote server, in order to set
    # all the user-defined values from validate_config.
    put(get_beiwe_environment_file_path(eb_environment_name), DEPLOYMENT_ENVIRON_SETTING_REMOTE_FILE_PATH)

def test_args_for_environment():
    """ argparse is not well suited to printing a nice message when a particular parameter is missing. """
    # check if parameter present
    arguments_sans_values = [arg.split("=")[0] for arg in sys.argv]
    # get value
    parameter_value = [arg.split("=")[1] for arg in sys.argv if "--environment=" in arg]
    # test with useful short-circuiting if --environment exists and has a real value
    if "--environment" not in arguments_sans_values or not parameter_value or not parameter_value[0]:
        log.error("You must provide a value to --environments, '--environment=abc123'")
        sleep(0.1)
        EXIT(1)
        
    
if __name__ == "__main__":
    if not all((are_aws_credentials_present(), is_global_configuration_valid())):
        EXIT(1)
    test_args_for_environment()
    
    parser = argparse.ArgumentParser(description="interactive set of commands for managing a Beiwe Cluster")
    
    # helper for creating the configuratiion for a deployment
    # list ip addresses for workers and managers
    # open-close ssh for worker and manager instances
    # create a manager
    # terminate manager
    # create N workers
    # terminate workers
    # update workers?
    # create elastic beanstalk and RDS
    # setup SSL and URL???
    parser.add_argument('--environment',
                        help="(Required) The name of the Beiwe environment to run an operation on")
    
    requires_environment = {
        'create_environment': "creates new environment with the provided environment name",
        'create_manager': "creates a data processing manager for the provided environment",
        'create_workers': "creates a data processing worker for the provided environment",
        "terminate_manager": "terminates the data processing manager for the provided environment",
        "terminate_worksers": "teminates the data processing workers for the provided environment",
        "update_workers": "updates the beiwe code for all workers in the provided environment",
        "update_manager": "updates the beiwe code for the manager in the provided environment",
        "update_elastic_beanstalk": "updates the beiwe code for the provided Elastic Beanstalk environment",
    }
    
    for arg, help in requires_environment.iteritems():
        parser.add_argument(arg, help=help, action="count")

    arguments = parser.parse_args()
    # so far all arguments require the environment be provided.
        
    print arguments

    EXIT(1)
    raise Exception("aoeuaoeuaoeu")
    # TODO: basic functiionality
    # prompt for environment name
    # validate some subset of credentials
    
    
    # # Get the configuration values and make them environment variables
    # combined_config = validate_config()
    # augmented_config = augment_config(combined_config)
    # write_config_to_local_file(augmented_config)
    #
    # # More fabric configuration
    # # AJK TODO temporary hardcode, this is going to be derived from boto
    # env.host_string = '54.88.7.29'
    # env.user = REMOTE_USERNAME
    # env.key_filename = AWS_PEM_FILE
    #
    # # Run actual code
    # run_remote_code()
