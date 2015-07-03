from db.mongolia_setup import DatabaseObject, DatabaseCollection, REQUIRED #, ID_KEY
from db.user_models import Users
from data.constants import SURVEY_TYPES

class Study( DatabaseObject ):
    DEFAULTS = { "name": REQUIRED,
                 "admins": [],          #admins for the study.
                 "super_admins":[],     #admins that can add admins.
                 "surveys": set(),      #the surveys pushed in this study.
                 "settings": REQUIRED,  #the device settings for the study.
                 "participants": [],
                 "encryption_key": REQUIRED }
    
    @classmethod
    def get_studies_for_admin(admin_id):
        return [Studies(study_id) for study_id in Studies(admins=admin_id)]
    
    def add_survey(self, survey):
        self["surveys"].append(survey._id)
    
    def remove_survey(self, survey_id):
#         if survey_id not in self['surveys']:
#             raise SurveyDoesNotExistError
        self["surveys"].remove()
    
    #TODO: Eli. test that this works and is not a cyclic import (it shouldn't be...)
    def get_participants_in_study(self):
        [ Users(participants) for participants in self.participants ]
    
    def get_surveys_for_study(self):
        return [Surveys(survey_id) for survey_id in self['surveys'] ]


class DeviceSettings( DatabaseObject ):
    """ The DeviceSettings database contains the structure that defines
        settings pushed to devices of users in of a study."""
    DEFAULTS = {}
    #TODO: Eli/Josh. fill this with all the toggles.


class Survey( DatabaseCollection ):
    DEFAULTS = {"content": REQUIRED,
                "timings": REQUIRED,
                "survey_type": REQUIRED }
    @classmethod
    #TODO: Eli. probably should have some kind of survey type check here
    def create_default_survey(cls, survey_type):
        if survey_type not in SURVEY_TYPES:
            raise SurveyTypeError("%s is not a valide survey type" % survey_type)
        survey = {'content:':"",
                  'timings': [False, False, False, False, False, False, False],
                  "survey_type": survey_type }
        cls.create(**survey)
        
    """TODO: Eli define a valid date-time schema
        list: days of week, starting on a sunday? (check implementation on android)
            of integers, in android we check day of the week and set that alarm.
            (check the app, I think sunday is 0 index)"""
    """TODO: Eli. determine exactly what data goes into a survey (I think it is already
        # a json string), and dump it in.  implement the appropriate create method."""

############################### Collections ####################################
class Studies( DatabaseCollection ):
    """ The Studies database."""
    OBJTYPE = Study
#TODO: Eli. this database collection needs a better name.
class StudyDeviceSettings( DatabaseCollection ):
    OBJTYPE = DeviceSettings
class Surveys(DatabaseCollection):
    OBJTYPE = Survey

################################ Exceptions ####################################
class SurveyDoesNotExistError(Exception): pass
class SurveyTypeError(Exception): pass
