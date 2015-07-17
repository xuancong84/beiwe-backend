# This file contains values used throughout the codebase.
# Don't change values if you don't know what they do.

# the name of the s3 bucket that will be used to store config
S3_BUCKET = "edit_me"

#the length of the public/private keys used in encrypting user config on their device
ASYMMETRIC_KEY_LENGTH = 2048

#the number of iterations used in password hashing.
ITERATIONS = 1000


ALLOWED_EXTENSIONS = set(['csv', 'json', 'mp4', 'txt'])
FILE_TYPES = ['gps', 'accel', 'voiceRecording', 'powerState', 'callLog', 'textLog',
              'bluetoothLog', 'surveyAnswers', 'surveyTimings']

#these strings are tags used in identifying files created by the surveys.
SURVEY_ANSWERS_TAG = 'surveyAnswers'
SURVEY_TIMINGS_TAG = 'surveyTimings'

#TODO: Eli. get rid of these.
DAILY_SURVEY_NAME = 'Daily'
WEEKLY_SURVEY_NAME = 'Weekly'

#Survey types
SURVEY_TYPES = ['audio', 'android_survey']

# class SURVEY_TYPES(object):
#     audio = "audio"
#     android_survey = "android_survey"

CHECKBOX_TOGGLES = ["accelerometer",
                  "gps",
                  "calls",
                  "texts",
                  "wifi",
                  "bluetooth",
                  "power_state"
                ]

