# Do not import from other utils files here
import logging
import random
import string
from datetime import datetime
from time import sleep

import botocore.exceptions as botoexceptions
import coloredlogs
from fabric.exceptions import NetworkError

coloredlogs.install(fmt="%(levelname)s %(name)s: %(message)s")

# Set logging levels
logging.getLogger('boto3').setLevel(logging.WARNING)
logging.getLogger('botocore').setLevel(logging.WARNING)
logging.getLogger('paramiko.transport').setLevel(logging.WARNING)

log = logging.getLogger("cluster-management")
log.setLevel(logging.DEBUG)


def current_time_string():
    """ used for pretty-printing the date in some logging statements"""
    return ("%s" % datetime.now())[:-7]


def EXIT(n=None):
    """ Ipython has some weirdness with exit statements. """
    if n is None:
        n = 0
    try:
        exit(n)
    except Exception:
        log.warn("ipython forcible exit...")
        sleep(0.05)
        import os
        os._exit(1)


def retry(func, *args, **kwargs):
    for i in range(10):
        try:
            return func(*args, **kwargs)
        except (NetworkError, botoexceptions.ClientError, botoexceptions.WaiterError) as e:
            log.error('Encountered error of type %s with error message "%s"\nRetrying with attempt %s.'
                      % (e.__name__, e, i+1) )
            sleep(3)


ALPHANUMERICS = string.ascii_letters + string.digits

#postgress passwords are alphanumerics plus "typable special characters" that are not not /, ", or @
POSTGRESS_PASSWORD_CHARACTERS = ALPHANUMERICS + '!#$%^&*()<>?[]{}_+='

def random_password_string(length):
    return ''.join(random.choice(POSTGRESS_PASSWORD_CHARACTERS) for _ in xrange(length))

def random_alphanumeric_string(length):
    return ''.join(random.choice(ALPHANUMERICS) for _ in xrange(length))

def random_alphanumeric_starting_with_letter(length):
    return random.choice(string.ascii_letters) + random_alphanumeric_string(length - 1)


def increment_identifier(base_string, increment_string):
    """ Finds the next number to use for an incrementing numerical suffix"""
    splits = increment_string.split(base_string)
    
    if len(splits) != 2:
        raise Exception("%s not found or found more than once in %s" % (base_string, increment_string))

    prefix, suffix = splits
    if suffix is "":
        suffix_increment = 1
    else:
        suffix_increment = int(suffix) + 1
    return prefix + str(suffix_increment)
    