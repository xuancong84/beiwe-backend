from libs.user_db import DatabaseObject, DatabaseCollection, REQUIRED, ID_KEY

class User( DatabaseObject ):
    #internal table name
    PATH = "users"
    
    #defaults are column names.  a dictionary containing key: sql_flag-thing and type
    DEFAULTS = { "client_id": REQUIRED, "password": None, 'device_id': None }
    
    @staticmethod
    def retrieve( some_client_id ):
        # if I want
        if User.exists( client_id=some_client_id ):
            return User( client_id=some_client_id )
        return None
    
    @classmethod
    def create(cls, some_client_id):
        #if I add new columns
        new_client = {'client_id': some_client_id, "password":None, 'device_id': None }
        return super(User, cls).create(new_client)
    
    @classmethod
    def remove(cls):
        #TODO: implement
        pass


#the thing I use to access the entire table
class Users( DatabaseCollection ):
    OBJTYPE = User
    
"""
User.retrieve(id) #this is how you reetrievee a user
User.create(id) #thjis is how you create an ew user
Users() #this gets you all your users
"""
