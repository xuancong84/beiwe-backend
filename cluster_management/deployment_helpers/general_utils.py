# Do not import from other utils files here
import logging, coloredlogs, string, random

coloredlogs.install(fmt="%(levelname)s %(name)s: %(message)s")

# Set logging levels
logging.getLogger('boto3').setLevel(logging.WARNING)
logging.getLogger('botocore').setLevel(logging.WARNING)
logging.getLogger('paramiko.transport').setLevel(logging.WARNING)

log = logging.getLogger("cluster-management")
log.setLevel(logging.DEBUG)

#TODO: the remaining variables should be moved to some kind of configuration file rather than utils.

APT_GET_INSTALLS = [
    'ack-grep',  # Search within files
    'build-essential',  # Includes a C compiler for compiling python
    'htop',
    'libbz2-dev',
    'libreadline-gplv2-dev',
    'libsqlite3-dev',
    'libssl-dev',
    # AJK TODO do I need this? github says I do
    # 'mailutils',  # Necessary for cronutils
    'moreutils',  # Necessary for cronutils
    'nload',
    'rabbitmq-server',  # Queue tasks to run using celery
    'sendmail',  # Necessary for cronutils
    'silversearcher-ag',  # Search within files
]

# Files to push from the local server before the rest of launch
# This is a list of 2-tuples of (local_path, remote_path) where local_path is located
# in PUSHED_FILES_FOLDER and remote_path is located in REMOTE_HOME_DIRECTORY.
FILES_TO_PUSH = [
    ('bash_profile.sh', '.profile'),  # standard bash profile
    ('.inputrc', '.inputrc'),  # modifies what up-arrow, tab etc. do
    ('known_hosts', '.ssh/known_hosts'),  # allows git clone without further prompting
]

##
## Code
##

import botocore.exceptions as botoexceptions
from time import sleep
from fabric.exceptions import NetworkError


def retry(func, *args, **kwargs):
    for i in range(10):
        try:
            return func(*args, **kwargs)
        except (NetworkError, botoexceptions.ClientError, botoexceptions.WaiterError) as e:
            log.error('Encountered error of type %s with error message "%s"\nRetrying with attempt %s.'
                      % (e.__name__, e, i+1) )
            sleep(3)


TYPEABLE_CHARACTERS = string.ascii_letters + '0123456789!@#$%^&*()<>?[]{}_+='

def random_typeable_string(length):
    return ''.join(random.choice(TYPEABLE_CHARACTERS) for _ in xrange(length))

def random_alphanumeric_string(length):
    return ''.join(random.choice(TYPEABLE_CHARACTERS) for _ in xrange(length))

