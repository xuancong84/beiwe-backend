from flask import Blueprint, request, abort, json, render_template

from data.constants import (ALLOWED_EXTENSIONS, SURVEY_ANSWERS_TAG, SURVEY_TIMINGS_TAG,
                            DAILY_SURVEY_NAME, WEEKLY_SURVEY_NAME)
from libs.data_handlers import get_survey_results
from libs.db_models import User
from libs.s3 import ( s3_list_files, s3_upload, get_client_public_key_string,
                      get_client_private_key )

from libs.encryption import decrypt_device_file

from libs.user_authentication import authenticate_user, authenticate_user_registration
from pages.survey_designer import get_latest_survey


################################################################################
############################# GLOBALS... #######################################
################################################################################
mobile_api = Blueprint('mobile_api', __name__)

################################################################################
############################# DOWNLOADS ########################################
################################################################################

@mobile_api.route('/download_daily_survey', methods=['GET', 'POST'])
@authenticate_user
def download_daily_survey():
    return get_latest_survey('daily')

@mobile_api.route('/download_weekly_survey', methods=['GET', 'POST'])
@authenticate_user
def download_weekly_survey():
    return get_latest_survey('weekly')

################################################################################
############################# graph data #######################################
################################################################################


@mobile_api.route('/graph', methods=['GET', 'POST'])
@authenticate_user
def fetch_graph():
    """ Fetches the patient's answers to the most recent survey, marked by
        survey ID. The results are dumped into a jinja template and pushed
        to the device."""
    patient_id = request.values['patient_id']
    data_results = []

    #results is a list of lists
    # inner list 0 is the title/question text
    # inner list 1 is a list of y coordinates
    results = get_survey_results(username=patient_id,
                                 survey_type=DAILY_SURVEY_NAME, number_points=7)
    for pair in results:

        coordinates = [json.dumps(coordinate) for coordinate in pair[1] ]
        # javascript understands json null/none values but not python Nones,
        # we must dump all variables individually.
        data_results.append( [ json.dumps( pair[0] ), coordinates ] )

    return render_template("phone_graphs.html", graphs=data_results)


################################################################################
################################ UPLOADS #######################################
################################################################################

@mobile_api.route('/upload', methods=['POST'])
@authenticate_user
def upload():
    """ Entry point to relay GPS, Accelerometer, Audio, PowerState, Calls Log,
        Texts Log, and Survey Response files. """
    patient_id = request.values['patient_id']
    uploaded_file = request.values['file']
    file_name = request.values['file_name']
    #print "uploaded file name:", file_name, len(uploaded_file)
    
    #Debugging code, decrypts non-media files from Eli's tablet
    if patient_id == "18wh3b" and file_name[-4:] != ".mp4":
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
            
        #TODO: Eli. debug, drop the file name conditional, dedent, drop the try-except, dedent.
        if file_name[-4:] == ".mp4":
            print "media file length:", len(uploaded_file)
            try:
                client_private_key =client_private_key = get_client_private_key(patient_id)
                decrypted_data = decrypt_device_file(patient_id, uploaded_file,
                                                     client_private_key )
                s3_upload(file_name.replace("_", "/"), decrypted_data)
                          
            except Exception as e:
                if not e.message == "there was an error in decryption":
                    raise
                return abort(406)
        else:
            s3_upload( file_name.replace("_", "/") , uploaded_file )
        print "upload success: ", file_name
        return render_template('blank.html'), 200
    
    #error cases, (self documenting)
    else:
        print "an upload has failed, ", file_name,
        if not uploaded_file:
            print "there was no/an empty uploaded file, returning 200 OK so device deletes bad file."
            return render_template('blank.html'), 200
        elif not file_name: print "there was no provided file name, device error."
        elif file_name and not contains_valid_extension( file_name ):
            print ("contains an invalid extension, it was interpretted as",
            grab_file_extension(file_name) )
        else: print "AN UNKNOWN ERROR OCCURRED"
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
    print "REGISTERING:", patient_id, phone_number, mac_address, device_id
    
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
    
    upload_device_ids(patient_id, mac_address, phone_number, device_id)
    user.set_device( device_id )
    User(patient_id).set_password(request.values['new_password'])
    return get_client_public_key_string(patient_id), 200


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
############################ RELATED FUNCTIONALITY #############################
################################################################################

def upload_device_ids( patient_id, mac_address, phone_number, device_id ):
    """ Uploads the user's various identifiers. """
    number_of_files = len( s3_list_files(patient_id + '/identifiers' ) )
    file_name = patient_id + '/identifiers_' + str(number_of_files)
    file_contents = ("patient_id, MAC, phone_number, device_id\n" +
                     patient_id+","+mac_address+","+phone_number+","+device_id )
    s3_upload( file_name, file_contents )

def parse_filename(filename):
    """ Splits filename into user-id, file-type, unix-timestamp. """
    name = filename.split("_")
    if len(name) == 3:
        return name[1], name[2]

def parse_filetype(file_type):
    """ Separates alphabetical characters from digits for parsing."""
    questions_created_timestamp = filter(str.isdigit, str(file_type)).lower()
    survey_data_type = filter(str.isalpha, str(file_type)).lower()
    return survey_data_type, questions_created_timestamp

def grab_file_extension(file_name):
    return file_name.rsplit('.', 1)[1]
    
def contains_valid_extension(file_name):
    """ Checks if string has a recognized file extension, this is not necessarily
        limited to 4 characters."""
    return '.' in file_name and grab_file_extension(file_name) in ALLOWED_EXTENSIONS


def get_s3_filepath_for_survey_data( data_type, patient_id, timestamp ):
    """ The survey data files is in the name of the file, this function processes
        the supplied information and returns the correct file path string."""
    survey_data_type, questions_created_timestamp = parse_filetype( data_type )
    print "survey_data_type", survey_data_type
    print "questions_created_timestamp", questions_created_timestamp
    
    survey_frequency = 'UNKNOWN_TYPE'
    if 'daily' in survey_data_type: survey_frequency = DAILY_SURVEY_NAME
    if 'weekly' in survey_data_type: survey_frequency = WEEKLY_SURVEY_NAME
    
    if survey_data_type.startswith( SURVEY_ANSWERS_TAG ):
        survey_data_type = SURVEY_ANSWERS_TAG
    if survey_data_type.startswith( SURVEY_TIMINGS_TAG ):
        survey_data_type = SURVEY_TIMINGS_TAG
    
    return (patient_id + '/' +
            survey_data_type + '/' +
            survey_frequency + '/' +
            questions_created_timestamp + '/' +
            timestamp )

