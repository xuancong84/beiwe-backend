import functools
from datetime import datetime, timedelta
from flask import session, redirect
from db.user_models import Admin, Admins
from libs.security import generate_easy_alphanumeric_string
from db.study_models import Studies
from bson.objectid import ObjectId

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

def authenticate_admin_login(some_function):
    """Decorator for functions (pages) that require a login.
       Redirects to index if not authenticate_admin_login"""
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

#TODO: Josh/Alvin. permission denied page
#TODO: Josh/Alvin. (low priority) we need a survey does not exist error page.
def authenticate_admin_study_access(some_function):
    """ This authentication decorator checks whether the user has permission to
        to access the study/survey they are accessing.
        This decorator requires the specific keywords "survey_id" or "study_id"
        be provided as keywords to the function, and will error if one is not.
        The pattern is for a url with <string:survey/study_id> to pass in this
        value. """
    @functools.wraps(some_function)
    def authenticate_and_call(*args, **kwargs):
        if not is_logged_in(): #check for regular login requirement
            print 2
            return redirect("/")
        admin_name = session["admin_username"]
        #check proper syntax usage.
        if "survey_id" not in kwargs and "study_id" not in kwargs:
            raise ArgumentMissingException()
        #We want the survey_id check to execute first if both args are supplied. 
        if "survey_id" in kwargs:
            print 3
            survey_id = ObjectId(kwargs["survey_id"])
            #mongo's equality test evaluates for both = and 'in' for database elements containing json lists.
            study = Studies(surveys=survey_id, admins=admin_name)
            if not study: #if the admin is not authorized for this survey, fail.
                print 'survey id invalid', survey_id
                return redirect("/")
        if "study_id" in kwargs:
            print 4
            study_id = ObjectId(kwargs['study_id'])
            study = Studies(_id=study_id, admins=admin_name)
            if not study: #if the admin is not authorized for this study, fail.
                print 'study id invalid', study_id
                return redirect("/")
        return some_function(*args, **kwargs)
    return authenticate_and_call

def get_admins_allowed_studies():
    """ Return a list of studies which the currently logged-in admin is autho-
    rized to view and edit """
    admin = Admin(session['admin_username'])
    return Studies(admins=admin._id)

def admin_is_system_admin():
    # TODO: Josh, find a more efficient way of checking this and "allowed_studies" than passing it to every render_template
    admin = Admin(session['admin_username'])
    return admin.system_admin


################################################################################
########################## System Administrator ################################
################################################################################

#TODO: Josh/Alvin. (low priority) we need a permission denied page.
def authenticate_system_admin(some_function):
#     print "\n\n doees this even run\n\n\n"
    @functools.wraps(some_function)
    def authenticate_and_call(*args, **kwargs):
        admin = Admin(session['admin_username'])
        if not admin["system_admin"]:
            return redirect("permission_denied.html")
        return some_function(*args, **kwargs)
    return authenticate_and_call

