from db.mongolia_setup import DatabaseObject, DatabaseCollection, REQUIRED #, ID_KEY
from db.user_models import Users


class Study( DatabaseObject ):
    DEFAULTS = { "name": REQUIRED,
                 "admins": [],          #admins for the study.
                 "super_admins":[],     #admins that can add admins.
                 "surveys": [],         #the surveys pushed in this study.
                 "settings": REQUIRED,  #the device settings for the study.
                 "devices": [],
                 "encryption_key": REQUIRED
                 }
    
    #def add_survey(self, content, timings, survey_type):
    def add_survey(self, survey):
        self["surveys"].append(survey._id)
    
    @classmethod
    def get_studies_for_admin(admin_id):
        return [Studies(study_id) for study_id in Studies(admins=admin_id)]
    
    #TODO: test that this works and is not a cyclic import (it shouldn't be...)
    def get_users_in_study(self):
        [ Users(device_id) for device_id in self.devices ]
    
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
    timings for survey (as json) (what days, what hour) 
    """
    #TODO: we need a canonical list of survey types. (probably voice, text)
class Survey( DatabaseCollection ):
    DEFAULTS = {"content": REQUIRED,
                "timings": REQUIRED,
                "survey_type": REQUIRED,
                #TODO: do we need the following per-survey settings?
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
    