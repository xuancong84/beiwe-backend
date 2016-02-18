#heart: http://stackoverflow.com/questions/12523044/how-can-i-tail-a-log-file-in-python

import subprocess
from libs.logging import log_and_email_error

class ModWSGIError(Exception): pass
class SegfaultError(Exception): pass
class BucketBrigadeError(Exception): pass
class UnkownIOError(Exception): pass

f = subprocess.Popen(['tail','-F',"/var/log/apache2/error.log"],
                     stdout=subprocess.PIPE,stderr=subprocess.PIPE)

while True:
    line = f.stdout.readline()

    if "End of script output before headers" in line:
        log_and_email_error( ModWSGIError("WSGI timeout error"),
                             log_message=line )
        continue

    if "Segmentation fault" in line:
        log_and_email_error( SegfaultError("Apache encountered a segfault"),
                             log_message=line )
        continue

    if "Unable to get bucket brigade for request" in line:
        log_and_email_error( BucketBrigadeError("Bucket brigade error"),
                                 log_message=line )
        continue

    if "IOError: failed to write data" in line:
        log_and_email_error( UnkownIOError("WSGI IOError"),
                             log_message=line )
        continue