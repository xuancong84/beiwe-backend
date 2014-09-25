from flask import request
from libs.db_models import User
import functools


def authenticated(some_function):
    print "this line was printed inside the decorator, type 2."
    """Decorator for functions (pages) that require a user to provide identification.
       Returns 403 (forbidden) if the identifying info (usernames, passwords
       device IDs are invalid."""
    @functools.wraps(some_function)
    def wrapped(*args, **kwargs):
        is_this_user_valid = check_identifiers( *args, **kwargs )
#        return some_function(*args, **kwargs)
        if is_this_user_valid: return some_function(*args, **kwargs)
        #return 403
    return wrapped


def check_identifiers( *args, **kwargs ):
#    return True
    print "something"
    """Check if user exists, check if the provided passwords match"""
#     patient_id, device_id, password
    patient_id = request.values['patient_id'],
    print "patient id: ", patient_id, ' -- type: ', type(patient_id)
    device_id = request.values['device_id'],
    print "device id: ", device_id, ' -- type: ', type(device_id)
    password = request.values['password']
    print 'password: ', password, ' -- type: ', type(password)

    if not User.exists(patient_id):
        print "user id was false"
        return False
    print 'user id was true'
    user = User( patient_id )
    
    if not user.validate_password( password ):
        print 'password was false'
        return False
    print 'password was true'
    
    if not user['device_id'] == device_id:
        print "device id was false"
        return False
    print 'device id was true'
    print 'RETURNING TRUE'
    
    return True
