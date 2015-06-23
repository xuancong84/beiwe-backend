import functools
from datetime import datetime, timedelta
from flask import session, redirect
from db.user_models import Admin, Admins
from libs.security import generate_easy_alphanumeric_string
from db.study_models import Studies

################################################################################
############################ Existence Modifiers ###############################
################################################################################

def create_admin(username, password):
    Admin.create(username, password)

def remove_admin(username):
    Admin(username).remove()

################################################################################
############################ Website Functions #################################
################################################################################


def authenticate_admin(some_function):
    """Decorator for functions (pages) that require a login.
       Redirects to index if not authenticate_admin"""
    @functools.wraps(some_function)
    def authenticate_and_call(*args, **kwargs):
        if is_logged_in(): return some_function(*args, **kwargs)
        return redirect("/")
    return authenticate_and_call


def log_in_admin(username):
    session['admin_uuid'] = generate_easy_alphanumeric_string()
    session['expiry'] = datetime.now() + timedelta(hours=6)
    session['admin_username'] = username


def logout_loggedin_admin():
    if "admin_uuid" in session: del session['admin_uuid']
    if "expiry" in session: del session['expiry']


def is_logged_in():
    if 'expiry' in session and session['expiry'] > datetime.now():
        return 'admin_uuid' in session
    logout_loggedin_admin()

################################################################################
########################## Study Editing Privileges ############################
################################################################################

class ArgumentMissingException(Exception): pass

#TODO: test survey editing wrapper.
#this is untested fake code and requires a proper understanding of intercepting kwargs to implement
def authenticate_editing(some_function):
    """ This authentication decorator is for checking whether the user has
        permissions for the study they are accessing.
        This decorator requires that a specific keyword argument be provided to
        the function, the "survey_id" keyword. """
    @functools.wraps(some_function)
    def authenticate_and_call(*args, **kwargs):
        if "survey_id" not in kwargs:
            raise ArgumentMissingException("missing keyword argument 'survey_id'")
        study_name = kwargs["survey_id"]
        admin_name = session["admin_username"]
        #mongo's equality test evaluates for both = and 'in' for database elements containing json lists.
        #TODO: should we actually expose the database keys... probably not.  ask zags about indexing in mongolia (not that it is really important...)
        survey = Studies(_id=study_name, admins=admin_name)
        if not survey:
            #todo: permission denied page
            return redirect("/")
    return authenticate_and_call


################################################################################
########################## System Administrator ################################
################################################################################

# TODO: test sysadmin wrapper
def authenticate_sysadmin(some_function):
    @functools.wraps(some_function)
    def authenticate_and_call(*args, **kwargs):
        admin = Admins(session['admin_username'])
        if not admin["system_admin"]:
            #TODO: permission denied page.
            return redirect("/")
    return authenticate_and_call

