from flask import request
from libs.db_models import User
import functools


# def authenticated(f):
#     print "this line was printed inside the decorator, type 1."
#     """Decorator for functions (pages) that require a user to provide identification.
#        Returns 403 (forbidden) if the identifying info (usernames, passwords
#        device IDs are invalid."""
#     @functools.wraps(f)
#     def wrapped(*args, **kwargs):
#         is_this_user_valid = check_identifiers( request.values['patient_id'],
#                                                 request.values['device_id'],
#                                                 request.values['password'] )
#
#         if is_this_user_valid: return f(*args, **kwargs)
#         return 403
#     return wrapped
#
# def check_identifiers( patient_id, device_id, password ):
#     """Check if user exists, check if the provided passwords match"""
#     if not User.exists(patient_id): return False
#
#     user = User( patient_id )
#
#     if not user.validate_password( password ): return False
#     if not user['device_id'] == device_id: return False
#
#     return True


def authenticated(f):
    print "this line was printed inside the decorator, type 2."
    """Decorator for functions (pages) that require a user to provide identification.
       Returns 403 (forbidden) if the identifying info (usernames, passwords
       device IDs are invalid."""
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        is_this_user_valid = check_identifiers( *args, **kwargs )

        if is_this_user_valid: return f(*args, **kwargs)
        return 403
    return wrapped


def check_identifiers( *args, **kwargs ):
    """Check if user exists, check if the provided passwords match"""
#     patient_id, device_id, password
    patientt_id = request.values['patient_id'],
    device_id = request.values['device_id'],
    password = request.values['password']

    if not User.exists(patient_id): return False

    user = User( patient_id )

    if not user.validate_password( password ): return False
    if not user['device_id'] == device_id: return False

    return True
