# We need to execute this file directly, so we always run the import hack
from os.path import abspath as _abspath
import imp as _imp

from libs.logging import email_system_administrators

_current_folder_init = _abspath(__file__).rsplit('/', 1)[0]+ "/__init__.py"
_imp.load_source("__init__", _current_folder_init)

#worker commands:
# celery -A data_processing_tasks worker --loglevel=info
# celery -A celery_data_processing.data_processing_tasks worker --loglevel=info

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
                    task_track_started=True )

################################################################################
############################# Data Processing ##################################
################################################################################
from time import sleep
from datetime import datetime, timedelta

from cronutils import ErrorSentry

from config.constants import FILE_PROCESS_PAGE_SIZE, DATA_PROCESSING_NO_ERROR_STRING, CELERY_EXPIRY_MINUTES, CELERY_ERROR_REPORT_TIMEOUT_SECONDS
from config.secure_settings import SENTRY_DSN
from db.data_access_models import FilesToProcess, FileProcessLock
from libs.files_to_process import ProcessingOverlapError, do_process_user_file_chunks, EverythingWentFine

@celery_app.task
def queue_user(name):
    return celery_process_file_chunks(name)

#Fixme: does this work? also doing a
queue_user.max_retries = 0

def create_file_processing_tasks():
    #literally wrapping the entire thing in an ErrorSentry...
    with ErrorSentry(SENTRY_DSN) as error_sentry:
        
        if FileProcessLock.islocked():
            handle_locked()
        FileProcessLock.lock()
        
        now = datetime.now()
        expiry = now + timedelta(minutes=CELERY_EXPIRY_MINUTES)
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


def handle_locked():
    """ Creates a useful error report with information about the run time. """
    timedelta_since_last_run = FileProcessLock.get_time_since_locked()
    if timedelta_since_last_run.total_seconds() > CELERY_ERROR_REPORT_TIMEOUT_SECONDS:
        error_msg =\
            "Data processing has overlapped with a prior data index run that started more than %s minutes ago.\n"\
            "That prior run has been going for %s hour(s), %s minute(s)"
        error_msg = error_msg % (CELERY_ERROR_REPORT_TIMEOUT_SECONDS / 60,
                                 str(int(timedelta_since_last_run.total_seconds() / 60 / 60)),
                                 str(int(timedelta_since_last_run.total_seconds() / 60 % 60)))
        
        if timedelta_since_last_run.total_seconds() > CELERY_ERROR_REPORT_TIMEOUT_SECONDS * 4:
            email_system_administrators(error_msg, "DATA PROCESSING OVERLOADED, CHECK SERVER")
        raise ProcessingOverlapError(error_msg)


# we are not really using the this class for much anymore, but it is there if we need it in future
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
    number_bad_files = 0
    error_sentry = ErrorSentry(sentry_dsn=SENTRY_DSN,
                               sentry_client_kwargs = {"tags":{ "user_id": user_id } }
    )
    log.append("processing files for %s" % user_id)
    
    while True:
        previous_number_bad_files = number_bad_files
        starting_length = FilesToProcess.count(user_id=user_id)
        
        log.append(str(datetime.now()) + " processing %s, %s files remaining" % (user_id, starting_length))
        number_bad_files += do_process_user_file_chunks(
                count=FILE_PROCESS_PAGE_SIZE,
                error_handler=error_sentry,
                skip_count=number_bad_files,
                user_id=user_id)

        if starting_length == FilesToProcess.count(user_id=user_id):  # zero files processed
            if previous_number_bad_files == number_bad_files:
                # Cases:
                #   every file broke, blow up. (would cause infinite loop otherwise)
                #   no new files.
                break
            else:
                continue
