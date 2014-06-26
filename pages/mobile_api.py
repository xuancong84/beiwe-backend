from flask import Blueprint, request, abort
from werkzeug import secure_filename
from utils.s3 import s3_upload_handler

mobile_api = Blueprint('mobile_api', __name__)

ALLOWED_EXTENSIONS = set(['csv', 'mp3'])

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def _upload(file_obj):
    if file_obj and allowed_file(file_obj.filename):
        s3_upload_handler(secure_filename(file_obj.filename), file_obj)

@mobile_api.route('/upload_gps/', methods=['GET', 'POST'])
def upload_gps():
    if request.method == 'POST':
        _upload(request.files['file'])
        #mongo_instance.save()
        return'200'

@mobile_api.route('/upload_accel/', methods=['GET', 'POST'])
def upload_accel():
    if request.method == 'POST':
        _upload(request.files['file'])
        #mongo_instance.save()
        return'200'

@mobile_api.route('/upload_powerstate/', methods=['GET', 'POST'])
def upload_powerstate():
    if request.method == 'POST':
        _upload(request.files['file'])
        #mongo_instance.save()
        return'200'

@mobile_api.route('/upload_calls/', methods=['GET', 'POST'])
def upload_calls():
    if request.method == 'POST':
        _upload(request.files['file'])
        #mongo_instance.save()
        return'200'

@mobile_api.route('/upload_texts/', methods=['GET', 'POST'])
def upload_texts():
    if request.method == 'POST':
        _upload(request.files['file'])
        #mongo_instance.save()
        return'200'

@mobile_api.route('/upload_surveyresponse/', methods=['GET', 'POST'])
def upload_surveyresponse():
    if request.method == 'POST':
        _upload(request.files['file'])
        #mongo_instance.save()
        return'200'

@mobile_api.route('/upload_audio/', methods=['GET', 'POST'])
def upload_audio():
    if request.method == 'POST':
        _upload(request.files['file'])
        #mongo_instance.save()
        return'200'
