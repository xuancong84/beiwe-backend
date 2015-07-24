import calendar, time

from flask import Blueprint, request, abort, render_template, json

from config.constants import (ALLOWED_EXTENSIONS, SURVEY_ANSWERS_TAG, SURVEY_TIMINGS_TAG,
                            DAILY_SURVEY_NAME, WEEKLY_SURVEY_NAME)
from db.user_models import User
from db.study_models import Study
from libs.encryption import decrypt_device_file
from libs.s3 import s3_upload, get_client_public_key_string, get_client_private_key
from libs.user_authentication import authenticate_user, authenticate_user_registration
from libs.logging import log_error

################################################################################
############################# GLOBALS... #######################################
################################################################################
mobile_api = Blueprint('mobile_api', __name__)

################################################################################
############################# DOWNLOADS ########################################
################################################################################

@mobile_api.route("/download_surveys", methods=['GET', 'POST']) 
@authenticate_user
def download_surveys():
    # TODO: Eli. handle survey deletion in the app correctly.
    patient_id = request.values['patient_id']
    user = User(patient_id)
    study = Study(user.study_id)
    surveys = study.get_surveys_for_study()
    #TODO: Eli/Josh/Alvin there is no way this is valid, there is always something wrong with json dumps.
    return json.dumps(surveys)

#TODO: Eli. find and purge all instances in the app that contain these two urls, point them at the new downloader
# @mobile_api.route('/download_daily_survey', methods=['GET', 'POST'])
# @authenticate_user
# def download_daily_survey():
#     return get_latest_survey('daily')
# 
# @mobile_api.route('/download_weekly_survey', methods=['GET', 'POST'])
# @authenticate_user
# def download_weekly_survey():
#     return get_latest_survey('weekly')


################################################################################
################################ UPLOADS #######################################
################################################################################

@mobile_api.route('/upload', methods=['POST'])
@authenticate_user
def upload():
    """ Entry point to upload GPS, Accelerometer, Audio, PowerState, Calls Log,
        Texts Log, Survey Response, and debugging files to s3"""
    patient_id = request.values['patient_id']
    uploaded_file = request.values['file']
    file_name = request.values['file_name']
#     print "uploaded file name:", file_name, len(uploaded_file)
    client_private_key = get_client_private_key(patient_id)
    try:
        uploaded_file = decrypt_device_file(patient_id, uploaded_file, client_private_key )
    except Exception as e:
        if not e.message == "there was an error in decryption":
            raise
        return abort(406)
        
    #print "decryption success:", file_name
    #if uploaded data a) actually exists, B) is validly named and typed...
    if uploaded_file  and file_name and contains_valid_extension( file_name ):
        data_type, timestamp  = parse_filename( file_name )
        
        #survey files have special file names and need some extra parsing logic
        if SURVEY_ANSWERS_TAG in data_type  or SURVEY_TIMINGS_TAG in data_type:
            file_name = get_s3_filepath_for_survey_data(data_type, patient_id, timestamp)
            
        s3_upload( file_name.replace("_", "/") , uploaded_file )
#         print "upload success: ", file_name
        return render_template('blank.html'), 200
    
    #error cases, (self documenting)
    else:
        #TODO: Eli.  This should probably send an email if it fails.
        error_message ="an upload has failed: " + file_name + ", "
        if not uploaded_file:
            error_message += "there was no/an empty file, returning 200 OK so device deletes bad file."
            log_error( Exception("upload error"), error_message )
            return render_template('blank.html'), 200
        
        elif not file_name:
            error_message += "there was no provided file name, this is an app error."
        elif file_name and not contains_valid_extension( file_name ):
            error_message += "contains an invalid extension, it was interpretted as "
            error_message += grab_file_extension(file_name)
        else: error_message += "AN UNKNOWN ERROR OCCURRED."
        log_error( Exception("upload error"), error_message )
        return abort(400)


################################################################################
############################## Registration ####################################
################################################################################

@mobile_api.route('/register_user', methods=['GET', 'POST'])
@authenticate_user_registration
def register_user():
    """ Checks that the patient id has been granted, and that there is no device
        registered with that id.  If the patient id has no device registered it
        registers this device and logs the bluetooth mac address.
        Returns the encryption key for this patient. """
    #CASE: If the id and password combination do not match, the decorator returns
    # a 403 error.
    patient_id = request.values['patient_id']
    mac_address = request.values['bluetooth_id']
    phone_number = request.values['phone_number']
    device_id = request.values['device_id']
    user = User(patient_id)
    study_id = user['study_id']
#     print "REGISTERING:", patient_id, phone_number, mac_address, device_id
    
    if user['device_id'] is not None and user['device_id'] != request.values['device_id']:
        # CASE: this patient has a registered a device already and it does not
        # match this device.  They need to contact the study and unregister
        # their their other device.  The device will receive a 405 error and
        # should alert the user accordingly.
        # Provided a user does not completely reset their device (which resets
        # the device's unique identifier) they user CAN reregister an existing
        # device, the unlock key they need to enter to at registration is their\
        # old password.
        return abort(405)
    
    # At this point the device has been checked for validity and will be
    # registered successfully.  Any errors after this point will be server errors
    # and return 500 codes
    # the final return will be the encryption key associated with this user.
    
    #Upload the user's various identifiers.
    unix_time = str(calendar.timegm(time.gmtime() ) )
    file_name = patient_id + '/identifiers_' + unix_time + ".csv"
    file_contents = ("patient_id, MAC, phone_number, device_id\n" +
                     patient_id+","+mac_address+","+phone_number+","+device_id )
    s3_upload( file_name, file_contents, study_id )
    # set up device.
    user.set_device( device_id )
    User(patient_id).set_password(request.values['new_password'])
    return get_client_public_key_string(patient_id, study_id), 200


################################################################################
############################### USER FUNCTIONS #################################
################################################################################

@mobile_api.route('/set_password', methods=['GET', 'POST'])
@authenticate_user
def set_password():
    """ After authenticating a user, sets the new password and returns 200."""
    User(request.values["patient_id"]).set_password(request.values["new_password"])
    return render_template('blank.html'), 200

################################################################################
########################## FILE NAME FUNCTIONALITY #############################
################################################################################

#TODO: Eli/Josh: redo file naming.

def parse_filename(filename):
    """ Splits filename into user-id, file-type, unix-timestamp. """
    name = filename.split("_")
    if len(name) == 3:
        return name[1], name[2]

def parse_filetype(file_type):
    """ Separates alphabetical characters from digits for parsing."""
    questions_created_timestamp = filter(str.isdigit, str(file_type))
    survey_data_type = filter(str.isalpha, str(file_type))
    return survey_data_type, questions_created_timestamp

def grab_file_extension(file_name):
    """ grabs the chunk of text after the final period. """
    return file_name.rsplit('.', 1)[1]
    
def contains_valid_extension(file_name):
    """ Checks if string has a recognized file extension, this is not necessarily
        limited to 4 characters."""
    return '.' in file_name and grab_file_extension(file_name) in ALLOWED_EXTENSIONS


def get_s3_filepath_for_survey_data( data_type, patient_id, timestamp ):
    """ The survey config files is in the name of the file, this function processes
        the supplied information and returns the correct file path string."""
    survey_data_type, questions_created_timestamp = parse_filetype( data_type )
#     print "survey_data_type", survey_data_type
#     print "questions_created_timestamp", questions_created_timestamp
    
    survey_frequency = 'UNKNOWN_TYPE'
    if DAILY_SURVEY_NAME in survey_data_type: survey_frequency = DAILY_SURVEY_NAME
    if WEEKLY_SURVEY_NAME in survey_data_type: survey_frequency = WEEKLY_SURVEY_NAME
    
    if SURVEY_ANSWERS_TAG in survey_data_type:
        survey_data_type = SURVEY_ANSWERS_TAG
    if SURVEY_TIMINGS_TAG in survey_data_type:
        survey_data_type = SURVEY_TIMINGS_TAG
    
    return (patient_id + '/' +
            survey_data_type + '/' +
            survey_frequency + '/' +
            questions_created_timestamp + '/' +
            timestamp )


################################################################################
########################### Device Survey Getters ##############################
################################################################################

#TODO: Eli. make sure that this url is pointed at correctly by the app
#TODO: Eli. check that this authenticate_user decorator is correctly used.
@mobile_api.route('/download', methods=['GET', 'POST'])
@authenticate_user
def get_latest_survey():
    user = User(request.values['patient_id'])
    study = Study(user.study_id)
    #TODO: Eli. Check how timings are sent to the app, if they need to be sent inside of this function (probably yes)
    return study.get_surveys_for_study()

#TODO: Eli. Purge any use of the commented urls below, both app and server.
# @survey_designer.route('/get_weekly_survey', methods=['GET', 'POST'])
# def get_latest_weekly():
#     """ Method responsible for fetching latest created weekly survey
#         (frequency 1) """
#     return get_latest_survey('weekly')

# @survey_designer.route('/get_daily_survey', methods=['GET', 'POST'])
# def get_latest_daily():
#     """ Method responsible for fetching latest created daily survey (frequency 1) """
#     return get_latest_survey('daily')
# def get_surveys(prefix):
#     surveys = s3_list_files(prefix)
#     return [survey_file for survey_file in surveys]
