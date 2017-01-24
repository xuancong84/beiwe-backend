import traceback, smtplib
from datetime import datetime
from config.security import E500_EMAIL_ADDRESS, SYSADMIN_EMAILS, OTHER_EMAIL_ADDRESS


def log_and_email_error(e, log_message=None, emails=SYSADMIN_EMAILS ):
    """ Prints in the server logs (defaults to Apache if not specified),
        does NOT stop execution.
        Note the error.message value is actually the subject line of the email,
        the "log_message" variable is a passed in as the "message" variable
        into the log_error function and appears as part of the email and log statement. """
    try:
        subject = "Beiwe Error: %s" % e.message
        message = log_error(e, log_message, reraise=True)
        _send_email(E500_EMAIL_ADDRESS, SYSADMIN_EMAILS, message, subject)
        
    except Exception:
        print("\n!!!! ERROR IN log_and_email_error !!!!")


def email_bundled_error(e, subject, emails=SYSADMIN_EMAILS):
    _send_email(OTHER_EMAIL_ADDRESS, SYSADMIN_EMAILS, e.__repr__(), subject)
    

def log_error(e, message=None, reraise=False):
    """ Prints an error to the apache log.
        "message" is a customizable that will be printed in the log.
        Reraise is dangerous, only set to true if you understand why it is."""
    try:
        error_message = "===================\n"
        error_message += datetime.utcnow().isoformat() + "\n"
        if message is not None: error_message += message + "\n"
        error_message += "ERROR:" + str(e.__repr__()) + "\n"
        error_message += traceback.format_exc() + "\n"
        error_message += "===================\n"
        print(error_message)
        return error_message
    except Exception:
        print("\n!!!! ERROR IN log_error !!!!")
        if reraise:
            raise


def email_system_administrators(message, subject, source_email=OTHER_EMAIL_ADDRESS):
    """ Sends an email to the system administrators. """
    error_email = 'Subject: %s\n\n%s' % (subject, message)
    try:
        _send_email(source_email, SYSADMIN_EMAILS, message, subject)
    except Exception as e:
        # todo: low priority. this reraise parameter may be incorrect.
        log_error(e, message="sysadmin email failed", reraise=False)


def _send_email(source_email_address, destination_email_addresses, message, subject):
    email_server = smtplib.SMTP("localhost")
    try:
        email_server.sendmail( source_email_address,
                               destination_email_addresses,
                               'Subject: %s\n\n%s' % (subject, message) )
    except Exception:
        raise
    finally:
        email_server.quit()