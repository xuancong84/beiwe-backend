from libs.db_mongo import DatabaseObject, DatabaseCollection, REQUIRED, ID_KEY
from libs.security import password_hash

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
    
    #TODO: Add to the create User a check to see if a user under that ID already exists on s3
    @classmethod
    def check_password(self, patient_id, password):
        password = password_hash( patient_id, password )
        if not User.exists( password=password ):
            return False
        some_user = User( password=password )
        if some_user[ID_KEY] == patient_id:
            return True
        return False
    
    @classmethod
    def set_password(cls, patient_id, password):
        if cls.exists(patient_id):
            Users( ID_KEY = patient_id )[0]['password'] = password
            
            

#the thing I use to access the entire table
class Users( DatabaseCollection ):
    OBJTYPE = User
    
"""
User.retrieve(id) #this is how you retrieve a user
User.create(id) #thjis is how you create a new user
Users() #this gets you all your users
"""


# TODO: implement initial user setup/device registration pin provided by an admin to a user.
# actually we should implement this by just setting a default password that the user has to type in on first run.

# TODO: add a randomly-generate new user id.  User only needs to type in a user ID on device registration.

# HOWTO: implement password reset
# on login screen: 1 regular enter password to log-in field, one forgot password button
# forgot password button: explains they need to call the study, and talk with someone.
# that someone will send them a reset code, which they type into the single field
# that you can enter from the forgot password screen.  On entering the reset pin
# sets the reset pin to be your new password.  You can then go and reset your password in
# the password reset screen.  Note that resetting a password requires a data connection.

# TODO: Dori.  The reset password activity inside of the app (the one that you
# can access when you are logged in on the device) requires an active internet connection.


class Admin( DatabaseObject ):
    PATH = "database.admins"
    
    DEFAULTS = { "password":REQUIRED }
    
    @classmethod
    def create(cls, username, password):
        new_admin = {ID_KEY :username,
                    password: password_hash( username, password ) }
        return super(Admin, cls).create(new_admin)
    
    @classmethod
    # Look for password match anywhere, then check if the usernames match.
    # We are not handling hash collisions.  The birthday paradox dictates
    # that we must have 2^(n/2) hashes before we are "likely" to have a collision,
    # and SHA-256 has 256 bits, so we need 2^128 hash events. At a rate of about
    # 0.5 seconds per password_hash() function that would take 10^31 years.
    # I think we are fine.
    def check_password(cls, username, password):
        password = password_hash( username, password )
        if not Admin.exists( password=password ):
            return False
        some_admin = Admin( password=password )
        if some_admin[ID_KEY] == username:
            return True
        return False
    
class Admins( DatabaseCollection ):
    OBJTYPE = Admin