from db.mongolia_setup import DatabaseObject, DatabaseCollection, REQUIRED #, ID_KEY
from db.user_models import Users
from data.constants import SURVEY_TYPES
from bson.objectid import ObjectId

class Study( DatabaseObject ):
    PATH = "beiwe.studies"
    
    DEFAULTS = { "name": REQUIRED,
                 "admins": [],          #admins for the study.
                 "super_admins":[],     #admins that can add admins.
                 "surveys": [],         #the surveys pushed in this study.
                 "device_settings": REQUIRED,  #the device settings for the study.
                 "participants": [],    #paticipants (user ids) in the study
                 "encryption_key": REQUIRED #the study's data encryption key. 
                }
    #Editors
    def add_participant(self, user_id):
        """ Note: participant ids (user ids) are strings, not ObjectIds. """
        self["participants"].append(user_id)
    
    def remove_participant(self, user_id):
        """ Note: participant ids (user ids) are strings, not ObjectIds. """
        if user_id not in self['participants']:
            raise UserDoesNotExistError
        self["participants"].remove(user_id)
    
    def add_admin(self, admin_id):
        """ Note: admin ids are strings, not ObjectIds. """
        self["admins"].append(admin_id)
    
    def remove_admin(self, admin_id):
        """ Note: admin ids are strings, not ObjectIds. """
        if admin_id not in self['participants']:
            raise UserDoesNotExistError
        self["admins"].remove(admin_id)
    
    def add_survey(self, survey):
        """ Note: this takes survey objects, not survey ids."""
        self["surveys"].append(survey._id)
        self.save()
    
    def remove_survey(self, survey):
        """ Note: this takes survey objects, not survey ids."""
        if survey._id not in self['surveys']:
            raise SurveyDoesNotExistError
        self["surveys"].remove(survey._id)
    
    #Accessors, class methods
    @classmethod
    def get_studies_for_admin(cls, admin_id):
        return [Studies(study_id) for study_id in Studies(admins=admin_id)]
    
    #Accessors, instance methods
    def get_participants_in_study(self):
        [ Users(ObjectId(user_id)) for user_id in self.participants ]
    
    def get_surveys_for_study(self):
        return [Surveys(survey_id) for survey_id in self['surveys'] ]
    
    def get_survey_ids_for_study(self):
        return [str(survey) for survey in self['surveys']]
    

class StudyDeviceSettings( DatabaseObject ):
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
    """ Surveys contain all information the app needs to display the survey
        correctly to a user, and when it should push the notifications to take
        the survey.
        
        Surveys must have a 'survey_type', which is a string declaring the type of
        survey it contains, which the app uses to display the correct interface. 
        
        Surveys contain 'content', which is a json string that is unpacked on the
        app and displayed to the user in the form indicated by the survey_type.
        
        Timings schema: a survey must indicate the day of week and time of day
        on which to trigger, by default it contains no values.
        The timings schema mimics the Java.util.Calendar.DayOfWeek specification,
        i.e. it is zero-indexed with day 0 of Sunday.  'timings' is a list of 7
        inner-lists, each inner list contains any number of times of the day,
        times of day are integer values indicating the "seconds past 12am". """
        
    #TODO: Josh. define / document the survey json survey format you created.
    # it doesn't need to be in this document, but this should say where to find it.
    PATH = "database.surveys"
    DEFAULTS = {"content": "",
                "timings": [ [], [], [], [], [], [], [] ],
                "survey_type": REQUIRED }
    
    @classmethod
    def create_default_survey(cls, survey_type):
        if survey_type not in SURVEY_TYPES:
            raise SurveyTypeError("%s is not a valid survey type" % survey_type)
        survey = { "survey_type": survey_type }
        return super(Survey, cls).create(survey, random_id=True)

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
class UserDoesNotExistError(Exception): pass