from flask import Blueprint, request, abort, jsonify, json, render_template
from werkzeug import secure_filename
from libs.s3 import s3_upload_handler_file, s3_list_files, s3_retrieve,\
    s3_upload_handler_string
from libs.data_handlers import get_weekly_results
from libs.encryption import check_client_key

mobile_api = Blueprint('mobile_api', __name__)

################################################################################
############################# GLOBALS ##########################################
################################################################################

ALLOWED_EXTENSIONS = set(['csv', '3gp', 'json', 'mp4', 'txt'])
FILE_TYPES = ['gps', 'accel', 'voiceRecording', 'powerState', 'callLog', 'textLog', \
              'bluetoothLog', 'surveyAnswers', 'surveyTimings']

ANSWERS_TAG = 'surveyAnswers'
TIMINGS_TAG = 'surveyTimings'

################################################################################
############################# ROUTES ###########################################
################################################################################

@mobile_api.route('/fetch_survey', methods=['GET', 'POST'])
def fetch_survey():
    """ Method responsible for serving the latest survey JSON. """
    f = open("/var/www/scrubs/sample_survey.json", 'rb')
    return jsonify(json.load(f))
    if request.method == 'POST':
        if request.values["magic"] == "12345":
            return jsonify(json.load(open("/var/www/scrubs/sample_survey.json"), 'rb'))
    else:
        return


@mobile_api.route('/upload', methods=['POST'])
def upload():
    """ Entry point to relay GPS, Accelerometer, Audio, PowerState, Calls Log,
        Texts Log, and Survey Response files. """
    uploaded_file = request.files['file']
    #Method werkzeug.secure_filename may return empty if unsecure
    file_name = secure_filename(uploaded_file.filename)
    if uploaded_file and file_name and allowed_extension(file_name):
        user_id, file_type, timestamp  = parse_filename(file_name)
        if ANSWERS_TAG in file_type or TIMINGS_TAG in file_type:
            ftype, parsed_id = parse_filetype(file_type)
            s3_prepped_filename = "%s/%s/%s/%s" % (user_id, ftype, parsed_id, timestamp)
            s3_upload_handler_file(s3_prepped_filename, uploaded_file)
            #mongo_survey_response_instance.save(user_id, timestamp, uploaded_file.read())
        else:
            s3_upload_handler_file(s3_prep_filename(file_name), uploaded_file)
        return'200'
    else:
        abort(400)


# FIXME: Dori/Eli. DEBUG until the user data storage is finished, and we have a
# way of getting and storing user ids safely.
@mobile_api.route('/userinfo', methods=['GET', 'POST'])
def get_user_info():
    """ Method for receiving user info upon registration """
    userID = request.values['patientID']
    droidID = request.values['droidID']
    bluetoothID = request.values['btID']
    # TODO: Dori. Check if legal username function goes here
    print userID + "\n" + droidID + "\n" + bluetoothID
    if (check_user_exists(userID)):
        return 'Exists'
    else:
        s3_upload_handler_string(userID + '/ids.csv', droidID + ',' + bluetoothID)
        return 'Not_Exists'

#, methods=['GET', 'POST']

#TODO: Eli + Dori
# this should be a dynamic page, the url should look like "users/some-uuid/graph"
# @mobile_api.route('/users/<user_id>/graph', methods=['GET', 'POST'])
@mobile_api.route('/graph')
def fetch_graph():
#     userID = request.values['patientID']
#     password = request.values['pwd']
#     results = [json.dumps(i) for i in get_weekly_results(username=userID)]
    return render_template("phone_graphs.html")#, data=results)


#TODO: Eli, I (Josh) need a function called /update_survey
# I want to send a POST or GET request to it that has a long (~1kb) string of JSON
# I want it to save the current survey.json file (right now it's sample_survey.json on the server)
# as an older version (maybe timestamped or something)
# And then I want it to overwrite the survey.json file with the string I pass it.
# I'm not sure where the survey.json file will be; I think Kevin wanted it to be a file on S3.
import libs.s3 as s3
from datetime import datetime
@mobile_api.route('/update_survey', methods=['GET', 'POST'])
def update_survey():
    #TODO: Josh. stick in the identifier for the field(?) to grab from the post request.
    # you will probably need to write the post request before you can answer this question.
    new_quiz = request.values("whatever-it-is-that-josh-supplies-as-a-label-in-the-post-request")
    s3.s3_copy_with_new_name("survey", "survey." + datetime.now().isoformat() )
    s3.s3_upload_handler_string("survey", new_quiz)


#FIXME: Eli. this is currently debug code, need to store/fetch keys on s3
@mobile_api.route('/fetch_key', methods=['GET', 'POST'])
def fetch_key():
    return open("/var/www/scrubs/keyFile", 'rb').read()


#fixme: Eli. implement
@mobile_api.route('/<user_id>/key', methods=['GET', 'POST'])
def get_key():
    pass


#TODO: Eli/Dori. implement user registration.
# note: a return statment without a value results in a 200 OK HTTP response.
@mobile_api.route('/register_user', methods=['GET', 'POST'])
def register_user():
    user_id = request.values["user_id"]
    #check if user_id is a valid, registerable user_id.

    #if a client key already exists, the user cannot register a device (403 forbidden)
    if check_client_key(user_id):
        return 403
    #if the client does not have a key


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


def check_user_exists(userID):
    return (len(s3_list_files(userID + '/')) > 0)


################################################################################
############################## TO BE DEPRECATED ################################
################################################################################

@mobile_api.route('/<user_id>', methods=['GET', 'POST'])
#@admin_authentication.authenticated
#TODO: Kevin.  I'm pretty sure we don't have this kind of user authentication.
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