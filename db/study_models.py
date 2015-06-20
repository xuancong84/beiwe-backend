from db.mongolia_setup import DatabaseObject, DatabaseCollection, REQUIRED, ID_KEY

"""TODO: New db table named Studies containing studies.
     Study name
     reference to administrators allowed to administer this study
     references to surveys in the study in the Surveys table(?)
     settings for survey (as json? maybe we want another table) """

class Study( DatabaseObject ):
    #TODO: implement pages for admins, superadmins
    DEFAULTS = { "name": REQUIRED,
                 "admins": [],          #admins for the study.
                 "super_admins":[],     #admins that can add admins.
                 "surveys": [],         #the surveys pushed in this study.
                 "settings": REQUIRED   #the device settings for the study.
                 }

class Studies( DatabaseCollection ):
    """ The Studies database."""
    OBJTYPE = Study
    
################################################################################
   
class DeviceSettings( DatabaseObject ):
    """ The DeviceSettings database contains the structure that defines
        settings pushed to devices of users in of a study."""
    DEFAULTS = {}
    #TODO: fill this with settings.
    
#TODO: this database collection needs a better name.
class StudyDeviceSettings( DatabaseCollection ):
    OBJTYPE = DeviceSettings
    
################################################################################
"""TODO: new db table Surveys.
    fields: reference to a study,
    type of survey (audio or regular),
    content of survey (in json),
    timings for survey (as json) (daily, weekly, what day, what hour) 
    """
    
class Survey( DatabaseCollection ):
    DEFAULTS = {'questions': REQUIRED,
                "timings": REQUIRED,
                "type": REQUIRED
                }
    