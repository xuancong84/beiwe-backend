from mongolia import (connect_to_database, authenticate_connection, ID_KEY,
    REQUIRED, UPDATE, CHILD_TEMPLATE, DatabaseObject, DatabaseCollection)

from mongolia.errors import MalformedObjectError, DatabaseConflictError
from libs.security import MONGO_USERNAME, MONGO_PASSWORD

connect_to_database()
authenticate_connection(MONGO_USERNAME, MONGO_PASSWORD)
