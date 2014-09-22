from data.passwords import MONGO_PASSWORD, MONGO_USERNAME, FLASK_SECRET_KEY
from pbkdf2 import PBKDF2
from data.passwords import SALT

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

# TODO: Eli. Profile and make sure this is a good number of iterations
# pbkdf2 is a hashing function for key derivation.
def password_hash ( username, password ):
    return PBKDF2(password, SALT, iterations=1000).read(32).encode("base64")
