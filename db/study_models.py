from db.mongolia_setup import DatabaseObject, DatabaseCollection, REQUIRED #, ID_KEY
from config.constants import SURVEY_TYPES
from __builtin__ import classmethod


class Study( DatabaseObject ):
    PATH = "beiwe.studies"
    
    DEFAULTS = { "name": REQUIRED,
                 "admins": [],          #admins for the study.
                 "super_admins":[],     #admins that can add admins.
                 #TODO: Low Priority. Eli/Josh. the above variable will be used in the yet-to-be-implemented 3-tier user model.
                 "surveys": [],         #the surveys pushed in this study.
                 "device_settings": REQUIRED,  #the device settings for the study.
                 "encryption_key": REQUIRED #the study's config encryption key. 
                }
    
    @classmethod
    def create_default_study(cls, name, encryption_key):
        if Studies(name=name):
            raise StudyAlreadyExistsError("a study named %s already exists" % name)
        if len(encryption_key) != 32:
            error_text = "the encryption key must be 32 characters, you only " +\
                         "entered %d characters" % len(encryption_key)
            raise InvalidEncryptionKeyError(error_text)
        device_settings = StudyDeviceSettings.create_default()
        study = { "name":name,
                 "encryption_key":encryption_key,
                 "device_settings":device_settings._id
                 }
        return Study.create(study, random_id=True)
        
    #Editors
    def add_admin(self, admin_id):
        """ Note: admin ids are strings, not ObjectIds. """
        if not (admin_id in self["admins"]):
            self["admins"].append(admin_id)
            self.save()
    
    def remove_admin(self, admin_id):
        """ Note: admin ids are strings, not ObjectIds. """
        if admin_id in self['admins']:
            self["admins"].remove(admin_id)
            self.save()
    
    def add_survey(self, survey):
        """ Note: this takes survey objects, not survey ids."""
        self["surveys"].append(survey._id)
        self.save()
    
    def remove_survey(self, survey):
        """ Note: this takes survey objects, not survey ids."""
        if survey._id not in self['surveys']:
            raise SurveyDoesNotExistError
        self["surveys"].remove(survey._id)
        self.save()
    
    #Accessors, class methods
    @classmethod
    def get_studies_for_admin(cls, admin_id):
        return [Studies(_id=study_id) for study_id in Studies(admins=admin_id)]
    
    def get_surveys_for_study(self):
        """ Returns a dict of survey_id strings paired with their survey data. """
        ret = [ dict(Survey(survey_id)) for survey_id in self['surveys'] ]
        for x in ret:
            x['_id'] = str(x['_id'])
        return ret
    
    def get_survey_ids_for_study(self, survey_type='tracking_survey'):
        return [Survey(survey_id)['_id'] for survey_id in self['surveys']
                if Survey(survey_id)['survey_type'] == survey_type]
    
    def get_study_device_settings(self):
        return StudyDeviceSettings(self['device_settings'])
    
    
class StudyDeviceSettings( DatabaseObject ):
    """ The DeviceSettings database contains the structure that defines
        settings pushed to devices of users in of a study."""
    PATH = "beiwe.device_settings"
    #TODO: Eli/Josh. sensor and timer variables here, names possibly subject to change,
    # ensure that any changes here are well defined and enforced in frontend
    # and on the app.
    #VERY IMPORTANT: ensure that any toggles displayed on the website using
    # CHECKBOXES are enumerated in CHECKBOX_TOGGLES in constants.
    DEFAULTS = {#device sensors (listeners)
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
                "bluetooth_total_duration_seconds": 0, #TODO: Eli. change this to off duration in app and here.
                "bluetooth_global_offset_seconds": 150, #TODO: Eli. determine whether we definitely need this parameter for bluetooth. 
                "check_for_new_surveys_frequency_seconds": 3600 * 6,
                "create_new_data_files_frequency_seconds": 15 * 60,
                "gps_off_duration_seconds": 300,
                "gps_on_duration_seconds": 300,
                "seconds_before_auto_logout": 300,
                "upload_data_files_frequency_seconds": 3600,
                "voice_recording_max_time_length_seconds": 300,
                "wifi_log_frequency_seconds": 300,
                #text strings
                "about_page_text": "The Beiwe application runs on your phone and helps researchers collect information about your behaviors. Beiwe may ask you to fill out short surveys or to record your voice. It may collect information about your location (using phone GPS) and how much you move (using phone accelerometer). Beiwe may also monitor how much you use your phone for calling and texting and keep track of the people you communicate with. Importantly, Beiwe never records the names or phone numbers of anyone you communicate with. While it can tell if you call the same person more than once, it does not know who that person is. Beiwe also does not record the content of your text messages or phone calls. Beiwe may keep track of the different Wi-Fi networks and Bluetooth devices around your phone, but the names of those networks are replaced with random codes.\n\nAlthough Beiwe collects large amounts of data, the data is processed to protect your privacy. This means that it does not know your name, your phone number, or anything else that could identify you. Beiwe only knows you by an identification number. Because Beiwe does not know who you are, it cannot communicate with your clinician if you are ill or in danger. Researchers will not review the data Beiwe collects until the end of the study. To make it easier for you to connect with your clinician, the 'Call my Clinician' button appears at the bottom of every page.\n\nBeiwe was conceived and designed by Dr. Jukka-Pekka 'JP' Onnela at the Harvard T.H. Chan School of Public Health. Development of the Beiwe smartphone application and data analysis software is funded by NIH grant 1DP2MH103909-01 to Dr. Onnela. The smartphone application was built by Zagaran, Inc., in Cambridge, Massachusetts.",
                "call_clinician_button_text": "Call My Clinician",
                "consent_form_text": " I have read and understood the information about the study and all of my questions about the study have been answered by the study researchers.",
                "survey_submit_success_toast_text": """Thank you for completing the survey.  A clinician will not see your answers immediately, so if you need help or are thinking about harming yourself, please contact your clinician.  You can also press the "Call My Clinician" button."""
            }
    @classmethod
    def create_default(cls):
        return StudyDeviceSettings.create(cls.DEFAULTS, random_id=True)
    
    
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
        
    #TODO: Low priority. Josh. define / document the survey json survey format you created.
    # it doesn't need to be in this document, but this should say where to find it.
    PATH = "beiwe.surveys"
    DEFAULTS = {"content": [],
                "timings": [ [], [], [], [], [], [], [] ],
                "survey_type": REQUIRED,
                "settings":{} }
    
    @classmethod
    def create_default_survey(cls, survey_type):
        if survey_type not in SURVEY_TYPES:
            raise SurveyTypeError("%s is not a valid survey type" % survey_type)
        survey = { "survey_type": survey_type }
        return Survey.create(survey, random_id=True)
    
    #debugging function
#     def set_alarms_thirty_seconds(self):
#         now = datetime.now() - timedelta(seconds = 3600*4) #EDT, server is UTC.
#         start_of_day = datetime(now.year, now.month, now.day)
#         time_diff = int((now - start_of_day).total_seconds() + 30)
#         self['timings'] =[ [time_diff],
#                              [time_diff],
#                              [time_diff],
#                              [time_diff],
#                              [time_diff],
#                              [time_diff],
#                              [time_diff] ]
#         self.save()

"""############################ Collections #################################"""
class Studies( DatabaseCollection ):
    """ The Studies database."""
    OBJTYPE = Study
class StudyDeviceSettingsCollection( DatabaseCollection ):
    """ The per-study device settings. """
    OBJTYPE = StudyDeviceSettings
class Surveys( DatabaseCollection ):
    """ The Surveys database."""
    OBJTYPE = Survey

"""############################# Exceptions #################################"""
class SurveyDoesNotExistError(Exception): pass
class SurveyTypeError(Exception): pass
class UserDoesNotExistError(Exception): pass
class StudyAlreadyExistsError(Exception): pass
class InvalidEncryptionKeyError(Exception): pass