from libs.user_db import DatabaseObject, DatabaseCollection, REQUIRED, ID_KEY

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
            return User.exists( device_id=device_id )
        return None
    

#the thing I use to access the entire table
class Users( DatabaseCollection ):
    OBJTYPE = User
    
"""
User.retrieve(id) #this is how you retrieve a user
User.create(id) #thjis is how you create a new user
Users() #this gets you all your users
"""
