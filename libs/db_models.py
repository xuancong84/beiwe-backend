from libs.db_mongo import DatabaseObject, DatabaseCollection, REQUIRED, ID_KEY
from libs.security import generate_hash_and_salt, compare_hashes

class User( DatabaseObject ):
    
    PATH = "database.users"
    
    # Column Name:Default Value.  Use REQUIRED to indicate a non-nullable value.
    # We are using the patient's assigned ID as a unique Id.
    DEFAULTS = { "password":None, 'device_id':None, 'salt':None }
    
    @classmethod
    #TODO: Add to create User a check to see if a user under that ID already exists on s3
    def create(cls, patient_id):
        new_client = {ID_KEY: patient_id, "password":None, 'device_id':None, "salt":None }
        return super(User, cls).create(new_client)
    
    
    @classmethod
    def by_device_id(cls, device_id):
        return User( device_id=device_id )
    
    
    @classmethod
    def check_password(self, patient_id, compare_me ):
        if not User.exists( patient_id ):
            return False
        user = User( patient_id )
        return user.validate_password( compare_me )
    
    
    #provide this instance with a password, it returns true if it matches
    def validate_password(self, compare_me):
        return compare_hashes( compare_me, self['salt'], self['password'] )
    
    
    def set_password(self, password):
        password, salt  = generate_hash_and_salt( password )
        self['password'] = password
        self['salt'] = salt
        self.save()


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
    
    DEFAULTS = { "password":REQUIRED, 'salt':REQUIRED }
    
    @classmethod
    def create(cls, username, password):
        password, salt = generate_hash_and_salt( password )
        new_admin = {ID_KEY :username, 'password':password, 'salt':salt }
        return super(Admin, cls).create(new_admin)
    
    @classmethod
    # Look for password match anywhere, then check if the usernames match.
    # We are not handling hash collisions.  The birthday paradox dictates
    # that we must have 2^(n/2) hashes before we are "likely" to have a collision,
    # and SHA-256 has 256 bits, so we need 2^128 hash events. At a rate of about
    # 0.5 seconds per password_hash() function that would take 10^31 years.
    # I think we are fine.
    def check_password(cls, username, compare_me ):
        if not Admin.exists( username ):
            return False
        admin = Admin( username )
        return admin.validate_password( compare_me )
    
    
    #provide this instance with a password, it returns true if it matches
    def validate_password(self, compare_me):
        return compare_hashes( compare_me, self['salt'], self['password'] )
    
    
class Admins( DatabaseCollection ):
    OBJTYPE = Admin