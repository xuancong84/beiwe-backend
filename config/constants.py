# This file contains values used throughout the codebase.
# Don't change values if you don't know what they do.

ALLOWED_EXTENSIONS = set(['csv', 'json', 'mp4', 'txt'])
FILE_TYPES = ['gps', 'accel', 'voiceRecording', 'powerState', 'callLog', 'textLog',
              'bluetoothLog', 'surveyAnswers', 'surveyTimings']

#TODO: Eli/Josh. These values are still used in the graph, which needs to be rewritten anyway
DAILY_SURVEY_NAME = 'Daily'
WEEKLY_SURVEY_NAME = 'Weekly'

#Survey types
SURVEY_TYPES = ['audio_survey', 'tracking_survey']

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
