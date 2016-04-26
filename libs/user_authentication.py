import functools
from flask import request, abort
from werkzeug.datastructures import MultiDict
from db.user_models import User
from config.constants import ANDROID_API, IOS_API

def authenticate_user(some_function):
    """Decorator for functions (pages) that require a user to provide identification.
       Returns 403 (forbidden) or 401 (depending on beiwei-api-version) if the identifying info (usernames, passwords
       device IDs are invalid.

       In any funcion wrapped with this decorator provide a parameter named
       "patient_id" (with the user's id), a parameter named "password" with an SHA256
       hashed instance of the user's password, a parameter named "device_id" with a
       unique identifier derived from that device. """
    @functools.wraps(some_function)
    def authenticate_and_call(*args, **kwargs):
        check_for_basic_auth( *args, **kwargs );
        is_this_user_valid = validate_post( *args, **kwargs )
        if is_this_user_valid:
            return some_function(*args, **kwargs)
        return abort(401 if (kwargs["OS_API"] == IOS_API) else 403)
    return authenticate_and_call


def validate_post( *args, **kwargs ):
    """Check if user exists, check if the provided passwords match, and if the
    device id matches."""
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


def authenticate_user_registration(some_function):
    """Decorator for functions (pages) that require a user to provide identification.
       Returns 403 (forbidden)  or 401 (depending on beiwei-api-version) if the identifying info (usernames, passwords
       device IDs are invalid.

       In any funcion wrapped with this decorator provide a parameter named
       "patient_id" (with the user's id) and a parameter named "password" with an
       SHA256 hashed instance of the user's password. """
    @functools.wraps(some_function)
    def authenticate_and_call(*args, **kwargs):
        check_for_basic_auth( *args, **kwargs );
        is_this_user_valid = validate_registration( *args, **kwargs )
        if is_this_user_valid: return some_function(*args, **kwargs)
        return abort(401 if (kwargs["OS_API"] == IOS_API) else 403)
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

#TODO: Keary.  Please document the effect of this function. (I gather that it sets the
#values that you stick into the iOS http requests.)
def check_for_basic_auth( *args, **kwargs ):
    """Check if user exists, check if the provided passwords match"""
    auth = request.authorization
    if not auth:
        return
    username_parts = auth.username.split('@')
    if len(username_parts) == 2:
        replace_dict = MultiDict(request.values.to_dict());
        if "patient_id" not in replace_dict:
            replace_dict['patient_id'] = username_parts[0]
        if "device_id" not in replace_dict:
            replace_dict['device_id'] = username_parts[1]
        if "password" not in replace_dict:
            replace_dict['password'] = auth.password
        request.values = replace_dict
    return
