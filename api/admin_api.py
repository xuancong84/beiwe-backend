from flask import abort, Blueprint, redirect, render_template, request, send_file
from libs.admin_authentication import authenticate_admin_study_access,\
    authenticate_admin_login, authenticate_system_admin
from db.user_models import User, Admin
from db.study_models import Study, Studies, InvalidEncryptionKeyError,\
    StudyAlreadyExistsError
from bson.objectid import ObjectId
from libs.s3 import s3_upload, create_client_key_pair
from libs.http_utils import checkbox_to_boolean, combined_multi_dict_to_dict
from config.constants import CHECKBOX_TOGGLES

admin_api = Blueprint('admin_api', __name__)


"""######################### Study Administration ###########################"""

@admin_api.route('/create_new_study', methods=["POST"])
@authenticate_system_admin
def create_new_study():
    try:
        study = Study.create_new_survey(request["name"], request["encryption_key"])
    except InvalidEncryptionKeyError:
        #TODO: Josh/Alvin.  create an error display/page for the following
        return render_template("some error display for invalid encryption key")
    except StudyAlreadyExistsError:
        #TODO: Josh/Alvin.  create an error display/page for the following
        return render_template("some error display for study of that name already exists")
    return redirect("/edit_study_device_settings/" + str(study._id))


@admin_api.route('/submit_device_settings/<string:study_id>', methods=["POST"])
@authenticate_system_admin
@authenticate_admin_study_access
def submit_device_settings(study_id=None):
    study = Study(ObjectId(study_id))
    settings = study.get_study_device_settings()
    params = combined_multi_dict_to_dict( request.values )
    params = checkbox_to_boolean(CHECKBOX_TOGGLES, params)
    settings.update(**params)
    #TODO: Alvin.  make this do something more user friendly than reload the page
    return redirect("/edit_study_device_settings/" + str(study._id) )


@admin_api.route('/add_researcher_to_study', methods=['GET', 'POST'])
@authenticate_system_admin
def add_researcher_to_study():
    admin = Admin(request.args.get('admin_id'))
    study = Study(ObjectId(request.args.get('study_id')))
    study.add_admin(admin._id)
    return redirect('/edit_admin/' + admin._id)


@admin_api.route('/remove_researcher_from_study', methods=['GET', 'POST'])
@authenticate_system_admin
def remove_researcher_from_study():
    admin = Admin(request.args.get('admin_id'))
    study = Study(ObjectId(request.args.get('study_id')))
    study.remove_admin(admin._id)
    return redirect('/edit_admin/' + admin._id)


@admin_api.route('/delete_researcher/<string:admin_id>', methods=['GET','POST'])
@authenticate_system_admin
def delete_researcher(admin_id):
    admin = Admin(admin_id)
    if not admin:
        return abort(404)
    for study in Studies():
        study.remove_admin(admin)
    admin.remove()
    return redirect('/manage_admins')


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
    Study(ObjectId(study_id)).add_participant(patient_id)
    s3_upload(patient_id, "", study_id)
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
