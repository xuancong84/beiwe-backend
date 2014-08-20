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

# Decorator for functions (pages) that require a login
def gen_decorator(test, default_page):
    def auth_decorator(page=default_page, **url_args):
        def decorator(f):
            @functools.wraps(f)
            def wrapped(*args, **kwargs):
                if test(): return f(*args, **kwargs)
                return redirect(url_for(page, redirect=request.path, **url_args))
            return wrapped
        return decorator
    return auth_decorator

authenticated = gen_decorator(lambda: is_logged_in(), 'main')
