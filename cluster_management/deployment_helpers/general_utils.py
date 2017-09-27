# Do not import from other utils files here, only import

import logging
import os
import sys
from time import sleep

import botocore.exceptions as botoexceptions
from fabric.exceptions import NetworkError

CLUSTER_MANAGEMENT_FOLDER = os.path.abspath(__file__).rsplit('/', 2)[0]
log = logging.getLogger(CLUSTER_MANAGEMENT_FOLDER)

def retry(function, *args, **kwargs):
    while True:
        print(".")
        sys.stdout.flush()
        try:
            return function(*args, **kwargs)
        except (NetworkError, botoexceptions.ClientError, botoexceptions.WaiterError) as e:
            log.debug("retrying due to %s" % e)
            sleep(3)
