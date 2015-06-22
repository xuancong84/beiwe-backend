from datetime import datetime, timedelta
from flask import session, redirect
from db.user_models import Admin, Admins
from libs.security import generate_easy_alphanumeric_string
import functools

#TODO: I think this comment is incorrect:
#note: admin passwords cannot currently be changed.

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
    def wrapped(*args, **kwargs):
        if is_logged_in(): return some_function(*args, **kwargs)
        return redirect("/")
    return wrapped


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
########################## System Administrator ################################
################################################################################

# TODO: test sysadmin wrapper
def authenticate_sysadmin(some_function):
    """Decorator for functions (pages) that require a login.
       Redirects to index if not authenticate_admin"""
    @functools.wraps(some_function)
    def wrapped(*args, **kwargs):
        admin = Admins(session['admin_username'])
        if not admin["system_admin"]:
            #TODO: we need a permission denied page.
            return redirect("/")
    return wrapped
