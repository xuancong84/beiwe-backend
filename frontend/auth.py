from datetime import datetime, timedelta
from flask import session, redirect, url_for, request
import functools

def is_logged_in():
    if 'expiry' in session and session['expiry'] > datetime.now():
        return 'admin_uuid' in session
    logout_loggedin_admin()

def logout_loggedin_admin():
    if "admin_uuid" in session: del session['admin_uuid']
    if "expiry" in session: del session['expiry']

def login_admin():
    #TODO: we probably don't need an admin uuid... we might?
    session['admin_uuid'] = "1234567890"
    session['expiry'] = datetime.now() + timedelta(hours=6)

#
def authenticated(f):
    """Decorator for functions (pages) that require a login.
       Redirects to index if not authenticated"""
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if is_logged_in(): return f(*args, **kwargs)
        return redirect("/")
    return wrapped
