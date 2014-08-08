from flask import Blueprint, request, abort, jsonify, json
from werkzeug import secure_filename
from utils.s3 import s3_upload_handler, list_s3_files, s3_retrieve

mobile_api = Blueprint('mobile_api', __name__)

ALLOWED_EXTENSIONS = set(['csv', '3gp', 'json', 'mp4', 'txt'])
FILE_TYPES = ['gps', 'accel', 'voiceRecording', 'powerState', 'callsLog', 'textsLog', \
              'bluetoothLog', 'surveyAnswers', 'surveyTimings']


@mobile_api.route('/login_user', methods=['GET', 'POST'])
def login_or_register_user():
    """
    Web app on server is responsible for relaying and storing password information, as well as checking
    password match upon future login attempts, and given a successful match, redirects to another web page which a user
    see's a list and graph of past survey responses.
    """
    user_id = request.values["username"]
    password = request.values["password"]
    #TODO:
    # 1. check if user with user_id already exists
    # 2. if not, create user to store user password
    # 3. if yes, check if password matches
    # 4. if match, authenticate user
    # 5. if not match, return error message
    if password == "test": #example hardcoded password
        return render_user_panel(user_id)
    else:
        return "User Password combination not found"

def fetch_user_responses(user_id):
    """
    TODO: untested
    """
    all_responses = {}
    list_of_s3names = list_s3_files(user_id + 'surveyResponses')
    for l in list_of_s3names:
        all_responses["l"] = s3_retrieve(l)
    return all_responses

@mobile_api.route('/<user_id>', methods=['GET', 'POST'])
#@auth.authenticated() TODO to make authenticated on user level
def render_user_panel(user_id):
    responses = fetch_user_responses(user_id)
    return jsonify(responses)
    #TODO:
    # 1. Fetch all files related to user_id in S3
    # 2. Render list of contents
    # 3. Render graph if applicable

@mobile_api.route('/fetch_survey', methods=['GET', 'POST'])
def fetch_survey():
    f = open("/var/www/scrubs/sample_survey.json", 'rb')
    return jsonify(json.load(f))
    if request.method == 'POST':
        if request.values["magic"] == "12345":
            return jsonify(json.load(open("/var/www/scrubs/sample_survey.json"), 'rb'))
    else:
        return

def parse_filetype(filename):
    """Splits filename into user-id, file-type, unix-timestamp"""
    l = filename.split("_")
    if len(l) == 3:
        return l[0], l[1], l[2]

def s3_prep_filename(filename):
    replacemnts = {"_": "/"}
    for k,v in replacemnts.iteritems():
        filename = filename.replace(k,v )
    return filename


def allowed_extension(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@mobile_api.route('/upload', methods=['POST'])
def upload():
    """
    Entry point to relay GPS, Accelerometer, Audio, PowerState, Calls Log, Texts Log, and Survey Response files.
    """
    uploaded_file = request.files['file']
    #Method werkzeug.secure_filename may return empty if unsecure
    file_name = secure_filename(upload.filename)
    if uploaded_file and file_name and allowed_extension(file_name):
        s3_upload_handler(s3_prep_filename(file_name), uploaded_file)
#         user_id, file_type, timestamp  = parse_filetype(file_name)
#         if "surveyAnswers" in filetype or "surveyTimings" in filetype:
#             mongo_survey_response_instance.save(user_id, timestamp, uploaded_file.read())
        return'200'
    else:
        abort(400)