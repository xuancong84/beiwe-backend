# Admin to refers to users/parts of the site that study administrators use.

from flask import Blueprint, request, abort, send_file, render_template
from libs import admin_authentication
from flask import redirect

admin = Blueprint('admin', __name__)


@admin.route('/')
@admin.route('/admin')
def render_login_page():
    if admin_authentication.is_logged_in():
        return redirect("/admin_panel")
    return render_template('admin_login.html')


# methods defines which HTML operations are expected
@admin.route("/validate_login", methods=["GET", "POST"])
def login():
    # Method responsible to authenticate researcher administrators.
    if request.method == 'POST':
        username = request.values["username"]
        password = request.values["password"]
        if validate_login_credentials(password, username):
            admin_authentication.login_admin()
            return redirect("/admin_panel")
        return "Username password combination is incorrect. Try again."
    else:
        return redirect("/admin")


def validate_login_credentials(password, username):
    if password == "1" and username == "1":
        return True
    return False
    #TODO: Eli/Kevin make this a real thing.
    #move to admin_authentication.py?


@admin.route("/logout")
def logout():
    admin_authentication.logout_loggedin_admin()
    return redirect("/")


@admin.route("/download")
def download():
    """ Method responsible for distributing APK file of Android app"""
    return send_file("Beiwe.apk", as_attachment=True)


@admin.route('/admin_panel', methods=["GET", "POST"])
@admin_authentication.authenticated
def render_main():
    """ Method responsible rendering admin template"""
    data = {
            #"users": []
            #"sms_cohorts": [c for c in Cohorts()],
            #"email_cohorts": [ec for ec in EmailCohorts()]
           }
    return render_template('admin_panel.html', **data)
