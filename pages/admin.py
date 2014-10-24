from flask import Blueprint, request, send_file, render_template, redirect
from libs import admin_authentication
from libs.db_models import User, Users
from libs.s3 import s3_upload_handler_string
from libs.encryption import create_client_key_pair

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
    # Method responsible to authenticate researcher administrators.
    if request.method == 'POST':
        username = request.values["username"]
        password = request.values["password"]
        if admin_authentication.validate_login_credentials(password, username):
            admin_authentication.login_admin()
            return redirect("/admin_panel")
        return "Username password combination is incorrect. Try again."
    else:
        return redirect("/admin")


################################################################################
############################# The Admin Page ###################################
################################################################################

@admin.route('/admin_panel', methods=["GET", "POST"])
#@admin_authentication.authenticate_admin
def render_main():
    """ Method responsible rendering admin template"""
    patients = {user['_id']: patient_dict(user) for user in Users()}
    return render_template('admin_panel.html', patients = patients)


def patient_dict(patient):
    return {
        'placeholder_field': 'placeholder field for future data',
        'has_device': patient['device_id'] is not None
    }


################################################################################
######################### Actual Functionality #################################
################################################################################

#TODO: Josh/Dori/Eli. We need response pages (or some other way of telling the person
# that they have entered bad information)


#TODO: create route and response page.
@admin.route('/reset_patient_password', methods=["POST"])
# @admin_authentication.authenticate_admin
def reset_user_password():
    """ Takes a patient ID and resets its password. Returns the new random password."""
    patient_id = request.values["patient_id"]
    if User.exists(patient_id):
        user = User(patient_id)
        new_password = user.reset_password()
        user.set_password(new_password)
        return new_password
    return "that patient id does not exist"


#TODO: create route and response page.
@admin.route('/reset_device', methods=["POST"])
# @admin_authentication.authenticate_admin
def reset_device():
    patient_id = request.values["patient_id"]
    if User.exists(patient_id):
        user = User(patient_id)
        user.clear_device()
        return "device has been reset, password is untouched."
    return "that patient id does not exist"


#TODO: make this work with admin authentication
@admin.route('/create_new_patient', methods=["POST"])
# @admin_authentication.authenticate_admin
def create_new_patient():
    """ Creates a new user, generates a password and keys, pushes data to s3
    and user database, returns a string containing password and patient id"""
    patient_id, password = User.create()
    s3_upload_handler_string(patient_id, "")
    create_client_key_pair(patient_id)
    return "patient_id: " + patient_id + "\npassword: " + password


################################################################################
############################# Other Stuff ######################################
################################################################################

@admin.route("/download")
def download():
    """ Method responsible for distributing APK file of Android app"""
    return send_file("Beiwe.apk", as_attachment=True)
