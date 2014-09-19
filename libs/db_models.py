from libs.db_mongo import DatabaseObject, DatabaseCollection, REQUIRED, ID_KEY
from hashlib import pbkdf2_hmac
from data.passwords import SALT

class User( DatabaseObject ):
    #internal table name
    PATH = "database.users"
    
    # Column Name:Default Value.  Use REQUIRED to indicate a non-nullable value.
    # We are using the patient's assigned ID as a unique Id.
    #TODO: Eli. Check with Kevin/Ben that this uniqueness is enforced.
    DEFAULTS = { "password": None, 'device_id': None }
    
    @classmethod
    def create(cls, patient_id):
        new_client = {ID_KEY: patient_id, "password":None, 'device_id':None }
        return super(User, cls).create(new_client)
    
    # Use this for reference, it is a modified retrieve method.
    # @staticmethod
    # def retrieve( some_client_id ):
    #    if User.exists( client_id=some_client_id ):
    #        return User( client_id=some_client_id )
    #    return None

    @classmethod
    def by_device_id(cls, device_id):
        if User.exists( device_id=device_id ):
            return User( device_id=device_id )
        return None
    

#the thing I use to access the entire table
class Users( DatabaseCollection ):
    OBJTYPE = User
    
"""
User.retrieve(id) #this is how you retrieve a user
User.create(id) #thjis is how you create a new user
Users() #this gets you all your users
"""



# pbkdf2_hmac is a hashing function for key derivation.  (there is apparently
# a faster implementation in somewhere in OpenSSL, from OpenSSL import something)
# We hash with the salt provided in passwords.py, plus the (unique) user name
# in order to handle the case of different users with the same password.
# Hash 100,000+ times, as recommended by the Python Docs for hashlib.
def password_hash (password, username):
    return pbkdf2_hmac('sha256', password, SALT + username, 125295)


class Admin( DatabaseObject ):
    PATH = "database.admins"
    
    DEFAULTS = { "password":REQUIRED }
    
    @classmethod
    def create(cls, username, password):
        new_admin = {ID_KEY :username,
                    password: password_hash(password) }
        return super(Admin, cls).create(new_admin)
    
    @classmethod
    # Look for password match anywhere, then check if the usernames match.
    # We are not handling hash collisions.  The birthday paradox dictates
    # that we must have 2^(n/2) hashes before we are "likely" to have a collision,
    # and SHA-256 has 256 bits, so we need 2^128 hash events. At a rate of about
    # 0.5 seconds per password_hash() function that would take 10^31 years.
    # I think we are fine.
    def check_password(cls, username, password):
        password = password_hash( password )
        if not Admin.exists( password=password ):
            return False
        some_admin = Admin( password=password )
        if some_admin[ID_KEY] == username:
            return True
        return False
    
class Admins( DatabaseCollection ):
    OBJTYPE = Admin