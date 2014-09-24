from datetime import datetime, timedelta
from flask import session, redirect
from libs.db_models import Admin, Admins
import functools



def logout_loggedin_admin():
    if "admin_uuid" in session: del session['admin_uuid']
    if "expiry" in session: del session['expiry']


def login_admin():
    #TODO: Eli/Kevin. Currently only 1 admin user. Allow more than one admin user.
    session['admin_uuid'] = "12345678987654321" #111111111^2
    session['expiry'] = datetime.now() + timedelta(hours=6)


def validate_login_credentials(password, username):
    if password == "1" and username == "1":
        return True
    return False
    #TODO: Eli/Kevin make this a real thing.


def is_logged_in():
    if 'expiry' in session and session['expiry'] > datetime.now():
        return 'admin_uuid' in session
    logout_loggedin_admin()


def authenticated(f):
    """Decorator for functions (pages) that require a login.
       Redirects to index if not authenticated"""
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if is_logged_in(): return f(*args, **kwargs)
        return redirect("/")
    return wrapped


def create_admin(username, password):
    Admin.create(username, password)


def remove_admin(username):
    Admin(username).remove()