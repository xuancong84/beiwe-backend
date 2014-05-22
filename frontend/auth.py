from flask import session
from datetime import datetime, timedelta


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

