import functools
from flask import request, abort
from db.user_models import User
from db.study_models import Study


def authenticate_user(some_function):
    """Decorator for functions (pages) that require a user to provide identification.
       Returns 403 (forbidden) if the identifying info (usernames, passwords
       device IDs are invalid."""
    @functools.wraps(some_function)
    def authenticate_and_call(*args, **kwargs):
        is_this_user_valid = validate_post( *args, **kwargs )
        if is_this_user_valid:
            return some_function(*args, **kwargs)
        return abort(403)
    return authenticate_and_call


def validate_post( *args, **kwargs ):
    """Check if user exists, check if the provided passwords match."""
    #print "user info:  ", request.values.items()
    #print "file info:  ", request.files.items()
    if ("patient_id" not in request.values
        or "password" not in request.values
        or "device_id" not in request.values):
        return False
    if not User.exists(request.values['patient_id']): return False
    user = User( request.values['patient_id'] )
    if not user.validate_password( request.values['password'] ): return False
    if not user['device_id'] == request.values['device_id']: return False
    return True


#FIXME: Eli. Ensure that user registration authentication are still correct for new user registration.
def authenticate_user_registration(some_function):
    """Decorator for functions (pages) that require a user to provide identification.
       Returns 403 (forbidden) if the identifying info (usernames, passwords
       device IDs are invalid."""
    @functools.wraps(some_function)
    def authenticate_and_call(*args, **kwargs):
        is_this_user_valid = validate_registration( *args, **kwargs )
        if is_this_user_valid: return some_function(*args, **kwargs)
        return abort(403)
    return authenticate_and_call


def validate_registration( *args, **kwargs ):
    """Check if user exists, check if the provided passwords match"""
    if ("patient_id" not in request.values or "password" not in request.values
        or "device_id" not in request.values):
        return False
    if not User.exists(request.values['patient_id']): return False
    user = User( request.values['patient_id'] )
    if not user.validate_password( request.values['password'] ): return False
    return True

