from flask import Blueprint, request, abort, json, render_template
from werkzeug import secure_filename

from libs.data_handlers import get_weekly_results
from libs.db_models import User
from libs.encryption import get_client_public_key_string#, decrypt_rsa_lines
from libs.s3 import (s3_upload_handler_file, s3_retrieve, s3_list_files,
                     s3_upload_handler_string)
from libs.user_authentication import authenticate_user, authenticate_user_registration

################################################################################
############################# GLOBALS... #######################################
################################################################################
mobile_api = Blueprint('mobile_api', __name__)

ALLOWED_EXTENSIONS = set(['csv', '3gp', 'json', 'mp4', 'txt'])
FILE_TYPES = ['gps', 'accel', 'voiceRecording', 'powerState', 'callLog', 'textLog',
              'bluetoothLog', 'surveyAnswers', 'surveyTimings']

ANSWERS_TAG = 'surveyAnswers'
TIMINGS_TAG = 'surveyTimings'


@mobile_api.route('/test', methods=['GET', 'POST'])
@authenticate_user
def test():
        return "abc123", 200


################################################################################
############################# DOWNLOADS ########################################
################################################################################

@mobile_api.route('/fetch_survey', methods=['GET', 'POST'])
@authenticate_user
def fetch_survey():
    """ Method responsible for serving the latest survey JSON. """
    return s3_retrieve("all_surveys/current_survey")


#TODO: Dori.  Update the url in the android app to point to /graph
@mobile_api.route('/graph', methods=['GET', 'POST'])
# @authenticate_user
def fetch_graph():
    """ TODO: This function fetches the patient's answers to the most recent survey,
    marked by survey ID. The results are rendered on a template in the patient's
    phone"""
    patient_id = request.values['patient_id']
    #TODO: Dori.  clean up, make variable named what they contain.
    data_results = []
#     results = [json.dumps(i) for i in get_weekly_results(username=userID)]
    results = get_weekly_results(username=patient_id)
    for pair in results:
        data_results.append([pair[0], json.dumps(pair[1])])
    print data_results
    return render_template("phone_graphs.html", data=results)


################################################################################
################################ UPLOADS #######################################
################################################################################

@mobile_api.route('/upload', methods=['POST'])
# @authenticate_user
def upload():
    """ Entry point to relay GPS, Accelerometer, Audio, PowerState, Calls Log,
        Texts Log, and Survey Response files. """
    patient_id = request.values['patient_id']
    uploaded_file = request.files['file']
    # werkzeug.secure_filename may return empty if unsecure
    # TODO: Josh? Kevin? what does it mean to be an insecure?
    file_name = secure_filename( uploaded_file.filename )
    if uploaded_file and file_name and allowed_extension( file_name ):
        file_type, timestamp  = parse_filename( file_name )

        if ANSWERS_TAG in file_type or TIMINGS_TAG in file_type:
            ftype, parsed_id = parse_filetype( file_type )

            if ftype.startswith( 'surveyAnswers' ):
                ftype = 'surveyAnswers'

            s3_filename = "%s/%s/%s/%s" % ( patient_id, ftype, parsed_id, timestamp )
            s3_upload_handler_file(s3_filename, uploaded_file)
        else:
            s3_upload_handler_file( file_name.replace("_", "/") , uploaded_file )
            #the same but with encryption.
            # data = decrypt_rsa_lines( uploaded_file.read(), patient_id )
            # s3_upload_handler_file( file_name.replace("_", "/") , data )
        return render_template('blank.html'), 200
    else:
        # Did not match any data upload files
        return abort(400)


# TODO: Dori.  Make sure android handling the different response codes correctly in android.
@mobile_api.route('/register_user', methods=['GET', 'POST'])
@authenticate_user_registration
def register_user():
    """ Checks that the patient id has been granted, and that there is no device
        registered with that id.  If the patient id has no device registered it
        registers this device and logs the bluetooth mac address.
        Returns the encryption key for this patient. """

    #Case: If the id and password combination do not match, the decorator returns
    # a 403 error.
    patient_id = request.values['patient_id']
    mac_address = request.values['bluetooth_id']
    user = User(patient_id)
    if user['device_id'] is not None:
        # Case: this patient has previously registered a device, 405 is the
        # "method not allowed" error, seems like a good response to me.
        return abort(405)
    upload_bluetooth(patient_id, mac_address)
    user.set_device( request.values['device_id'] )
    #Case: this device has been registered successfully, the return is the
    # encryption key associated with this user.
    return get_client_public_key_string(patient_id), 200


################################################################################
############################### USER FUNCTIONS #################################
################################################################################

@mobile_api.route('/set_password', methods=['GET', 'POST'])
# @authenticate_user
def set_password():
    User(request.values["patient_id"]).set_password(request.values["new_password"])
    return render_template('blank.html'), 200

################################################################################
############################ RELATED FUNCTIONALITY #############################
################################################################################

def upload_bluetooth( patient_id, mac_address ):
    """ Uploads the user's bluetooth mac address safely. """
    number_mac_addresses = len( s3_list_files(patient_id + '/mac' ) )
    s3_upload_handler_string(patient_id + '/mac_' + str(number_mac_addresses),
                             mac_address )

def parse_filename(filename):
    """ Splits filename into user-id, file-type, unix-timestamp. """
    name = filename.split("_")
    if len(name) == 3:
        return name[1], name[2]

def parse_filetype(file_type):
    """TODO: Josh/Dori.  Fill in this documentation line."""
    parsed_id = filter(str.isdigit, file_type)
    return filter(str.isalpha, file_type), parsed_id

def allowed_extension(filename):
    """ Checks if string has a recognized file extension. """
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
