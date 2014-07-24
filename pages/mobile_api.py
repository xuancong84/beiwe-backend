from flask import Blueprint, request, abort, jsonify, json
from werkzeug import secure_filename
from utils.s3 import s3_upload_handler

mobile_api = Blueprint('mobile_api', __name__)

ALLOWED_EXTENSIONS = set(['csv', '3gp', 'json', 'mp4', 'txt'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def _upload(file_obj):
    if file_obj and allowed_file(file_obj.filename):
        s3_upload_handler(secure_filename(file_obj.filename), file_obj)

def fetch_user_responses(user_id):
    pass

@mobile_api.route('/login_user', methods=['GET', 'POST'])
def login_or_register_user():
    """
        Documentation goes here. Web app on server is responsible for relaying and storing password information, as well as checking
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

@mobile_api.route('/upload_gps', methods=['GET', 'POST'])
def upload_gps():
    if request.method == 'POST' and request.files['file']:
        _upload(request.files['file'])
        #mongo_instance.save()
        return'200'
    else:
        abort(400)

@mobile_api.route('/upload_accel', methods=['GET', 'POST'])
def upload_accel():
    if request.method == 'POST' and request.files['file']:
        _upload(request.files['file'])
        #mongo_instance.save()
        return'200'
    else:
        abort(400)

@mobile_api.route('/upload_powerstate', methods=['GET', 'POST'])
def upload_powerstate():
    if request.method == 'POST' and request.files['file']:
        _upload(request.files['file'])
        #mongo_instance.save()
        return'200'
    else:
        abort(400)

@mobile_api.route('/upload_calls', methods=['GET', 'POST'])
def upload_calls():
    if request.method == 'POST' and request.files['file']:
        _upload(request.files['file'])
        #mongo_instance.save()
        return'200'
    else:
        abort(400)

@mobile_api.route('/upload_texts', methods=['GET', 'POST'])
def upload_texts():
    if request.method == 'POST' and request.files['file']:
        _upload(request.files['file'])
        #mongo_instance.save()
        return'200'
    else:
        abort(400)

@mobile_api.route('/upload_surveyresponse', methods=['GET', 'POST'])
def upload_surveyresponse():
    if request.method == 'POST' and request.files['file']:
        _upload(request.files['file'])
        #mongo_instance.save()
        return'200'
    else:
        abort(400)

@mobile_api.route('/upload_audio', methods=['GET', 'POST'])
def upload_audio():
    if request.method == 'POST' and request.files['file']:
        _upload(request.files['file'])
        #mongo_instance.save()
        return'200'
    else:
        abort(400)
