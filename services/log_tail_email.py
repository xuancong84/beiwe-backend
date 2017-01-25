#heart: http://stackoverflow.com/questions/12523044/how-can-i-tail-a-log-file-in-python

import subprocess
from libs.logging import log_and_email_500_error

class ModWSGIError(Exception): pass
class SegfaultError(Exception): pass
class BucketBrigadeError(Exception): pass
class UnkownIOError(Exception): pass

f = subprocess.Popen(['tail','-F',"/var/log/apache2/error.log"],
                     stdout=subprocess.PIPE,stderr=subprocess.PIPE)

while True:
    line = f.stdout.readline()

    if "End of script output before headers" in line:
        log_and_email_500_error(ModWSGIError("WSGI timeout error"),
                                log_message=line)
        continue

    if "Segmentation fault" in line:
        log_and_email_500_error(SegfaultError("Apache encountered a segfault"),
                                log_message=line)
        continue

    # As of Feb 19 2016 there are no complaints about function of the data access api.
    # I think (70007)The timeout specified has expired occurs when a connection is lost and occurs with mobile uploads, and
    # (70008)Partial results are valid but processing is incomplete occurs when a download via the data api is cancelled.
    # (these guesses are from looking at the IP addresses included in these errors.
    # if "Unable to get bucket brigade for request" in line:
    #     log_and_email_error( BucketBrigadeError("Bucket brigade error"),
    #                              log_message=line )
    #     continue

    # IOError means a connection was dropped, usually by the user.
    # if "IOError: failed to write data" in line:
    #     log_and_email_error( UnkownIOError("WSGI IOError"),
    #                          log_message=line )
    #     continue