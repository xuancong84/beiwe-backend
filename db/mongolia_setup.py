import os
from mongolia import (connect_to_database, authenticate_connection, ID_KEY,
    REQUIRED, UPDATE, CHILD_TEMPLATE, DatabaseObject, DatabaseCollection,
    set_defaults_handling, set_type_checking, AlertLevel, mongo_connection)

from mongolia.errors import MalformedObjectError, DatabaseConflictError
from config.secure_settings import MONGO_USERNAME, MONGO_PASSWORD, MONGO_PORT, MONGO_IP

connect_to_database(host=MONGO_IP, port=MONGO_PORT)
authenticate_connection(MONGO_USERNAME, MONGO_PASSWORD)
set_defaults_handling(AlertLevel.error)
set_type_checking(AlertLevel.error)

db_connection = mongo_connection.CONNECTION.get_connection()['beiwe']
