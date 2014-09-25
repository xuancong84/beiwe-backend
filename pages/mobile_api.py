from flask import Blueprint, request, abort, jsonify, json, render_template, redirect
from werkzeug import secure_filename

from libs.data_handlers import get_weekly_results
from libs.db_models import User
from libs.encryption import check_client_key, get_client_public_key_string
from libs.security import generate_random_user_id
from libs.s3 import (s3_upload_handler_file, s3_list_files, s3_retrieve,
                     s3_upload_handler_string)

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
def fetch_survey():
    """ Method responsible for serving the latest survey JSON. """
    return s3_retrieve("all_surveys/current_survey")
    if request.method == 'POST':
        if request.values["magic"] == "12345":
            return jsonify(json.load(open("/var/www/scrubs/sample_survey.json"), 'rb'))


@mobile_api.route('/upload', methods=['POST'])
def upload():
    """ Entry point to relay GPS, Accelerometer, Audio, PowerState, Calls Log,
        Texts Log, and Survey Response files. """
    uploaded_file = request.files['file']
    # werkzeug.secure_filename may return empty if unsecure
    file_name = secure_filename(uploaded_file.filename)
    if uploaded_file and file_name and allowed_extension(file_name):
        user_id, file_type, timestamp  = parse_filename(file_name)
        if ANSWERS_TAG in file_type or TIMINGS_TAG in file_type:
            ftype, parsed_id = parse_filetype(file_type)
            if (ftype.startswith('surveyAnswers')):
                ftype = 'surveyAnswers'
            s3_prepped_filename = "%s/%s/%s/%s" % (user_id, ftype, parsed_id, timestamp)
            s3_upload_handler_file(s3_prepped_filename, uploaded_file)
        else:
            s3_upload_handler_file(s3_prep_filename(file_name), uploaded_file)
        return'200'
    else:
        abort(400)


# FIXME: Eli. I beleive this is the beginning of the user authentication code.
# TODO: Dori. check what the response codes from this is.
@mobile_api.route('/userinfo', methods=['GET', 'POST'])
# @user auth...
def set_user_info():
    """ Method for receiving and setting user info upon registration. """
    user_id = request.values['patientID']
    android_id = request.values['android_id']
    bluetooth_id = request.values['btID']

    if User.exists( patient_id=user_id ):
        s3_upload_handler_string( user_id + '/ids.csv', android_id + '\n' + bluetooth_id)


@mobile_api.route('/valid_user', methods=['GET', 'POST'])
def check_user_exists():
    user_id = request.values['patientID']
    if User.exists( patient_id=user_id ):
        return 200
    return 403


#TODO: Eli + Dori
# this should be a dynamic page, the url should look like "users/some-uuid/graph"
@mobile_api.route('/users/<user_id>/graph', methods=['GET', 'POST'])
# @mobile_api.route('/graph', methods=['GET', 'POST'])
def fetch_graph( user_id ):
#     userID = request.values['patientID']
#     password = request.values['pwd']
    data_results = []
#     results = [json.dumps(i) for i in get_weekly_results(username=userID)]
    results = get_weekly_results(username=user_id)
    for pair in results:
        data_results.append([json.dumps(pair[0]), json.dumps(pair[1])])
    print results[0][1]
    return render_template("phone_graphs.html", data=results)


#TODO: Eli. implement user registration.
@mobile_api.route('/register_user', methods=['GET', 'POST'])
def register_user():
    user_id = request.values["user_id"]
    #check if user_id is a valid, registerable user_id.

    #if a client key already exists, the user cannot register a device (403 forbidden)
    if check_client_key(user_id):
        return 403
    #if the client does not have a key

    # register cases
    # id valid, no existing device
    # id valid, there is already an existing device
    # id invalid


@mobile_api.route('/check_password', methods=['GET', 'POST'])
def check_password_match():
    password = request.values['pwd']
    patient_id = request.values['patientID']
    if User.check_password( patient_id, password ):
        return 200
    return 403

#TODO: Eli. modify after implementing user authentication.
#should you be given a user id and passwor on registration, or do you create your password?
#(yes)
@mobile_api.route('/set_password', methods=['GET', 'POST'])
def set_password():
    old_password = request.values['pwd']
    patient_id = request.values['patientID']
    new_password = request.valuse('new_pwd')

    if User.check_password(patient_id, old_password):
        User(patient_id).set_password(new_password)
        return 200
    return 403

################################################################################

#TODO: Eli. deprecate
@mobile_api.route('/fetch_key', methods=['GET', 'POST'])
def fetch_key():
    return open("/var/www/scrubs/keyFile", 'rb').read()

#TODO: Eli. move fully over to get_key once real keys exist.
@mobile_api.route('/<user_id>/key', methods=['GET', 'POST'])
def get_key(user_id):
    return get_client_public_key_string( user_id )


################################################################################

from libs.user_authentication import authenticated
@mobile_api.route('/test_auth', methods=['GET', 'POST'])
@authenticated
def test_function():
    print 'this line was printed from inside the test function'
    return redirect("/")
################################################################################
############################ RELATED FUNCTIONALITY #############################
################################################################################

def parse_filename(filename):
    """ Splits filename into user-id, file-type, unix-timestamp """
    l = filename.split("_")
    if len(l) == 3:
        return l[0], l[1], l[2]


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


# TODO: Eli.  Implement... currently unsure how to do this...
def verify_user(user_id):
    pass


# TODO: add a randomly-generate new user id.  User only needs to type in a user ID on device registration.
def create_new_user():
    try:
        User.create( generate_random_user_id )
    except DatabaseConflictError:
        create_new_user()

################################################################################
############################## TO BE DEPRECATED ################################
################################################################################

@mobile_api.route('/<user_id>', methods=['GET', 'POST'])
#@admin_authentication.authenticated
#FIXME: Eli/Kevin.  set up user authentication?

def render_user_panel(user_id):
    """ Method displays user information. """
    responses = fetch_user_responses(user_id)
    return jsonify(responses)
    #TODO: Dori
    # 1. Fetch all files related to user_id in S3
    # 2. Render list of contents
    # 3. Render graph if applicable


# Deprecate - This is received by the fetch_graph function
def fetch_user_responses(user_id):
    """ Method fetches a user's survey responses. """
    #TODO: Dori. untested, old, test and update
    all_responses = {}
    list_of_s3_names = s3_list_files(user_id + 'surveyResponses')
    for l in list_of_s3_names:
        all_responses["l"] = s3_retrieve(l)
    return all_responses
