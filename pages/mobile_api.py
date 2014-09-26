from flask import Blueprint, request, abort, jsonify, json, render_template
from werkzeug import secure_filename

from libs.data_handlers import get_weekly_results
from libs.db_models import User
from libs.encryption import check_client_key, get_client_public_key_string
from libs.security import generate_upper_case_alphanumeric_string
from libs.s3 import s3_upload_handler_file, s3_retrieve, s3_upload_handler_string
from libs.user_authentication import authenticate_user

from mongolia.errors import DatabaseConflictError

################################################################################
############################# GLOBALS... #######################################
################################################################################
mobile_api = Blueprint('mobile_api', __name__)

ALLOWED_EXTENSIONS = set(['csv', '3gp', 'json', 'mp4', 'txt'])
FILE_TYPES = ['gps', 'accel', 'voiceRecording', 'powerState', 'callLog', 'textLog',
              'bluetoothLog', 'surveyAnswers', 'surveyTimings']

ANSWERS_TAG = 'surveyAnswers'
TIMINGS_TAG = 'surveyTimings'

################################################################################
############################# ROUTES ###########################################
################################################################################

@mobile_api.route('/fetch_survey', methods=['GET', 'POST'])
# @authenticate_user
def fetch_survey():
    """ Method responsible for serving the latest survey JSON. """
    return s3_retrieve("all_surveys/current_survey")
    if request.method == 'POST':
        if request.values["magic"] == "12345":
            return jsonify(json.load(open("/var/www/scrubs/sample_survey.json"), 'rb'))


@mobile_api.route('/upload', methods=['POST'])
# @authenticate_user
def upload():
    """ Entry point to relay GPS, Accelerometer, Audio, PowerState, Calls Log,
        Texts Log, and Survey Response files. """
    uploaded_file = request.files['file']
    # werkzeug.secure_filename may return empty if unsecure
    file_name = secure_filename(uploaded_file.filename)
    if uploaded_file and file_name and allowed_extension(file_name):
        patient_id, file_type, timestamp  = parse_filename(file_name)
        if ANSWERS_TAG in file_type or TIMINGS_TAG in file_type:
            ftype, parsed_id = parse_filetype(file_type)
            if (ftype.startswith('surveyAnswers')):
                ftype = 'surveyAnswers'
            s3_prepped_filename = "%s/%s/%s/%s" % (patient_id, ftype, parsed_id, timestamp)
            s3_upload_handler_file(s3_prepped_filename, uploaded_file)
        else:
            s3_upload_handler_file(s3_prep_filename(file_name), uploaded_file)
        return'200'
    else:
        abort(400)


# TODO: Dori. check what the response codes from this is.
@mobile_api.route('/userinfo', methods=['GET', 'POST'])
# @authenticate_user
def set_user_info():
    """ Method for receiving and setting user info upon registration. """
    patient_id = request.values['patientID']
    android_id = request.values['android_id']
    bluetooth_id = request.values['btID']
    
    if User.exists( patient_id=patient_id ):
        s3_upload_handler_string( patient_id + '/ids.csv', android_id + '\n' + bluetooth_id)


@mobile_api.route('/valid_user', methods=['GET', 'POST'])
# @authenticate_user
def check_user_exists():
    patient_id = request.values['patientID']
    if User.exists( patient_id=patient_id ):
        return 200
    return 403


#TODO: Eli + Dori
# this should be a dynamic page, the url should look like "users/some-uuid/graph"
@mobile_api.route('/users/<patient_id>/graph', methods=['GET', 'POST'])
# @mobile_api.route('/graph', methods=['GET', 'POST'])
# @authenticate_user
def fetch_graph( patient_id ):
    data_results = []
#     results = [json.dumps(i) for i in get_weekly_results(username=userID)]
    results = get_weekly_results(username=patient_id)
    for pair in results:
        data_results.append([json.dumps(pair[0]), json.dumps(pair[1])])
    print results[0][1]
    return render_template("phone_graphs.html", data=results)


# TODO: Dori.  This registration url
@mobile_api.route('/register_user', methods=['GET', 'POST'])
# @authenticate_user
def register_user():
    patient_id = request.values["patient_id"]
    device_id = request.values["device_id"]
    
    #if a device is already registered with this patient_id, forbid.
    if User(patient_id) is not None:
        #TODO: Dori, change this code to something meaningful that you can
        # respond to on the Android side.
        return render_template('empty.html'), 403  
    
    # TODO: Eli/Dori.  Oops, we need to make the bluetooth database.
    
    #if the device id matches, then all is good and we return the user's public key
    return get_client_public_key_string(patient_id), 200


@mobile_api.route('/check_password', methods=['GET', 'POST'])
# @authenticate_user
def check_password_match():
    password = request.values['pwd']
    patient_id = request.values['patientID']
    if User.check_password( patient_id, password ):
        return render_template('blank.html'), 200
    return abort(403)

#TODO: Eli. modify after implementing user authentication.
#you will be given a randomly generated user id and password upon registration.
@mobile_api.route('/set_password', methods=['GET', 'POST'])
# @authenticate_user
def set_password():
    User(request.values["patient_id"]).set_password(request.values["new_password"])
    return render_template('blank.html'), 200

################################################################################
############################## test... #########################################
################################################################################

@mobile_api.route('/test_auth', methods=['GET', 'POST'])
@authenticate_user
def test_function():
    return render_template("blank.html"), 200

################################################################################
############################ RELATED FUNCTIONALITY #############################
################################################################################

def parse_filename(filename):
    """ Splits filename into user-id, file-type, unix-timestamp. """
    name = filename.split("_")
    if len(name) == 3:
        return name[0], name[1], name[2]


def parse_filetype(file_type):
    parsed_id = filter(str.isdigit, file_type)
    ftype = filter(str.isalpha, file_type)
    return ftype, parsed_id


def s3_prep_filename(filename):
    """ Preps a filename to become a S3 file path for prefix organization. """
    replacemnts = {"_": "/"}
    for k,v in replacemnts.iteritems():
        filename = filename.replace( k,v )
    return filename


def allowed_extension(filename):
    """ Method checks to see if uploaded file has filename that ends in an
        allowed extension. Does not verify content. """
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


# TODO: add a randomly-generate new user id.  User only needs to type in a user ID on device registration.
def create_new_user():
    try:
        User.create( generate_upper_case_alphanumeric_string )
    except DatabaseConflictError:
        create_new_user()
