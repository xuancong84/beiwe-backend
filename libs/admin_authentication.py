import functools
from datetime import datetime, timedelta
from flask import session, redirect
from db.user_models import Admin, Admins
from libs.security import generate_easy_alphanumeric_string
from db.study_models import Studies, Study
from bson.objectid import ObjectId
from werkzeug.exceptions import abort

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

#TODO: Low Priority. Josh/Alvin. permission denied page.
#TODO: Low Priority. Josh/Alvin.  we need a survey does not exist error page.
def authenticate_admin_study_access(some_function):
    """ This authentication decorator checks whether the user has permission to
        to access the study/survey they are accessing.
        This decorator requires the specific keywords "survey_id" or "study_id"
        be provided as keywords to the function, and will error if one is not.
        The pattern is for a url with <string:survey/study_id> to pass in this
        value.
        A system admin is always able to access a study or survey. """
    @functools.wraps(some_function)
    def authenticate_and_call(*args, **kwargs):
        if not is_logged_in(): #check for regular login requirement
            return redirect("/")
        admin_name = session["admin_username"]
        admin = Admin(admin_name)
        #check proper syntax usage.
        if "survey_id" not in kwargs and "study_id" not in kwargs:
            raise ArgumentMissingException()
        #We want the survey_id check to execute first if both args are supplied. 
        if "survey_id" in kwargs:
            #turn the survey_id into a bson ObjectId.
            survey_id = ObjectId(kwargs["survey_id"]) 
            kwargs['survey_id'] = survey_id
            #MongoDB checks both equality and contains when you pass it a value.
            study = Study(surveys=survey_id)
            if not study: #study does not exist.
                return abort(404)
            #check admin is allowed, allow system admins.
            if not admin.system_admin:
                if admin['_id'] not in study.admins:
                    return abort(403)
        if "study_id" in kwargs:
            study_id = ObjectId(kwargs['study_id'])
            kwargs['study_id'] = study_id
            study = Study(study_id)
            if not study:
                return abort(404)
            if not admin.system_admin:
                if admin['_id'] not in study.admins:
                    return abort(403)
        return some_function(*args, **kwargs)
    return authenticate_and_call

def get_admins_allowed_studies():
    """ Return a list of studies which the currently logged-in admin is autho-
    rized to view and edit """
    admin = Admin(session['admin_username'])
    return Studies(admins=admin._id)

def admin_is_system_admin():
    # TODO: Low Priority. Josh. find a more efficient way of checking this and "allowed_studies" than passing it to every render_template
    # talk with Eli about this, we can make a better solution.  maybe make a decorator?
    admin = Admin(session['admin_username'])
    return admin.system_admin

################################################################################
########################## System Administrator ################################
################################################################################

#TODO: Low priority. Josh/Alvin. we need a permission denied page.
def authenticate_system_admin(some_function):
    """ Authenticate system admin checks whether a user is a system admin before
    allowing access to pages marked with this decorator.  If a study_id variable
    is supplied as a keyword argument, the decoator will automatically grab the
    ObjectId in place of the string provided in a route.
    NOTE: if you are using this function along with the authenticate_admin_study_access
    decorator you must place this decorator below it, otherwise behavior is undefined
    and probably causes a 500 error inside the authenticate_admin_study_access decorator."""
    @functools.wraps(some_function)
    def authenticate_and_call(*args, **kwargs):
        if not is_logged_in(): #check for regular login requirement
            return redirect("/")
        admin = Admin(session['admin_username'])
        if not admin["system_admin"]:
            # TODO: Low Priority. Josh. redirect to a URL, not a template file
            return redirect("permission_denied.html")
        if 'study_id' in kwargs:
            study_id = kwargs['study_id']
            if not isinstance(study_id, ObjectId):#make an extra check in case
                study_id = ObjectId(study_id)     #authenticate_admin_study_access
                kwargs['study_id'] = study_id     #has already converted the id.
            if not Studies(_id=study_id):
                return redirect("/")
        return some_function(*args, **kwargs)
    return authenticate_and_call

