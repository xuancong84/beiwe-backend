'''
Created on Sep 12, 2014

@author: Eli
'''

from s3 import s3_retrieve, s3_upload_handler_string

""" The Users file is a simple text file containing the master list of valid,
registerable user_ids."""


USER_IDS = set(s3_retrieve("users").splitlines())

#TODO: Eli. ask Ben if this construction makes any sense at all...
def get_users_file():
    USER_IDS = set(s3_retrieve("users").splitlines())
    return USER_IDS


def add_users( add_user_ids ):
    """ Takes a comma separated string of user ids and adds them to
        the valid users list.  Removes all whitespace"""
    add_user_ids = add_user_ids.replace( str.whitespace, "" )
    
    add_user_ids = set( add_user_ids.split(',') )
    
    USER_IDS.update( add_user_ids )
    return update_users_file()


def remove_user( remove_user_ids ):
    
    """ Takes a comma separated string of user ids and removes them from
    the valid users list.  Removes whitespace before checking.  Returns
    a set of entries that did not match, or, if S3 had issues, simply returns false"""
    #if remove_user_ids is a comma separated list, turn it into a set of those user ids
    remove_user_ids = remove_user_ids.replace( str.whitespace, "" )
    remove_user_ids = set( remove_user_ids.split(',').strip_whitespace() )
    
    unresolved_ids = USER_IDS.intersection( remove_user_ids )
    
    USER_IDS.symmetric_difference_update( remove_user_ids )
    
    if update_users_file():
        return remove_user_ids.difference(unresolved_ids)
    else: return False


#TODO: Eli. ask Kevin about logging this kind of error.  (also just look into logging)
def update_users_file():
    users_update = ""
    for user_id in USER_IDS:
        users_update += user_id + "\n"
    try: s3_upload_handler_string("users", users_update)
    except Exception as e:
        print e.message
        return False
    return True
