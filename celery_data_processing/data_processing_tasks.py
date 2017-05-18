# We need to execute this file directly, so we always run the import hack
from os.path import abspath as _abspath
import imp as _imp
_current_folder_init = _abspath(__file__).rsplit('/', 1)[0]+ "/__init__.py"
_imp.load_source("__init__", _current_folder_init)

from kombu.exceptions import OperationalError
from pymongo.errors import CursorNotFound

from libs.logging import email_system_administrators
from config.secure_settings import MONGO_IP

from celery import Celery, states
from celery.states import FAILURE, SUCCESS

STARTED_OR_WAITING = [ states.PENDING,
                       states.RECEIVED,
                       states.STARTED ]

FAILED = [ states.REVOKED,
           states.RETRY,
           states.FAILURE ]

celery_app = Celery("data_processing_tasks",
                    broker='pyamqp://guest@%s//' % MONGO_IP,
                    backend='rpc://',
                    task_publish_retry=False,
                    task_track_started=True )

################################################################################
############################# Data Processing ##################################
################################################################################
from time import sleep
from datetime import datetime, timedelta

from cronutils import ErrorSentry
from raven.transport import HTTPTransport

from config.constants import FILE_PROCESS_PAGE_SIZE, CELERY_EXPIRY_MINUTES, CELERY_ERROR_REPORT_TIMEOUT_SECONDS
from config.secure_settings import SENTRY_DSN
from db.data_access_models import FilesToProcess, FileProcessLock
from libs.files_to_process import ProcessingOverlapError, do_process_user_file_chunks

@celery_app.task
def queue_user(name):
    return celery_process_file_chunks(name)

#Fixme: does this work? also doing a
queue_user.max_retries = 0

def safe_queue_user(*args, **kwargs):
    for i in range(100):
        try:
            return queue_user.apply_async( *args, **kwargs)
        except OperationalError:
            if i < 3:
                pass
            else:
                raise

def get_user_list_safely(retries=10):
    """ This error started occurring on occasionally on Mar 22, 2017, we don't know why. """
    try:
        return set(FilesToProcess(field="user_id"))
    except CursorNotFound:
        if retries < 1:
            raise
        print "encountered cursor error, retrying..."
        sleep(0.1)
        return get_user_list_safely(retries=retries - 1)

def create_file_processing_tasks():
    #literally wrapping the entire thing in an ErrorSentry...
    with ErrorSentry(SENTRY_DSN,
                     sentry_client_kwargs={'transport':HTTPTransport}) as error_sentry:
        print error_sentry.sentry_client.is_enabled()
        if FileProcessLock.islocked():
            report_file_processing_locked_and_exit()
            exit(0) #This is really a safety check, this code should not actually be reachable.
        else:
            FileProcessLock.lock()
            
        print "starting."
        now = datetime.now()
        expiry = now + timedelta(minutes=CELERY_EXPIRY_MINUTES)
        user_ids = get_user_list_safely()
        running = []
        
        for user_id in user_ids:
            # queue all users, get list of futures to check
            #Apparently this can fail sometimes deep inside amqp/transport.py in read_frame at line 237
            # with an OperationalError, so we are wrapping it in a function to do some retries if it fails.
            running.append(safe_queue_user(args=[user_id],
                                           max_retries=0,
                                           expires=expiry,
                                           task_track_started=True,
                                           task_publish_retry=False,
                                           retry=False) )
        print "tasks:", running
        
        while running:
            new_running = []
            failed = []
            successful = []
            for future in running:
                # success = False
                # fail = False
                # waiting = False
                state = future.state
                
                if state == SUCCESS:
                    #we are getting some very weird errors where this string does not match.
                    successful.append(future)
                    # success = True
                
                if state in FAILED:
                    failed.append(future)
                    # fail = True
                    
                if state in STARTED_OR_WAITING:
                    new_running.append(future)
                    # waiting = True
                
                # if not success and not fail and not waiting:
                #     #this is all debugging code to try to identify what is going on with a specific
                #     # bug in which future.state IS DEFINITELY EQUAL to "SUCCESS", but the check above
                #     # fails to catch that. The value is probably changing between checks.
                #     lc1 = future.state == 'SUCCESS'
                #     lc2 = states.SUCCESS == 'SUCCESS'
                #     lc3 = states.SUCCESS == future.state
                #     lc4 = future.state == u'SUCCESS'
                #     lc5 = states.SUCCESS == u'SUCCESS'
                #     lc6 = states.SUCCESS == unicode(future.state)
                #     lc7 = states.SUCCESS == str(future.state)
                #
                #     msg = "Encountered unknown celery task state: '%s' \n " % future.state
                #
                #     msg = msg + "literal comparison future.state == 'SUCCESS': %s\n" % lc1
                #     msg = msg + "literal comparison states.SUCCESS == 'SUCCESS': %s\n" % lc2
                #     msg = msg + "literal comparison states.SUCCESS == future.state: %s\n" % lc3
                #     msg = msg + "literal comparison future.state == u'SUCCESS': %s\n" % lc4
                #     msg = msg + "literal comparison states.SUCCESS == u'SUCCESS': %s\n" % lc5
                #     msg = msg + "literal comparison states.SUCCESS == unicode(future.state): %s\n" % lc6
                #     msg = msg + "literal comparison states.SUCCESS == str(future.state): %s\n" % lc7
                #
                #     msg = msg + "success: %s\n" % success
                #     msg = msg + "fail: %s\n" % fail
                #     msg = msg + "waiting: %s\n" % waiting
                #     msg = msg + "success constant value: %s\n" % states.SUCCESS
                #     msg = msg + "future.state: %s\n" % future.state
                #     msg = msg + "STARTED_OR_WAITING states: %s\n" % str(STARTED_OR_WAITING)
                #     msg = msg + "FAILED states: %s\n" % str(FAILED)
                #     with error_sentry:
                #         raise Exception(msg)
                
            running = new_running
            print "tasks:", running
            if running:
                sleep(5)
                
        print "Finished, unlocking."
        FileProcessLock.unlock() #This must be ___inside___ the with statement


def report_file_processing_locked_and_exit():
    """ Creates a useful error report with information about the run time. """
    timedelta_since_last_run = FileProcessLock.get_time_since_locked()
    print "timedelta %s" % timedelta_since_last_run.total_seconds()
    if timedelta_since_last_run.total_seconds() > CELERY_ERROR_REPORT_TIMEOUT_SECONDS:
        error_msg =\
            "Data processing has overlapped with a prior data index run that started more than %s minutes ago.\n"\
            "That prior run has been going for %s hour(s), %s minute(s)"
        error_msg = error_msg % (CELERY_ERROR_REPORT_TIMEOUT_SECONDS / 60,
                                 str(int(timedelta_since_last_run.total_seconds() / 60 / 60)),
                                 str(int(timedelta_since_last_run.total_seconds() / 60 % 60)))
        
        if timedelta_since_last_run.total_seconds() > CELERY_ERROR_REPORT_TIMEOUT_SECONDS * 4:
            error_msg = "DATA PROCESSING OVERLOADED, CHECK SERVER.\n" + error_msg
            email_system_administrators(error_msg, "DATA PROCESSING OVERLOADED, CHECK SERVER")
        raise ProcessingOverlapError(error_msg)


# we are not really using the this class for much anymore, but it is there if we need it in future
class LogList(list):
    def append(self, p_object):
        super(LogList, self).append(p_object)
        print p_object
        
    def extend(self, iterable):
        print (str(i) for i in iterable)
        super(LogList, self).extend(iterable)
        
        
def celery_process_file_chunks(user_id):
    """ This is the function that is called from cron.  It runs through all new
    files that have been uploaded and 'chunks' them. Handles logic for skipping
    bad files, raising errors appropriately. """
    log = LogList()
    number_bad_files = 0
    error_sentry = ErrorSentry(SENTRY_DSN,
                               sentry_client_kwargs = {"tags":{ "user_id": user_id },
                                                       'transport':HTTPTransport }
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
