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
        try: raise ModWSGIError(line)
        except ModWSGIError as e:
            log_and_email_error(e, message="encountered a timeout error in the data access api")
            continue

    if "Segmentation fault" in line:
        try: raise SegfaultError(line)
        except SegfaultError as e:
            log_and_email_error(e, message="Apache encountered a segfault")
            continue

    if "Unable to get bucket brigade for request" in line:
        try: raise BucketBrigadeError(line)
        except BucketBrigadeError as e:
            log_and_email_error(e, message="Bucket brigade error")
            continue

    if "IOError: failed to write data" in line:
        try: raise UnkownIOError(line)
        except UnkownIOError as e:
            log_and_email_error(e, message="WSGI IOError")
            continue
