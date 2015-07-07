from db.mongolia_setup import DatabaseObject, DatabaseCollection, REQUIRED #, ID_KEY
from db.user_models import Users
from data.constants import SURVEY_TYPES

class Study( DatabaseObject ):
    PATH = "beiwe.studies"
    
    DEFAULTS = { "name": REQUIRED,
                 "admins": [],          #admins for the study.
                 "super_admins":[],     #admins that can add admins.
                 "surveys": [],      #the surveys pushed in this study.
                 "settings": REQUIRED,  #the device settings for the study.
                 "participants": [],
                 "encryption_key": REQUIRED }
    
    @classmethod
    def get_studies_for_admin(cls, admin_id):
        return [Studies(study_id) for study_id in Studies(admins=admin_id)]
    
    def add_survey(self, survey):
        self["surveys"].append(survey._id)
        self.save()
    
    def remove_survey(self, survey_id):
#         if survey_id not in self['surveys']:
#             raise SurveyDoesNotExistError
        self["surveys"].remove()
    
    #TODO: Eli. test that this works and is not a cyclic import (it shouldn't be...)
    def get_participants_in_study(self):
        [ Users(participants) for participants in self.participants ]
    
    def get_surveys_for_study(self):
        return [Surveys(survey_id) for survey_id in self['surveys'] ]
    
    def list_survey_ids_for_study(self):
        return [str(survey) for survey in self['surveys']]


class DeviceSettings( DatabaseObject ):
    """ The DeviceSettings database contains the structure that defines
        settings pushed to devices of users in of a study."""
    PATH = "beiwe.device_settings"
    #TODO: Eli/Josh. sensor and timer variables here, names possibly subject to change,
    # ensure that any changes here are well defined and enforced in frontend
    # and on the app.
    DEFAULTS = {#sensors:
                "accelerometer":False,
                "gps":False,
                "calls":False,
                "texts":False,
                "wifi":False,
                "bluetooth":False,
                "power_state":False,
                #timer variables
                "accelerometer_off_duration_seconds": 300,
                "accelerometer_on_duration_seconds": 300,
                "bluetooth_on_duration_seconds": 300,
                "bluetooth_total_duration_seconds": 300, #TODO: Eli, change this to off duration in app and here.
                "bluetooth_global_offset_seconds": 150, #TODO: Eli. determine whether we definitely need this. 
                "check_for_new_surveys_frequency_seconds": 3600 * 6,
                "create_new_data_files_frequency_seconds": 15 * 60,
                "gps_off_duration_seconds": 300,
                "gps_on_duration_seconds": 300,
                "seconds_before_auto_logout": 300,
                "upload_data_files_frequency_seconds": 3600,
                "voice_recording_max_time_length_seconds": 300,
                "wifi_log_frequency_seconds": 300
                }


class Survey( DatabaseObject ):
    PATH = "database.surveys"
    
    DEFAULTS = {"content": REQUIRED,
                "timings": REQUIRED,
                "survey_type": REQUIRED }
    
    #TODO: Eli. probably should have some kind of survey type check here
    @classmethod
    def create_default_survey(cls, survey_type):
        if survey_type not in SURVEY_TYPES:
            raise SurveyTypeError("%s is not a valid survey type" % survey_type)
        survey = {'content':"",
                  'timings': [False, False, False, False, False, False, False],
                  "survey_type": survey_type }
        return super(Survey, cls).create(survey, random_id=True)

    """TODO: Eli define a valid date-time schema
        list: days of week, starting on a sunday? (check implementation on android)
            of integers, in android we check day of the week and set that alarm.
            (check the app, I think sunday is 0 index)"""
    """TODO: Eli. determine exactly what data goes into a survey (I think it is already
        # a json string), and dump it in.  implement the appropriate create method."""

"""############################ Collections #################################"""
class Studies( DatabaseCollection ):
    """ The Studies database."""
    OBJTYPE = Study
class StudyDeviceSettings( DatabaseCollection ):
    """ The per-study device settings. """
    OBJTYPE = DeviceSettings
class Surveys( DatabaseCollection ):
    """ The Surveys database."""
    OBJTYPE = Survey

"""############################# Exceptions #################################"""
class SurveyDoesNotExistError(Exception): pass
class SurveyTypeError(Exception): pass
