from flask import Blueprint, redirect, render_template, request, session
from libs import admin_authentication
from libs.admin_authentication import authenticate_admin_login,\
    authenticate_system_admin, authenticate_admin_study_access
from db.user_models import Users, Admin
from db.study_models import Study, Studies
from bson.objectid import ObjectId

admin = Blueprint('admin', __name__)


@admin.route('/choose_study', methods=['GET'])
@authenticate_admin_login
def choose_study():
    admin = Admin(session['admin_username'])
    authorized_studies = Studies(admins=admin._id)
    # If the admin is authorized to view exactly 1 study, redirect to that study
    if len(authorized_studies) == 1:
        return redirect('/view_study/' + str(authorized_studies[0]._id))
    # Otherwise, show the "Choose Study" page
    return render_template('choose_study.html',
                           authorized_studies=authorized_studies)


@admin.route('/view_study/<string:study_id>', methods=['GET'])
@authenticate_admin_login
def view_study(study_id):
    study = Study(ObjectId(study_id))
    # TODO: Josh, get patients just for this study, not ALL the patients
    patients = {user['_id']: patient_dict(user) for user in Users()}
    survey_ids = study.get_survey_ids_for_study()
    admin = Admin(session['admin_username'])
    authorized_studies = Studies(admins=admin._id)
    return render_template('view_study.html', study=study, patients=patients,
                           survey_ids=survey_ids, study_name=study.name,
                           authorized_studies=authorized_studies)
    # TODO: Josh, pass a list of studies into the dropdown


def patient_dict(patient):
    return {'placeholder_field': 'placeholder field for future data',
            'has_device': patient['device_id'] is not None }


"""########################### Study Pages ##################################"""
""""TODO: Alvin/Josh. implement this page, point the post function at /create_new_study,
see the create_new_study function in admin_api for details.
Page should include a paraphrase of "enter encryption key here for the study, all
user data stored by server will require this password, strongly recommend you use a
true random source, for instance random.org"""
@admin.route('/new_study', methods=["GET"])
@authenticate_system_admin
def render_make_new_study():
    return render_template("fill_me_in_:D")


@admin.route('/edit_study_device_settings/<string:study_id>', methods=["GET"])
#TODO: Eli. confirm that we have both decorators.  do we need a 4th decorator that does exactly this?
#@authenticate_system_admin
@authenticate_admin_study_access
def render_edit_study_device_settings(study_id=None):
    study = Studies(_id=ObjectId(study_id))[0]
    settings = study.get_study_device_settings()
    return render_template("edit_device_settings.html",
                           settings=settings[0],
                           study_id=study_id)


"""########################## Login/Logoff ##################################"""

@admin.route('/')
@admin.route('/admin')
def render_login_page():
    if admin_authentication.is_logged_in():
        return redirect("/choose_study")
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
            return redirect("/choose_study")
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

