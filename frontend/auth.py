from flask import session
from datetime import datetime, timedelta
from flask import session, redirect, url_for, request
import functools


def is_logged_in():
    if 'expiry' in session and session['expiry'] > datetime.now():
        return 'phonenum' in session
    del_loggedin_phonenum()

def del_loggedin_phonenum():
    if "phonenum" in session: del session['phonenum']
    if "display_phonenum" in session: del session["display_phonenum"]
    if "expiry" in session: del session['expiry']

def login_user():
    session['phonenum'] = "+11234567890"
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

