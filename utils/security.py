class DatabaseIsDownError(Exception): pass

# set the secret key for the application
def set_secret_key(app):
    """Flask secret key"""
    app.secret_key = '\xb7BdD<\x11\x80\xe9\x01\xdb\x19\xba\xff\xa5&\xef8\x13\xfb\xa8vA\x190'

MONGO_USERNAME = "scrubs"
MONGO_PASSWORD = "scrubs_very_secure_password"

def pymongo():
    import pymongo
    try:
        conn = pymongo.Connection()
    except (pymongo.errors.AutoReconnect, pymongo.errors.ConnectionFailure):
        raise DatabaseIsDownError("No mongod process is running.")
    conn.admin.authenticate(MONGO_USERNAME, MONGO_PASSWORD)
    return conn
