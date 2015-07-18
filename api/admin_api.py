from flask import abort, Blueprint, redirect, request, send_file
from libs.admin_authentication import authenticate_admin_study_access,\
    authenticate_admin_login, authenticate_system_admin
from db.user_models import User, Admin
from db.study_models import Study, Studies
from bson.objectid import ObjectId
from libs.s3 import s3_upload, create_client_key_pair

admin_api = Blueprint('admin_api', __name__)


"""######################### Study Administration ###########################"""

@admin_api.route('/add_admin_to_study', methods=['POST'])
@authenticate_system_admin
def add_admin_to_study():
    admin = Admin(request.form.get('admin_id'))
    study = Study(ObjectId(request.form.get('study_id')))
    study.add_admin(admin._id)
    return '200'


@admin_api.route('/remove_admin_from_study', methods=['POST'])
@authenticate_system_admin
def remove_admin_from_study():
    admin = Admin(request.form.get('admin_id'))
    study = Study(ObjectId(request.form.get('study_id')))
    study.remove_admin(admin._id)
    return '200'


@admin_api.route('/delete_researcher/<string:admin_id>', methods=['GET','POST'])
@authenticate_system_admin
def delete_researcher(admin_id):
    admin = Admin(admin_id)
    if not admin:
        return abort(404)
    for study in Studies():
        study.remove_admin(admin_id)
    admin.remove()
    return redirect('/manage_admins')


@admin_api.route('/set_researcher_password', methods=['POST'])
@authenticate_system_admin
def set_researcher_password():
    admin = Admin(request.form.get('admin_id'))
    new_password = request.form.get('password')
    admin.set_password(new_password)
    return redirect('/edit_admin/' + admin._id)


"""########################## User Administration ###########################"""

@admin_api.route('/reset_patient_password', methods=["POST"])
@authenticate_admin_login
def reset_user_password():
    """ Takes a patient ID and resets its password. Returns the new random password."""
    patient_id = request.values["patient_id"]
    if User.exists(patient_id):
        user = User(patient_id)
        new_password = user.reset_password()
        user.set_password(new_password)
        return new_password
    return "that patient id does not exist"


@admin_api.route('/reset_device', methods=["POST"])
@authenticate_admin_login
def reset_device():
    """ Resets a patient's device.  The patient will not be able to connect
        until expect to register a new device. """
    patient_id = request.values["patient_id"]
    if User.exists(patient_id):
        user = User(patient_id)
        user.clear_device()
        return "device has been reset, password is untouched."
    return "that patient id does not exist"


@admin_api.route('/create_new_patient/<string:study_id>', methods=["POST"])
@authenticate_admin_study_access
def create_new_patient(study_id=None):
    """ Creates a new user, generates a password and keys, pushes data to s3
    and user database, adds user to the study they are supposed to be attached
    to, returns a string containing password and patient id. """
    patient_id, password = User.create()
    Study(study_id).add_participant(patient_id)
    s3_upload(patient_id, "", study_id)
    create_client_key_pair(patient_id, study_id)
    return "patient_id: " + patient_id + "\npassword: " + password


"""########################## Other Stuff ###################################"""

@admin_api.route("/download")
def download():
    """ Method responsible for distributing APK file of Android app"""
    return send_file("Beiwe.apk", as_attachment=True)

#TODO: Eli. this is part of the download script (maybe), find and purge.
# @admin_api.route("/user_list")
# def get_user_list():
#     all_users = ""
#     for user in Users():
#         all_users += user['_id'] + ','
#     return encrypt_for_server( all_users[:-1] )
