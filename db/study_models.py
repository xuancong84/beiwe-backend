from db.mongolia_setup import DatabaseObject, DatabaseCollection, REQUIRED #, ID_KEY

"""TODO: New db table named Studies containing studies.
     Study name
     reference to administrators allowed to administer this study
     references to surveys in the study in the Surveys table(?)
     settings for survey (as json? maybe we want another table) """

class Study( DatabaseObject ):
    DEFAULTS = { "name": REQUIRED,
                 "admins": [],          #admins for the study.
                 "super_admins":[],     #admins that can add admins.
                 "surveys": [],         #the surveys pushed in this study.
                 "settings": REQUIRED   #the device settings for the study.
                 }
    
    #def add_survey(self, content, timings, survey_type):
    def add_survey(self, survey):
        self["surveys"].append(survey._id)
        

class Studies( DatabaseCollection ):
    """ The Studies database."""
    OBJTYPE = Study
    
################################################################################
   
class DeviceSettings( DatabaseObject ):
    """ The DeviceSettings database contains the structure that defines
        settings pushed to devices of users in of a study."""
    DEFAULTS = {}
    #TODO: fill this with settings...
    
#TODO: this database collection needs a better name.
class StudyDeviceSettings( DatabaseCollection ):
    OBJTYPE = DeviceSettings
    
################################################################################
"""TODO: new db table Surveys.
    fields: reference to a study,
    type of survey (audio or regular),
    content of survey (in json)
    timings for survey (as json) (daily, weekly, what day, what hour) 
    """
    
class Survey( DatabaseCollection ):
    DEFAULTS = {'content': REQUIRED,
                "timings": REQUIRED,
                "survey_type": REQUIRED,
                #TODO: do we need the following?
#                 "other_settings": REQUIRED
               }
    #TODO: define the valid types of survey
    """TODO: define a valid date-time schema
        list: days of week, starting on a sunday? (check implementation on android)
            of integers, in android we check day of the week and set that alarm.
            
        """
    #TODO: determine exactly what data goes into a survey (I think it is already
    # a json string), and dump it in.  implement the appropriate create method.
    
class Surveys(DatabaseCollection):
    OBJTYPE = Survey
    