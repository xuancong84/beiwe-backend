from flask import Blueprint, request, abort
from werkzeug import secure_filename
from s3 import s3_upload_handler

mobile_api = Blueprint('mobile_api', __name__)

@mobile_api.route('/upload_gps/')
def upload_gps():
    if request.method == 'POST':
        file_obj = request.files['file']
        s3_upload_handler(secure_filename(file_obj.filename), file_obj)
        #mongo_instance.save()

@mobile_api.route('/upload_accel/')
def upload_accel():
    if request.method == 'POST':
        file_obj = request.files['file']
        s3_upload_handler(secure_filename(file_obj.filename), file_obj)
        #mongo_instance.save()

@mobile_api.route('/upload_powerstate/')
def upload_powerstate_log():
    if request.method == 'POST':
        file_obj = request.files['file']
        s3_upload_handler(secure_filename(file_obj.filename), file_obj)
        #mongo_instance.save()

@mobile_api.route('/upload_call/')
def upload_call():
    if request.method == 'POST':
        file_obj = request.files['file']
        s3_upload_handler(secure_filename(file_obj.filename), file_obj)
        #mongo_instance.save()

@mobile_api.route('/upload_texts/')
def upload_texts():
    if request.method == 'POST':
        file_obj = request.files['file']
        s3_upload_handler(secure_filename(file_obj.filename), file_obj)
        #mongo_instance.save()

@mobile_api.route('/upload_surveyresponse/')
def upload_surveyresponse():
    if request.method == 'POST':
        file_obj = request.files['file']
        s3_upload_handler(secure_filename(file_obj.filename), file_obj)
        #mongo_instance.save()

@mobile_api.route('/upload_audio/')
def upload_audio():
    if request.method == 'POST':
        file_obj = request.files['file']
        s3_upload_handler(secure_filename(file_obj.filename), file_obj)
        #mongo_instance.save()

