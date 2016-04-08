""" This file contains values used throughout the codebase.
    Don't change values if you don't know what they do. """

## Data streams and survey types ##
ALLOWED_EXTENSIONS = {'csv', 'json', 'mp4', "wav", 'txt'}
PROCESSABLE_FILE_EXTENSIONS = [".csv", ".mp4", ".wav"]
MEDIA_EXTENSIONS = [".mp4", ".wav"]
FILE_TYPES = ['gps', 'accel', 'voiceRecording', 'powerState', 'callLog', 'textLog',
              'bluetoothLog', 'surveyAnswers', 'surveyTimings']
SURVEY_TYPES = ['audio_survey', 'tracking_survey']

## HTML lists ##
CHECKBOX_TOGGLES = ["accelerometer",
                    "gps",
                    "calls",
                    "texts",
                    "wifi",
                    "bluetooth",
                    "power_state"]

TIMER_VALUES = ["accelerometer_off_duration_seconds",
                "accelerometer_on_duration_seconds",
                "bluetooth_on_duration_seconds",
                "bluetooth_total_duration_seconds",
                "bluetooth_global_offset_seconds", 
                "check_for_new_surveys_frequency_seconds",
                "create_new_data_files_frequency_seconds",
                "gps_off_duration_seconds",
                "gps_on_duration_seconds",
                "seconds_before_auto_logout",
                "upload_data_files_frequency_seconds",
                "voice_recording_max_time_length_seconds",
                "wifi_log_frequency_seconds"]

## Networking ##
DEFAULT_S3_RETRIES = 1 #This value is used in libs.s3, does what it says.
CONCURRENT_NETWORK_OPS = 10
NUMBER_FILES_IN_FLIGHT = 100
FILE_PROCESS_PAGE_SIZE = 250
#NOTE: these number was determined through trial and error on a C4 Large AWS instance.  There is a point in
# when reindexing the full dataset (@300,000 items it was after processing ~120,000)
# there are a chunk of files that, with a page size of 250, fills up ~38% of 
# available memory on a server with 4GB of ram.
# (There was also a memory leak that exacerbated this, but it has been vastly reduced/solved.)

API_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S"
"""1990-01-31T07:30:04 gets you jan 31 1990 at 7:30:04am
   human string is YYYY-MM-DDThh:mm:ss """
# This value is in seconds, it sets the time period that chunked files will be sliced into.
CHUNK_TIMESLICE_QUANTUM = 3600
# the name of the s3 folder that contains chunked data
CHUNKS_FOLDER = "CHUNKED_DATA"

# Constants for for the keys in data_stream_to_s3_file_name_string
ACCELEROMETER = "accelerometer"
BLUETOOTH = "bluetooth"
CALL_LOG = "calls"
GPS = "gps"
IDENTIFIERS = "identifiers"
LOG_FILE = "app_log"
POWER_STATE = "power_state"
SURVEY_ANSWERS = "survey_answers"
SURVEY_TIMINGS = "survey_timings"
TEXTS_LOG = "texts"
VOICE_RECORDING = "audio_recordings"
WIFI = "wifi"

ALL_DATA_STREAMS = [ACCELEROMETER, BLUETOOTH, CALL_LOG, GPS, IDENTIFIERS,
                    LOG_FILE, POWER_STATE, SURVEY_ANSWERS, SURVEY_TIMINGS,
                    TEXTS_LOG, VOICE_RECORDING, WIFI]

SURVEY_DATA_FILES = [SURVEY_ANSWERS, SURVEY_TIMINGS]

def data_stream_to_s3_file_name_string(data_type):
    """Maps a data type to the internal string representation used throughout the codebase.
        (could be a dict mapping, but it is fine) """
    if data_type == ACCELEROMETER: return "accel"
    if data_type == BLUETOOTH: return "bluetoothLog"
    if data_type == CALL_LOG: return "callLog"
    if data_type == GPS: return "gps"
    if data_type == IDENTIFIERS: return "identifiers"
    if data_type == LOG_FILE: return "logFile"
    if data_type == POWER_STATE: return "powerState"
    if data_type == SURVEY_ANSWERS: return "surveyAnswers"
    if data_type == SURVEY_TIMINGS: return "surveyTimings"
    if data_type == TEXTS_LOG: return "textsLog"
    if data_type == VOICE_RECORDING: return "voiceRecording"
    if data_type == WIFI: return "wifiLog"
    raise Exception("unknown data type: %s" % data_type)

CHUNKABLE_FILES = { ACCELEROMETER, BLUETOOTH, CALL_LOG, GPS, IDENTIFIERS,
                  LOG_FILE, POWER_STATE, SURVEY_TIMINGS, TEXTS_LOG, WIFI }
# RAW_FILES = set([SURVEY_ANSWERS, VOICE_RECORDING, LOG_FILE ])
