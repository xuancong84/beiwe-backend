from os import getenv
from config.study_constants import *
from config.settings import DOMAIN_NAME

### Environment settings ###
# All settings here can be configured by setting an environment variable, or by editing the default value

# To customize any of these values, use the following pattern.
# DEFAULT_S3_RETRIES = getenv("DEFAULT_S3_RETRIES") or 10
# Note that this file is _not_ in the gitignore.

## Networking
#This value is used in libs.s3, does what it says.
DEFAULT_S3_RETRIES = getenv("DEFAULT_S3_RETRIES") or 1

## File processing directives
#NOTE: these numbers were determined through trial and error on a C4 Large AWS instance.
#Used in data download and data processing, base this on CPU core count.
CONCURRENT_NETWORK_OPS = getenv("CONCURRENT_NETWORK_OPS") or 10
#Used in file processing, number of files to be pulled in and processed simultaneously.
# Higher values reduce s3 usage, reduce processing time, but increase ram requirements.
FILE_PROCESS_PAGE_SIZE = getenv("FILE_PROCESS_PAGE_SIZE") or 250

#This string will be printed into non-error hourly reports to improve error filtering.
DATA_PROCESSING_NO_ERROR_STRING = getenv("DATA_PROCESSING_NO_ERROR_STRING") or "2HEnBwlawY"

# The number of minutes after which a queued celery task will be invalidated.
# (this is not a timeout, it only invalidates tasks that have not yet run.)
CELERY_EXPIRY_MINUTES = getenv("CELERY_EXPIRY_MINUTES") or 4
CELERY_ERROR_REPORT_TIMEOUT_SECONDS = getenv("CELERY_ERROR_REPORT_TIMEOUT_SECONDS") or 60*15


## Data streams and survey types ##
ALLOWED_EXTENSIONS = {'csv', 'json', 'mp4', "wav", 'txt', 'jpg'}
PROCESSABLE_FILE_EXTENSIONS = [".csv", ".mp4", ".wav"]

# File names that will be checked for data presence
CHECKABLE_FILES = ['accel', 'accessibilityLog', 'callLog', 'gyro', 'gps', 'magnetometer', 'steps', 'light', 'powerState', 'tapsLog', 'textsLog', 'usage']
ALLOW_EMPTY_FILES = {'callLog', 'textsLog'}

## All device parameters
ALL_DEVICE_PARAMETERS = [
    # Study settings (must be put at the beginning, these will NOT be sent to phone during registration)
    [["study_cycle_days", 30], ["date_elapse_color", '"lime" if elapse<30*3600 else ("orange" if elapse<72*3600 else "red")'],
     ["daily_check_formula", 'a=[light>24, accel>24, gps>0, accessibilityLog>5, textsLog>0, callLog>0, tapsLog>5, usage>1, powerState>1].count(True);output="<font color=%s>%d</font>"%("lime" if a>6 else ("orange" if a>3 else "red"), a)'],
     ['external_dashboards', '']],

    # APP settings
    [["calls", True], ["texts", True]],
    [["accelerometer", True], ["accelerometer_off_duration_seconds", 590], ["accelerometer_on_duration_seconds", 10]],
    [["ambientlight", True], ["ambientlight_interval_seconds", 300]],
    [["gps", True], ["use_gps_fuzzing", True], ["gps_off_duration_seconds", 870], ["gps_on_duration_seconds", 30]],
    [["bluetooth", False], ["bluetooth_on_duration_seconds", 60], ["bluetooth_total_duration_seconds", 300], ["bluetooth_global_offset_seconds", 0]],
    [["gyro", False], ["gyro_off_duration_seconds", 600], ["gyro_on_duration_seconds", 60]],
    [["magnetometer", False], ["magnetometer_off_duration_seconds", 600], ["magnetometer_on_duration_seconds", 60]],
    [["steps", False], ["steps_off_duration_seconds", 0], ["steps_on_duration_seconds", 30*60]],
    [["devicemotion", False], ["devicemotion_off_duration_seconds", 600], ["devicemotion_on_duration_seconds", 60]],
    [["usage", False], ["usage_update_interval_seconds", 60*60]],
    [["wifi", True]],
    [["power_state", True]],
    [["taps", False]],
    [["accessibility", False]],
    [["proximity", False]],
    [["reachability", True]],
    [["allow_upload_over_cellular_data", False], ["use_anonymized_hashing", True], ["phone_number_length", 8],
     ["write_buffer_size", 512], ["primary_care", ''], ['use_compression', True]],
    [["check_for_new_surveys_frequency_seconds", 3600*12], ["create_new_data_files_frequency_seconds", 60*60], ["seconds_before_auto_logout", 0],
     ["upload_data_files_frequency_seconds", 3600*12], ["voice_recording_max_time_length_seconds", 240], ["wifi_log_frequency_seconds", 3600]],
    [["about_page_text", ABOUT_PAGE_TEXT], ["call_clinician_button_text", CALL_BUTTON_TEXT],
     ["consent_form_text", CONSENT_FORM_TEXT], ["survey_submit_success_toast_text", SURVEY_SUBMIT_SUCCESS_TOAST_TEXT]]
]

# The format that dates should be in throughout the codebase
API_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S"
"""1990-01-31T07:30:04 gets you jan 31 1990 at 7:30:04am
   human string is YYYY-MM-DDThh:mm:ss """

## Chunks
# This value is in seconds, it sets the time period that chunked files will be sliced into.
CHUNK_TIMESLICE_QUANTUM = 3600
# the name of the s3 folder that contains chunked data
CHUNKS_FOLDER = "CHUNKED_DATA"
PIPELINE_FOLDER = "PIPELINE_DATA"

## Constants for for the keys in data_stream_to_s3_file_name_string
ACCELEROMETER = "accelerometer"
AMBIENTLIGHT = "ambientlight"
ACCESSIBILITY = "accessibility"
BLUETOOTH = "bluetooth"
CALL_LOG = "calls"
GPS = "gps"
TAPS = "taps"
STEPS = "steps"
IDENTIFIERS = "identifiers"
ANDROID_LOG_FILE = "app_log"
IOS_LOG_FILE = "ios_log"
POWER_STATE = "power_state"
SURVEY_ANSWERS = "survey_answers"
SURVEY_TIMINGS = "survey_timings"
TEXTS_LOG = "texts"
USAGE = "usage"
VOICE_RECORDING = "audio_recordings"
IMAGE_FILE = "image_survey"
WIFI = "wifi"
PROXIMITY = "proximity"
GYRO = "gyro"
MAGNETOMETER = "magnetometer"
DEVICEMOTION = "devicemotion"
REACHABILITY = "reachability"



ALL_DATA_STREAMS = [ACCELEROMETER,
                    AMBIENTLIGHT,
                    ACCESSIBILITY,
                    BLUETOOTH,
                    CALL_LOG,
                    GPS,
                    IDENTIFIERS,
                    ANDROID_LOG_FILE,
                    POWER_STATE,
                    SURVEY_ANSWERS,
                    SURVEY_TIMINGS,
                    TAPS,
                    TEXTS_LOG,
                    USAGE,
                    VOICE_RECORDING,
                    WIFI,
                    PROXIMITY,
                    GYRO,
                    MAGNETOMETER,
					STEPS,
                    DEVICEMOTION,
                    REACHABILITY,
                    IOS_LOG_FILE,
                    IMAGE_FILE]

SURVEY_DATA_FILES = [SURVEY_ANSWERS, SURVEY_TIMINGS]

UPLOAD_FILE_TYPE_MAPPING = {
    "accel": ACCELEROMETER,
    "accessibilityLog": ACCESSIBILITY,
    "light": AMBIENTLIGHT,
    "bluetoothLog": BLUETOOTH,
    "callLog": CALL_LOG,
    "devicemotion": DEVICEMOTION,
    "gps": GPS,
    "gyro": GYRO,
    "tapsLog": TAPS,
    "logFile": ANDROID_LOG_FILE,
    "magnetometer": MAGNETOMETER,
    "steps": STEPS,
    "powerState": POWER_STATE,
    "reachability": REACHABILITY,
    "surveyAnswers": SURVEY_ANSWERS,
    "surveyTimings": SURVEY_TIMINGS,
    "textsLog": TEXTS_LOG,
    "usage": USAGE,
    "voiceRecording": VOICE_RECORDING,
    "wifiLog": WIFI,
    "proximity": PROXIMITY,
    "ios_log": IOS_LOG_FILE,
    "imageSurvey":IMAGE_FILE,
}

def data_stream_to_s3_file_name_string(data_type):
    """Maps a data type to the internal string representation used throughout the codebase.
        (could be a dict mapping, but it is fine) """
    if data_type == IDENTIFIERS:
        return "identifiers"
    for k, v in UPLOAD_FILE_TYPE_MAPPING.iteritems():
        if data_type == v:
            return k
    raise Exception("unknown data type: %s" % data_type)

CHUNKABLE_FILES = {ACCELEROMETER,
                   AMBIENTLIGHT,
                   ACCESSIBILITY,
                   BLUETOOTH,
                   CALL_LOG,
                   GPS,
                   TAPS,
                   IDENTIFIERS,
                   ANDROID_LOG_FILE,
                   POWER_STATE,
                   SURVEY_TIMINGS,
                   TEXTS_LOG,
                   USAGE,
                   WIFI,
                   PROXIMITY,
                   GYRO,
				   STEPS,
                   MAGNETOMETER,
                   DEVICEMOTION,
                   REACHABILITY,
                   IOS_LOG_FILE}

## Survey Question Types
FREE_RESPONSE = "free_response"
CHECKBOX = "checkbox"
RADIO_BUTTON = "radio_button"
SLIDER = "slider"
INFO_TEXT_BOX = "info_text_box"

ALL_QUESTION_TYPES = {FREE_RESPONSE,
                      CHECKBOX,
                      RADIO_BUTTON,
                      SLIDER,
                      INFO_TEXT_BOX }

NUMERIC_QUESTIONS = {RADIO_BUTTON,
                     SLIDER,
                     FREE_RESPONSE }

## Free Response text field types (answer types)
FREE_RESPONSE_NUMERIC = "NUMERIC"
FREE_RESPONSE_SINGLE_LINE_TEXT = "SINGLE_LINE_TEXT"
FREE_RESPONSE_MULTI_LINE_TEXT = "MULTI_LINE_TEXT"

TEXT_FIELD_TYPES = {FREE_RESPONSE_NUMERIC,
                    FREE_RESPONSE_SINGLE_LINE_TEXT,
                    FREE_RESPONSE_MULTI_LINE_TEXT }

## Comparators
COMPARATORS = {"<",
               ">",
               "<=",
               ">=",
               "==",
               "!=" }

NUMERIC_COMPARATORS = {"<",
                       ">",
                       "<=",
                       ">=" }

## Password Check Regexes
SYMBOL_REGEX = "[^a-zA-Z0-9]"
LOWERCASE_REGEX = "[a-z]"
UPPERCASE_REGEX = "[A-Z]"
NUMBER_REGEX = "[0-9]"
PASSWORD_REQUIREMENT_REGEX_LIST = [SYMBOL_REGEX, LOWERCASE_REGEX, UPPERCASE_REGEX, NUMBER_REGEX]

DEVICE_IDENTIFIERS_HEADER = "patient_id,MAC,phone_number,device_id,device_os,os_version,product,brand,hardware_id,manufacturer,model,beiwe_version\n"

# Encryption constants
ASYMMETRIC_KEY_LENGTH = 2048  # length of private/public keys
ITERATIONS = 1000  # number of SHA iterations in password hashing

# Error reporting send-from emails
E500_EMAIL_ADDRESS = 'e500_error@{}'.format(DOMAIN_NAME)
OTHER_EMAIL_ADDRESS = 'telegram_service@{}'.format(DOMAIN_NAME)
