from flask import Blueprint, request, abort, send_file
from frontend import templating, auth
from flask import redirect

admin = Blueprint('admin', __name__)

@admin.route('/')
@admin.route('/admin')
@templating.template('admin_login.html')
def render_login_page():
    if auth.is_logged_in():
        return redirect("/admin_panel")
    return {}

@admin.route("/validate_login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        username = request.values["username"]
        password = request.values["password"]
        if password == "1" and username == "1":
            auth.login_user()
            return redirect("/admin_panel")
        return "Username password combination is incorrect. Try again."
    else:
        return redirect("/admin")

@admin.route("/logout")
def logout():
    auth.del_loggedin_phonenum()
    return redirect("/")

@admin.route("/download")
def download():
    return send_file("Beiwe.apk", as_attachment=True)

@admin.route('/admin_panel', methods=["GET", "POST"])
@auth.authenticated()
@templating.template('admin_panel.html')
def render_main():
    data = {
            #"sms_cohorts": [c for c in Cohorts()],
            #"email_cohorts": [ec for ec in EmailCohorts()]
           }
    return data