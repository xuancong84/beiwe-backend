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

def generate_hash_and_salt ( password ):
    salt = urandom(16).encode('base64')
    return (PBKDF2(password, salt, iterations=ITERATIONS).read(32).encode("base64"),
            salt )


def compare_hashes( compare_me, salt, real_password_hash ):
    if PBKDF2( compare_me, salt, iterations=ITERATIONS).read(32) == real_password_hash.decode("base64"):
        return True
    return False


def generate_random_password_and_salt():
    password = generate_upper_case_alphanumeric_string()
    password_hash, salt = generate_hash_and_salt( password )
    return password, password_hash, salt

################################################################################
############################### Random #########################################
################################################################################

def generate_upper_case_alphanumeric_string():
    #generates an alphanumeric uppercase letter string 10 characters long.
    random_string = hashlib.md5( urandom(16) ).digest().encode("base64")
    return re.sub(r'[^A-Z0-9]', "", random_string)[:10]
