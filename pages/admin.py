from flask import Blueprint, request, send_file, render_template, redirect
from libs import admin_authentication

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
    data = {
            #"users": []
            #"sms_cohorts": [c for c in Cohorts()],
            #"email_cohorts": [ec for ec in EmailCohorts()]
           }
    return render_template('admin_panel.html', **data)


#TODO: Eli. implement
def reset_user_password(): pass


#TODO: Eli. implement
def reset_admin_password(): pass


################################################################################
############################# Other Stuff ######################################
################################################################################

@admin.route("/download")
def download():
    """ Method responsible for distributing APK file of Android app"""
    return send_file("Beiwe.apk", as_attachment=True)
