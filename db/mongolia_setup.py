import os
from mongolia import (connect_to_database, authenticate_connection, ID_KEY,
    REQUIRED, UPDATE, CHILD_TEMPLATE, DatabaseObject, DatabaseCollection,
    set_defaults_handling, set_type_checking, AlertLevel)

from mongolia.errors import MalformedObjectError, DatabaseConflictError
from config.security import MONGO_USERNAME, MONGO_PASSWORD

# We are specifying the default database, see the mongolia documentation if you
# use a non-default configuration.

connect_to_database(host=os.getenv("MONGO_HOST", "localhost"), port=int(os.getenv("MONGO_PORT", "27017")))
authenticate_connection(os.getenv("MONGO_USERNAME", MONGO_USERNAME), os.getenv("MONGO_PASSWORD", MONGO_PASSWORD), db=os.getenv("MONGO_DB", "beiwe"))
set_defaults_handling(AlertLevel.error)
set_type_checking(AlertLevel.error)
