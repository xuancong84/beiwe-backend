from flask import request
from libs.admin_authentication import authenticate_admin_study_access,\
    authenticate_admin_login, authenticate_sysadmin
from flask.blueprints import Blueprint
from db.user_models import User
from db.study_models import Study, InvalidEncryptionKeyError, Studies,\
    StudyAlreadyExistsError
from bson.objectid import ObjectId
from libs.s3 import s3_upload, create_client_key_pair
from flask.helpers import send_file
from flask.templating import render_template
from django.shortcuts import redirect

admin_api = Blueprint('admin_api', __name__)

#TODO: Josh/Alvin. New studies need an error display function, i.e. invalid password.

"""###################### Actual Functionality ##############################"""

@admin_api.route('/create_new_study', methods=["POST"])
@authenticate_sysadmin
def create_new_study():
    try:
        study = Study.create_new_survey(request["name"], request["encryption_key"])
    except InvalidEncryptionKeyError:
        return render_template("some error display for invalid encryption key")
    except StudyAlreadyExistsError:
        return render_template("some error display for study of that name already exists")
    #survey created! redirect to study device settings? sure.
    return redirect("/edit_study_device_settings/" + str(study._id))


@admin_api.route('/submit_device_settings/<string:study_id>', methods=["POST"])
#TODO: Eli. Architecture. Ensure we can use both decorators at the same time.
@authenticate_sysadmin
@authenticate_admin_study_access
def submit_edit_device_settings(study_id=None):
    study = Studies(_id=ObjectId(study_id))
    settings = study.get_study_device_settings()
    #TODO: Eli/Josh. it is Exceedingly unlikely this little hack will work correctly... test.  :D
    settings.update(**request.values)
    settings.save() #TODO: Eli. is this even necessary?
    #reload page? sure.
    return redirect("/edit_study_device_settings/" + study._id)


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


""""TODO: Alvin/Josh. redirect any url in html or javascript that points at 
/create_new_patient to point at create_new_patient/*study id* """
@admin_api.route('/create_new_patient/<string:study_id>', methods=["POST"])
@authenticate_admin_study_access
def create_new_patient(study_id=None):
    """ Creates a new user, generates a password and keys, pushes data to s3
    and user database, adds user to the study they are supposed to be attached
    to, returns a string containing password and patient id. """
    patient_id, password = User.create()
    Study(ObjectId(study_id)).add_participant(patient_id)
    s3_upload(patient_id, "")
    create_client_key_pair(patient_id)
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
