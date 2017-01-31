# We need to execute this file directly, so we always run the import hack
from os.path import abspath as _abspath
import imp as _imp
_current_folder_init = _abspath(__file__).rsplit('/', 1)[0]+ "/__init__.py"
_imp.load_source("__init__", _current_folder_init)

#worker command: celery -A data_processing_tasks worker --loglevel=info
# celery -A celery_data_processing.data_processing_tasks worker --loglevel=info

################################################################################
############################### Celery Config ##################################
################################################################################

from celery import Celery, states
from celery.states import SUCCESS

STARTED_OR_WAITING = [ states.PENDING,
                       states.RECEIVED,
                       states.STARTED ]

FAILED = [ states.REVOKED,
           states.RETRY,
           states.FAILURE ]

celery_app = Celery("data_processing_tasks",
                    broker='pyamqp://guest@localhost//',
                    backend='rpc://',
                    task_publish_retry=False,
                    task_track_started=True, )

#todo: what is this?
# celery_app.conf.update(
    # task_publish_retry=False,
    
    # task_track_started=True,
    
    #todo: research worker_direct
    #worker_direct
# )

################################################################################
################################### Sentry #####################################
################################################################################

import logging
from raven import Client
from raven.contrib.celery import register_signal, register_logger_signal
from config.secure_settings import SENTRY_DSN

client = Client(SENTRY_DSN)

# register a custom filter to filter out duplicate logs
register_logger_signal(client)

# The register_logger_signal function can also take an optional argument
# `loglevel` which is the level used for the handler created.
# Defaults to `logging.ERROR`
register_logger_signal(client, loglevel=logging.INFO)

# hook into the Celery error handler
register_signal(client)

# The register_signal function can also take an optional argument
# `ignore_expected` which causes exception classes specified in Task.throws
# to be ignored
register_signal(client, ignore_expected=True)

################################################################################
############################# Data Processing ##################################
################################################################################
from time import sleep
from datetime import datetime, timedelta

from cronutils import ErrorHandler
from libs.logging import email_bundled_error, email_system_administrators

from db.data_access_models import FilesToProcess, FileProcessLock
from libs.files_to_process import ProcessingOverlapError, do_process_user_file_chunks, EverythingWentFine
from config.constants import FILE_PROCESS_PAGE_SIZE, DATA_PROCESSING_NO_ERROR_STRING


@celery_app.task
def queue_user(name):
    return celery_process_file_chunks(name)

#Fixme: does this work? also doing a
queue_user.max_retries = 0

def create_file_processing_tasks():
    if FileProcessLock.islocked():
        raise ProcessingOverlapError("Data processing overlapped with a previous data indexing run.")
    FileProcessLock.lock()
    
    now = datetime.now()
    expiry = now + timedelta(hours=1)
    #set an expiry time for the next hour boundary
    
    user_ids = set(FilesToProcess(field="user_id"))
    running = []
    
    for user_id in user_ids: #queue all users, get list of futures to check
        running.append(
                queue_user.apply_async(args=[user_id],
                                       max_retries=0,
                                       expires=expiry,
                                       task_track_started=True,
                                       task_publish_retry=False,
                                       retry=False)
            #should be able to use all options from apply_async: http://docs.celeryproject.org/en/latest/reference/celery.app.task.html#celery.app.task.Task.apply_async
        )
    print "tasks:", running
    while running:
        new_running = []
        failed = []
        successful = []
        for future in running:
            #TODO: make sure these strings match.
            if future.state == SUCCESS:
                successful.append(future)
            elif future.state in FAILED:
                failed.append(future)
            elif future.state in STARTED_OR_WAITING:
                new_running.append(future)
            else:
                raise Exception("Encountered unknown celery task state: %s" % future.state)
            
        running = new_running
        print "tasks:", running
        sleep(5)
    
    FileProcessLock.unlock()
    raise EverythingWentFine(DATA_PROCESSING_NO_ERROR_STRING)


class logging_list(list):
    def append(self, p_object):
        super(logging_list, self).append(p_object)
        print p_object
        
    def extend(self, iterable):
        print (str(i) for i in iterable)
        super(logging_list, self).extend(iterable)
        
        
def celery_process_file_chunks(user_id):
    """ This is the function that is called from cron.  It runs through all new
    files that have been uploaded and 'chunks' them. Handles logic for skipping
    bad files, raising errors appropriately. """
        
    log = logging_list()
    error_handler = ErrorHandler()
    number_bad_files = 0
    
    log.append("processing files for %s" % user_id)
    
    while True:
        previous_number_bad_files = number_bad_files
        starting_length = FilesToProcess.count(user_id=user_id)
        
        log.append(str(datetime.now()) + " processing %s, %s files remaining" % (user_id, starting_length))
        #TODO: optimize these values.
        number_bad_files += do_process_user_file_chunks(
                count=FILE_PROCESS_PAGE_SIZE,
                error_handler=error_handler,
                skip_count=number_bad_files,
                user_id=user_id)
        
        if starting_length == FilesToProcess.count(user_id=user_id):  # zero files processed
            if previous_number_bad_files == number_bad_files:
                # Cases:
                #   every file broke, might as well fail here, and would cause infinite loop otherwise.
                #   no new files.
                break
            else: continue
    
    if error_handler.errors:
        try:
            error_handler.raise_errors()
        except Exception as e:
            #TODO: in the middle of making this email appropriately upon failure.
            log.append("Data Processing Error: %s" % user_id)
            log.append(e)
            email_bundled_error(e, "Data Processing Error: %s" % user_id)
            return

    email_system_administrators("Everything went fine %s" % DATA_PROCESSING_NO_ERROR_STRING,
                                "No Data Processing Error: %s" % user_id,
                                source_email="processing.status@studies.beiwe.org" )
    
    