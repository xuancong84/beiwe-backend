# This file contains values used throughout the codebase.
# Don't change values if you don't know what they do.

# the name of the s3 bucket that will be used to store data
S3_BUCKET = "zagaran-beiwe"

#the length of the public/private keys used in encrypting user data on their device
ASYMMETRIC_KEY_LENGTH = 2048

#the number of iterations used in password hashing.
ITERATIONS = 1000


ALLOWED_EXTENSIONS = set(['csv', 'json', 'mp4', 'txt'])
FILE_TYPES = ['gps', 'accel', 'voiceRecording', 'powerState', 'callLog', 'textLog',
              'bluetoothLog', 'surveyAnswers', 'surveyTimings']

#these strings are tags used in identifying files created by the surveys.
SURVEY_ANSWERS_TAG = 'surveyAnswers'
SURVEY_TIMINGS_TAG = 'surveyTimings'

#TODO: get rid of these.
DAILY_SURVEY_NAME = 'Daily'
WEEKLY_SURVEY_NAME = 'Weekly'