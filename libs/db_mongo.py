from mongolia import (connect_to_database, authenticate_connection, ID_KEY,
    REQUIRED, UPDATE, CHILD_TEMPLATE, DatabaseObject, DatabaseCollection)

from mongolia.errors import MalformedObjectError, DatabaseConflictError
from data.passwords import MONGO_USERNAME, MONGO_PASSWORD

#needs arguments

# we are specifying the default database

connect_to_database()
authenticate_connection(MONGO_USERNAME, MONGO_PASSWORD)
