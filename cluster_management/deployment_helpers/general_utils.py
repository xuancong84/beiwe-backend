# Do not import from other utils files here

import logging
import os
import sys
from time import sleep

import botocore.exceptions as botoexceptions
from fabric.exceptions import NetworkError

# Folder and file names
CLUSTER_MANAGEMENT_FOLDER = os.path.abspath(__file__).rsplit('/', 2)[0]
USER_SPECIFIC_CONFIG_FOLDER = os.path.join(CLUSTER_MANAGEMENT_FOLDER, 'my_cluster_configuration')
AWS_PEM_FILE = os.path.join(USER_SPECIFIC_CONFIG_FOLDER, 'aws_deployment_key.pem')
AWS_CREDENTIALS_FILE = os.path.join(USER_SPECIFIC_CONFIG_FOLDER, 'aws_credentials.json')
OS_ENVIRON_SETTING_FILE = os.path.join(USER_SPECIFIC_CONFIG_FOLDER, 'env_values.py')


log = logging.getLogger(CLUSTER_MANAGEMENT_FOLDER)


def retry(func, *args, **kwargs):
    while True:
        print(".")
        sys.stdout.flush()
        try:
            return func(*args, **kwargs)
        except (NetworkError, botoexceptions.ClientError, botoexceptions.WaiterError) as e:
            log.debug("retrying due to %s" % e)
            sleep(3)
