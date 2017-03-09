from datetime import datetime
from flask import request

from raven import Client as SentryClient
from raven.transport import HTTPTransport

from config.secure_settings import SENTRY_DSN

#old email error code:
# email_system_administrators(error_report,
#                             "Beiwe Android Crash Log: %s" % user_id,
#                             source_email="android_errors@studies.beiwe.org")

def send_android_error_report(user_id, error_report):
        
    #get all non-empty lines in the error report
    contents = [line for line in error_report.splitlines() if line.strip() ]
    
    # the first line contains a unix millisecond timestamp, contruct a datetime
    # The printed value in the crash report is in UTC
    try: #Beiwe version greater than 4
        timestamp = datetime.fromtimestamp(float(contents[0]) / 1000)
        contents[0] = str(timestamp)
    except ValueError: #Beiwe version 4
        timestamp = datetime.fromtimestamp(float(request.values['file_name'].split("_")[1]) / 1000)
        contents.insert(0, str(timestamp))
    
    # Insert the actual error message as the first line
    contents.insert(0, "Android Error: %s" % contents[2].split(":",1)[1].strip())
    
    # the second line contains all the identifiers. Clean it up and parse into a dictionary.
    identifiers = {id.strip().split(":",1)[0] : id.strip().split(":",1)[1]
                                          for id in contents[2].split(',')}
    
    #construct some useful tags for this error report, add all identifiers as tags.
    tags = {"Android Error": "android error",
            "user_id":user_id,
            "date": str(timestamp.date()) }
    tags.update(identifiers)
    
    sentry_client = SentryClient(dsn=SENTRY_DSN,
                                 tags=tags,
                                 transport=HTTPTransport)
    
    sentry_client.captureMessage("\n".join(contents))
    