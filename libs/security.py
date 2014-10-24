from data.passwords import MONGO_PASSWORD, MONGO_USERNAME, FLASK_SECRET_KEY
from data.constants import ITERATIONS
from pbkdf2 import PBKDF2
from os import urandom
import hashlib
import re

class DatabaseIsDownError(Exception): pass


# set the secret key for the application
def set_secret_key(app):
    """Flask secret key"""
    app.secret_key = FLASK_SECRET_KEY


def pymongo():
    import pymongo
    try:
        conn = pymongo.Connection()
    except (pymongo.errors.AutoReconnect, pymongo.errors.ConnectionFailure):
        raise DatabaseIsDownError("No mongod process is running.")
    conn.admin.authenticate(MONGO_USERNAME, MONGO_PASSWORD)
    return conn


################################################################################
################################## HASHING #####################################
################################################################################

# Hashing note: Mongo does not like strings with arbitrary binary data, so we
# store passwords using base64 encoding.

# TODO: Eli. Profile and make sure this is a good number of ITERATIONS
# pbkdf2 is a hashing function for key derivation.

def _encode_base64(data):
    """ Creates a base64 representation of an input string without padding or lines."""
    return data.encode("base64").replace("\n", "")

# def _decode_base64(data):
#     return data.decode("base64")


def device_hash( data ):
    """ Hashes an input string using the sha256 hash.
        Used with the android device identifier, mirrors android behavior.
        Anticipates an unencoded string, returns a stripped base64 string."""
    sha256 = hashlib.sha256()
    sha256.update(data)
    return _encode_base64( sha256.digest() )

################################################################################

def generate_hash_and_salt( password ):
    """ Generates a hash and salt that will match for a given input string.
        Input is anticipated to be any arbitrary string."""
    salt = _encode_base64( urandom(16) )
    password_hashed =  _encode_base64( PBKDF2(password, salt, iterations=ITERATIONS).read(32) )
    return (password_hashed, salt )


def compare_password( proposed_password, salt, real_password_hash ):
    """ Compares a proposed password with a salt and a real password, returns
        True if the hash results are identical.
        Expects the proposed password to be a base64 encoded string.
        Expects the real password to be a base64 encoded string. """
    proposed_hash = _encode_base64( PBKDF2( proposed_password, salt, iterations=ITERATIONS).read(32) )
    if  proposed_hash == real_password_hash :
        return True
    return False


def generate_random_password_and_salt():
    """ Generates a random password, and an associated hash and salt.
        The password is an uppercase alphanumeric string,
        the password hash and salt are base64 encoded strings. """
    password = generate_upper_case_alphanumeric_string()
    password_hash, salt = generate_hash_and_salt( password )
    return password, password_hash, salt


################################################################################
############################### Random #########################################
################################################################################

def generate_upper_case_alphanumeric_string():
    #generates an alphanumeric uppercase letter string 10 characters long.
    random_string = hashlib.md5( urandom(16) ).digest().encode('base64')
    return re.sub(r'[^A-Z0-9]', "", random_string)[:10]
