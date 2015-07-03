from flask import (Blueprint, redirect, render_template, request, send_file,
                   session)
from libs import admin_authentication
from libs.admin_authentication import authenticate_admin_login
from db.user_models import User, Users, Admin
from libs.s3 import s3_upload, create_client_key_pair
from libs.encryption import encrypt_for_server
from db.study_models import Study

admin = Blueprint('admin', __name__)

################################################################################
############################# Login/Logoff #####################################
################################################################################

@admin.route('/')
@admin.route('/admin')
def render_login_page():
    if admin_authentication.is_logged_in():
        return redirect("/admin_panel")
    return render_template('admin_login.html')


@admin.route("/logout")
def logout():
    admin_authentication.logout_loggedin_admin()
    return redirect("/")


@admin.route("/validate_login", methods=["GET", "POST"])
def login():
    """ Authenticates administrator login, redirects to login page
        if authentication fails."""
    if request.method == 'POST':
        username = request.values["username"]
        password = request.values["password"]
        if Admin.check_password(username, password):
            admin_authentication.log_in_admin(username)
            return redirect("/admin_panel")
        return "Username password combination is incorrect. Try again."
    else:
        return redirect("/admin")


@admin.route('/reset_admin_password_form')
@authenticate_admin_login
def render_reset_admin_password_form():
    return render_template('reset_admin_password.html')

@admin.route('/reset_admin_password', methods=['POST'])
@authenticate_admin_login
def reset_admin_password():
    username = session['admin_username']
    current_password = request.values['current_password']
    new_password = request.values['new_password']
    confirm_new_password = request.values['confirm_new_password']
    if not Admin.check_password(username, current_password):
        return 'The "Current Password" you entered is invalid'
    if new_password != confirm_new_password:
        return 'New Password does not match Confirm New Password'
    Admin(username).set_password(new_password)
    return redirect('/')


################################################################################
############################# The Admin Page ###################################
################################################################################
#TODO: josh/alvin: replace use of this function/url with the new implementation, see the todo below.
@admin.route('/admin_panel', methods=["GET", "POST"])
@authenticate_admin_login
def render_main():
    """ Method responsible rendering admin template"""
    patients = {user['_id']: patient_dict(user) for user in Users()}
    return render_template('admin_panel.html', patients = patients)
 
def patient_dict(patient):
    return {'placeholder_field': 'placeholder field for future data',
            'has_device': patient['device_id'] is not None }

"""TODO: josh/alvin: this function provides the admin with users in the studies
they have access to, it is not used anywhere. Probably this can be on the front 
page for the site. """
#@admin.route('admin_panel') #maybe.
@authenticate_admin_login
def render_surveys():
    """Provides a dict of studies that the current admin has access to by study
    to a flask template."""
    studies = Study.get_studies_for_admin(session['admin_username'])
    users_by_study = {}
    for study in studies:
        users_by_study[study.name] = study.get_participants_in_study()
    return render_template('SOME_PAGE.PROBABLY_HTML', users_by_study=users_by_study)



################################################################################
######################### Actual Functionality #################################
################################################################################
#TODO: Eli. does this need update for new db schema?
@admin.route('/reset_patient_password', methods=["POST"])
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

#TODO: Eli. does this need update for new db schema?
@admin.route('/reset_device', methods=["POST"])
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

#TODO: Eli. update this to create new user and add to them to a specific study.
@admin.route('/create_new_patient', methods=["POST"])
@authenticate_admin_login
def create_new_patient():
    """ Creates a new user, generates a password and keys, pushes data to s3
    and user database, returns a string containing password and patient id"""
    patient_id, password = User.create()
    s3_upload(patient_id, "")
    create_client_key_pair(patient_id)
    return "patient_id: " + patient_id + "\npassword: " + password


################################################################################
############################# Other Stuff ######################################
################################################################################

@admin.route("/download")
def download():
    """ Method responsible for distributing APK file of Android app"""
    return send_file("Beiwe.apk", as_attachment=True)

#TODO: Eli. this is part of the download script (maybe), find and purge.
# @admin.route("/user_list")
# def get_user_list():
#     all_users = ""
#     for user in Users():
#         all_users += user['_id'] + ','
#     return encrypt_for_server( all_users[:-1] )
