from flask import Blueprint, request, abort, jsonify, json, render_template
from werkzeug import secure_filename
from utils.s3 import s3_upload_handler_file, list_s3_files, s3_retrieve,\
    s3_upload_handler_string
from utils.data_manipulations import get_weekly_results
from utils.encryption import check_client_key

mobile_api = Blueprint('mobile_api', __name__)

ALLOWED_EXTENSIONS = set(['csv', '3gp', 'json', 'mp4', 'txt'])
FILE_TYPES = ['gps', 'accel', 'voiceRecording', 'powerState', 'callLog', 'textLog', \
              'bluetoothLog', 'surveyAnswers', 'surveyTimings']

ANSWERS_TAG = 'surveyAnswers'
TIMINGS_TAG = 'surveyTimings'

#TODO: Eli/Dori.  correctly receive data from device.

#notes:
# a return without a value results in a 200 OK HTTP response

@mobile_api.route('/register_user', methods=['GET', 'POST'])
def register_user():
    user_id = request.values["user_id"]
    #check if user_id is a valid, registerable user_id.

    #if a client key already exists, the user cannot register a device (403 forbidden)
    if check_client_key(user_id):
        return 403
    #if the client does not already


def verify_user(user_id):
    pass


@mobile_api.route('/login_user', methods=['GET', 'POST'])
def login_user():
    #TODO: Eli.
    """ Spec: Web app on server is responsible for relaying and storing password
        information, as well as checking password match upon future login attempts,
        and given a successful match, redirects to another web page which a user
        see's a list and graph of past survey responses. """
    user_id = request.values["user_id"]
    password = request.values["password"]
    #TODO: Eli
    # 1. check if user with user_id already exists
    # 2. if not, create user to store user password
    # 3. if yes, check if password matches
    # 4. if match, authenticate user
    # 5. if not match, return error message
    if password == "test": #example hardcoded password
        return render_user_panel(user_id)
    else:
        return "User Password combination not found"


@mobile_api.route('/<user_id>', methods=['GET', 'POST'])
#@auth.authenticated #TODO to make authenticated on user level
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
    list_of_s3names = list_s3_files(user_id + 'surveyResponses')
    for l in list_of_s3names:
        all_responses["l"] = s3_retrieve(l)
    return all_responses


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
        filename = filename.replace(k,v )
    return filename


def allowed_extension(filename):
    """ Method checks to see if uploaded file has filename that ends in an allowed extension. Does not verify content. """
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@mobile_api.route('/upload', methods=['POST'])
def upload():
    """ Entry point to relay GPS, Accelerometer, Audio, PowerState, Calls Log, Texts Log, and Survey Response files. """
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


@mobile_api.route('/userinfo', methods=['GET', 'POST'])
def get_user_info():
    """ Method for receiving user info upon registration """
    userID = request.values['patientID']
    droidID = request.values['droidID'].decode('utf-8')
    bluetoothID = request.values['btID'].decode('utf-8')
    print (userID + droidID + bluetoothID)
    # FIXME: Dori/Eli. This is for debug purposes only, until the database goes on!
    if (check_user_exists(userID)):
        return 'Exists'
    else:
        s3_upload_handler_string(userID + '/ids.csv', droidID + ',' + bluetoothID)
        return 'Not_Exists'

def check_user_exists(userID):
    return (len(list_s3_files(userID + '/')) > 0)

#TODO: Eli + Dori
# this should be a dynamic page, the url should look like "/uuid/graph"
# @mobile_api.route('/users/<int:userid>/')
# def graph(userid):

@mobile_api.route('/graph', methods=['GET', 'POST'])
def fetch_graph():
    userID = request.values['patientID']
    password = request.values['pwd']
    results = [json.dumps(i) for i in get_weekly_results(username=userID)]
    print results
    return render_template("phone_graphs.html", data=results)


#FIXME: Eli. this is debug code.
@mobile_api.route('/fetch_key', methods=['GET', 'POST'])
def fetch_key():
    return open("/var/www/scrubs/keyFile", 'rb').read()


#fixme: implement
@mobile_api.route('/<int:user_id>/key', methods=['GET', 'POST'])
def get_key():
    pass

#TODO: Eli, I (Josh) need a function called /update_survey
# I want to send a POST or GET request to it that has a long (~1kb) string of JSON
# I want it to save the current survey.json file (right now it's sample_survey.json on the server)
# as an older version (maybe timestamped or something)
# And then I want it to overwrite the survey.json file with the string I pass it.
# I'm not sure where the survey.json file will be; I think Kevin wanted it to be a file on S3.
