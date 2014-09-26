from flask import Blueprint, request, send_file, render_template, redirect
from libs import admin_authentication
from libs.db_models import User
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
######################### Actual Functionality #################################
################################################################################

@admin.route('/admin_panel', methods=["GET", "POST"])
@admin_authentication.authenticate_admin
def render_main():
    """ Method responsible rendering admin template"""
    return render_template('admin_panel.html')


#TODO: Someone. We need response pages (or some other way of telling the person
# that they have entered bad information)
@admin_authentication.authenticate_admin
def reset_user_password():
    patient_id = request.values("patient_id")
    if User.exists( patient_id=patient_id ):
        new_password = User(patient_id).reset_password()
        return new_password
    return "that patient id does not exist"


# @admin_authentication.authenticate_admin
def create_new_patient():
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
