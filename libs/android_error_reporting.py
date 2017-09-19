from datetime import datetime

from cronutils import ErrorSentry
from dateutil import tz

from flask import request

from raven import Client as SentryClient
from raven.transport import HTTPTransport

from config.settings import SENTRY_DSN

#old email error code:
# email_system_administrators(error_report,
#                             "Beiwe Android Crash Log: %s" % user_id,
#                             source_email="android_errors@studies.beiwe.org")

def send_android_error_report(user_id, error_report):
    # Encountered a corrupted (write error) error report upload on Apr 30 2017, adding error sentry
    # so that we get *some* report of the error occuring but also delete that file from the device.
    with ErrorSentry(SENTRY_DSN, sentry_client_kwargs={'transport': HTTPTransport}):
        #get all non-empty lines in the error report
        contents = [line for line in error_report.splitlines() if line.strip() ]
        
        # the first line contains a unix millisecond timestamp, construct a datetime
        # The printed value in the crash report is in UTC
        try: #Beiwe version greater than 4
            timestamp = datetime.fromtimestamp(float(contents[0]) / 1000)
            contents.pop(0) #remove timestamp from message text
        except ValueError: #Beiwe version 4
            timestamp = datetime.fromtimestamp(float(request.values['file_name'].split("_")[1]) / 1000)
    
        device_identifiers = contents[0].split(',')
        contents.pop(0)  # remove device identifiers from message text
    
        # Insert the actual error message as the first line
        report_title = contents[0].split(":", 1)[1].strip()
        if "}" in report_title:  #cut title at end of file name
            report_title = report_title.split("}", 1)[0] + "}"
        contents.insert(0, "Android Error: %s" % report_title)
        
        # the second line contains all the identifiers. Clean it up and parse into a dictionary.
        device_identifiers = {ID.strip().split(":",1)[0] : ID.strip().split(":",1)[1]
                                              for ID in device_identifiers}
    
        #get a useful timestamp...
        eastern_time = timestamp.replace(tzinfo=tz.gettz('UTC')).astimezone(tz.gettz('America/New_York'))
        
        #construct some useful tags for this error report, add all identifiers as tags.
        tags = {"Android_Error": "android error",
                "user_id":user_id,
                "date": str(timestamp.date()),
                "time": str(timestamp).split(" ")[1].split(".")[0],
                "eastern_date": str(eastern_time.date()),
                "eastern_time": str(eastern_time).split(" ")[1].split(".")[0]
                }
        tags.update(device_identifiers)
        
        sentry_client = SentryClient(dsn=SENTRY_DSN,
                                     tags=tags,
                                     transport=HTTPTransport )
    
        sentry_client.captureMessage("\n".join(contents))
    
    
