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
import json
import os
import re
import sys
from os.path import relpath
from pprint import pprint

from fabric.api import put, run, sudo, env as fabric_env

from deployment_helpers.aws.elastic_beanstalk import (create_eb_environment,
    check_if_eb_environment_exists)
from deployment_helpers.aws.elastic_compute_cloud import\
    (get_manager_instance_by_eb_environment_name, create_processing_control_server,
    create_processing_server, get_manager_public_ip, get_manager_private_ip)
from deployment_helpers.aws.rds import create_new_rds_instance
from deployment_helpers.configuration_utils import (
    are_aws_credentials_present, is_global_configuration_valid,
    reference_environment_configuration_file, reference_data_processing_server_configuration,
    validate_beiwe_environment_config, create_finalized_configuration)
from deployment_helpers.constants import (
    APT_GET_INSTALLS, FILES_TO_PUSH, LOG_FILE,
    PUSHED_FILES_FOLDER, REMOTE_HOME_DIR, REMOTE_USERNAME,
    DEPLOYMENT_ENVIRON_SETTING_REMOTE_FILE_PATH, STAGED_FILES,
    DO_SETUP_EB_UPDATE_OPEN, DO_CREATE_MANAGER,
    HELP_SETUP_NEW_ENVIRONMENT, get_beiwe_python_environment_variables_file_path,
    get_server_configuration_file_path, ENVIRONMENT_NAME_RESTRICTIONS,
    DO_CREATE_ENVIRONMENT, USER_SPECIFIC_CONFIG_FOLDER, EXTANT_ENVIRONMENT_PROMPT,
    get_pushed_full_processing_server_env_file_path, LOCAL_CRONJOB_FILE_PATH,
    REMOTE_CRONJOB_FILE_PATH, get_finalized_environment_variables, get_server_configuration_file,
    LOCAL_GIT_KEY_PATH, REMOTE_GIT_KEY_PATH, REMOTE_PYENV_INSTALLER_FILE,
    LOCAL_PYENV_INSTALLER_FILE, REMOTE_CELERY_FILE, LOCAL_CELERY_FILE)
from deployment_helpers.general_utils import log, EXIT, current_time_string, do_zip_reduction


# Fabric configuration
class FabricExecutionError(Exception): pass
fabric_env.abort_exception = FabricExecutionError
fabric_env.abort_on_prompts = True


####################################################################################################
################################### Fabric Operations ##############################################
####################################################################################################

def get_global_configuration(param):
    pass


def configure_fabric(eb_environment_name, ip_address):
    get_finalized_environment_variables(eb_environment_name)
    fabric_env.host_string = ip_address
    fabric_env.user = REMOTE_USERNAME
    fabric_env.key_filename = get_global_configuration('DEPLOYMENT_KEY_FILE_PATH')


def setup_profile():
    for local_relative_file, remote_relative_file in FILES_TO_PUSH:
        local_file = os.path.join(PUSHED_FILES_FOLDER, local_relative_file)
        remote_file = os.path.join(REMOTE_HOME_DIR, remote_relative_file)
        put(local_file, remote_file)


def get_git_repo():
    """ Get a local copy of the git repository """
    # Grab the read-only key from the local repository
    put(LOCAL_GIT_KEY_PATH, REMOTE_GIT_KEY_PATH)
    run('chmod 600 {key_path}'.format(key_path=REMOTE_GIT_KEY_PATH))
    
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
    put(LOCAL_PYENV_INSTALLER_FILE, REMOTE_PYENV_INSTALLER_FILE)
    run('chmod +x {file}'.format(file=REMOTE_PYENV_INSTALLER_FILE))
    run(REMOTE_PYENV_INSTALLER_FILE)

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
    # Copy the script from the local repository onto the remote server,
    # make it executable and execute it.
    put(LOCAL_CELERY_FILE, REMOTE_CELERY_FILE)
    run('chmod +x {file}'.format(file=REMOTE_CELERY_FILE))
    run('{file} >> {log}'.format(file=REMOTE_CELERY_FILE, log=LOG_FILE))


def setup_cron():
    # Copy the cronjob file onto the remote server and add it to the remote crontab
    put(LOCAL_CRONJOB_FILE_PATH, REMOTE_CRONJOB_FILE_PATH)
    run('crontab -u {user} {file}'.format(file=REMOTE_CRONJOB_FILE_PATH, user=REMOTE_USERNAME))


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
    python_config_file = get_pushed_full_processing_server_env_file_path(eb_environment_name)
    put(python_config_file, DEPLOYMENT_ENVIRON_SETTING_REMOTE_FILE_PATH)


####################################################################################################
#################################### CLI Utility ###################################################
####################################################################################################

def do_fail_if_environment_does_not_exist(name):
    environment_exists = check_if_eb_environment_exists(name)
    if not environment_exists:
        log.error("There is already an environment named '%s'" % name.lower())
        EXIT(1)


def do_fail_if_environment_exists(name):
    environment_exists = check_if_eb_environment_exists(name)
    if environment_exists:
        log.error("There is already an environment named '%s'" % name.lower())
        EXIT(1)


def do_fail_if_bad_environment_name(name):
    if not (4 <= len(name) < 40):
        log.error("That name is either too long or too short.")
        EXIT(1)
    
    if not re.match("^[a-zA-Z0-9-]+$", name) or name.endswith("-"):
        log.error("that is not a valid Elastic Beanstalk environment name.")
        EXIT(1)


def prompt_for_new_eb_environment_name():
    print ENVIRONMENT_NAME_RESTRICTIONS
    name = raw_input()
    do_fail_if_bad_environment_name(name)
    return name


def prompt_for_extant_eb_environment_name():
    print EXTANT_ENVIRONMENT_PROMPT
    name = raw_input()
    environment_exists = check_if_eb_environment_exists(name)
    if not environment_exists:
        log.error("There is no environment with the name %s" % environment_exists)
        EXIT(1)
    validate_beiwe_environment_config(name)
    return name

####################################################################################################
##################################### AWS Operations ###############################################
####################################################################################################

def do_setup_eb_update():
    print "\n", DO_SETUP_EB_UPDATE_OPEN
    
    files = [f for f in os.listdir(STAGED_FILES) if f.lower().endswith(".zip")]
    files.sort()
    
    if not files:
        print "Could not find any zip files in " + STAGED_FILES
        EXIT(1)
    
    print "Enter the version of the codebase do you want to use:"
    for i, file_name in enumerate(files):
        print "[%s]: %s" % (i + 1, file_name)
    print "(press CTL-C to cancel)\n"
    try:
        index = int(raw_input("$ "))
    except Exception:
        log.error("Could not parse input.")
        EXIT(1)
    
    if index < 1 or index > len(files):
        log.error("%s was not a valid option." % index)
        EXIT(1)
    
    # handle 1-indexing
    file_name = files[index - 1]
    # log.info("Processing %s..." % file_name)
    time_ext = current_time_string().replace(" ", "_").replace(":", "_")
    output_file_name = file_name[:-4] + "_processed_" + time_ext + ".zip"
    do_zip_reduction(file_name, STAGED_FILES, output_file_name)
    log.info("Done processing %s." % file_name)
    log.info("The new file %s has been placed in %s" % (output_file_name, STAGED_FILES))
    print(
    "You can now provide Elastic Beanstalk with %s to run an automated deployment of the new code." % output_file_name)
    EXIT(0)


def do_create_environment():
    print DO_CREATE_ENVIRONMENT
    name = prompt_for_new_eb_environment_name()
    do_fail_if_bad_environment_name(name)
    do_fail_if_environment_exists(name)
    validate_beiwe_environment_config(name)  # Exits if any non-autogenerated credentials are bad.
    create_new_rds_instance(name)
    create_finalized_configuration(name)
    create_eb_environment(name)
    log.info("Created Beiwe cluster environment successfully")


def do_help_setup_new_environment():
    print HELP_SETUP_NEW_ENVIRONMENT
    name = prompt_for_new_eb_environment_name()
    do_fail_if_bad_environment_name(name)
    do_fail_if_environment_exists(name)

    beiwe_environment_fp = get_beiwe_python_environment_variables_file_path(name)
    processing_server_settings_fp = get_server_configuration_file_path(name)
    extant_files = os.listdir(USER_SPECIFIC_CONFIG_FOLDER)
    
    for fp in (beiwe_environment_fp, processing_server_settings_fp):
        if os.path.basename(fp) in extant_files:
            log.error("is already a file at %s" % relpath(beiwe_environment_fp))
            EXIT(1)
    
    with open(beiwe_environment_fp, 'w') as f:
        json.dump(reference_environment_configuration_file(), f, indent=1)
    with open(processing_server_settings_fp, 'w') as f:
        json.dump(reference_data_processing_server_configuration(), f, indent=1)
    
    print "Environment specific files have been created at %s and %s." % (
        relpath(beiwe_environment_fp),
        relpath(processing_server_settings_fp),
    )
    
    # Note: we actually cannot generate RDS credentials until we have a server, this is because
    # the hostname cannot exist until the server exists.
    print """After filling in the required contents of these newly created files you will be able
    to run the -create-environment command.  Note that several more credentials files will be
    generated as part of that process. """
    

def do_create_manager():
    print DO_CREATE_MANAGER
    name = prompt_for_extant_eb_environment_name()
    do_fail_if_environment_does_not_exist(name)
    instance = get_manager_instance_by_eb_environment_name(name)
    
    if instance is not None:
        log.error("There is already a manager server for the %s cluster." % name)
        EXIT(1)
    
    try:
        settings = get_server_configuration_file(name)
    except Exception as e:
        log.error("could not read settings file")
        log.error(e)
        EXIT(1)
        
    log.info("creating manager server for %s..." % name)
    instance = create_processing_control_server(name, settings["MANAGER_SERVER_INSTANCE_TYPE"])
    public_ip = instance['NetworkInterfaces'][0]['PrivateIpAddresses'][0]['Association']['PublicIp']
    # TODO: fabric up the rabbitmq and cron task, ensure other servers can connect, watch data process


def do_create_worker():
    print DO_CREATE_MANAGER
    name = prompt_for_extant_eb_environment_name()
    do_fail_if_environment_does_not_exist(name)
    manager_public_ip = get_manager_public_ip(name)
    manager_private_ip = get_manager_private_ip(name)
    
    if get_manager_instance_by_eb_environment_name(name) is None:
        log.error("There is no manager server for the %s cluster, cannot deploy a worker until there is." % name)
        EXIT(1)
    
    try:
        settings = get_server_configuration_file_path(name)
    except Exception as e:
        log.error("could not read settings file")
        log.error(e)
        EXIT(1)
    
    log.info("creating worker server for %s..." % name)
    instance = create_processing_server(name, settings["MANAGER_SERVER_INSTANCE_TYPE"])
    # TODO: fabric up the worker with the celery/supervisord and ensure it can connect to manager.



####################################################################################################
####################################### Validation #################################################
####################################################################################################
    
def cli_args_validation():
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
    
    # Warning: any change to format here requires you re-check all parameter validation
    parser = argparse.ArgumentParser(
             description="interactive set of commands for managing a Beiwe Cluster")
    
    parser.add_argument(
            '-create-environment',
            action="count",
            help="creates new environment with the provided environment name"
    )
    parser.add_argument(
            '-create-manager',
            action="count",
            help="creates a data processing manager for the provided environment"
    )
    parser.add_argument(
            '-create-worker',
            action="count",
            help="creates a data processing worker for the provided environment"
    )
    # parser.add_argument(
    #         '-terminate-manager',
    #         action="count",
    #         help="terminates the data processing manager for the provided environment"
    # )
    # parser.add_argument(
    #         '-terminate-worksers',
    #         action="count",
    #         help="teminates the data processing workers for the provided environment"
    # )
    # parser.add_argument(
    #         '-update-workers',
    #         action="count",
    #         help="updates the beiwe code for all workers in the provided environment"
    # )
    # parser.add_argument(
    #         '-update-manager',
    #         action="count",
    #         help="updates the beiwe code for the manager in the provided environment"
    # )
    parser.add_argument(
            "-setup-elastic-beanstalk-update",
            action="count",
            help="updates the beiwe code for the provided Elastic Beanstalk environment"
    )
    parser.add_argument(
            "-help-setup-new-environment",
            action="count",
            help= "assists in creation of configuration files for a beiwe environment deployment"
    )
    
    # Notes:
    # this arguments variable is not iterable.
    # access entities as arguments.long_name_of_argument, like arguments.update_manager
    arguments = parser.parse_args()

    # print help message if no arguments were supplied
    if len(sys.argv) == 1:
        parser.print_help()
        EXIT()

    return arguments


####################################################################################################
##################################### Argument Parsing #############################################
####################################################################################################

if __name__ == "__main__":
    # validate the global configuration file
    if not all((are_aws_credentials_present(), is_global_configuration_valid())):
        EXIT(1)
    
    # get CLI arguments, see function for details
    arguments = cli_args_validation()
    # pprint (vars(arguments))
    
    if arguments.help_setup_new_environment:
        do_help_setup_new_environment()
        EXIT(0)
    if arguments.setup_elastic_beanstalk_update:
        do_setup_eb_update()
        EXIT(0)

    if arguments.create_environment:
        do_create_environment()
        EXIT(0)
        
    if arguments.create_manager:
        do_create_manager()
        EXIT(0)
    
    if arguments.create_worker:
        do_create_worker()
        EXIT(0)
