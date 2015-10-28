from flask import Blueprint, redirect, render_template, request, session
from libs import admin_authentication
from libs.admin_authentication import authenticate_admin_login,\
    authenticate_system_admin, authenticate_admin_study_access,\
    get_admins_allowed_studies, admin_is_system_admin
from db.user_models import Users, Admin
from db.study_models import Study

admin_pages = Blueprint('admin_pages', __name__)


@admin_pages.route('/choose_study', methods=['GET'])
@authenticate_admin_login
def choose_study():
    allowed_studies = get_admins_allowed_studies()
    # If the admin is authorized to view exactly 1 study, redirect to that study
    if len(allowed_studies) == 1:
        return redirect('/view_study/' + str(allowed_studies[0]._id))
    # Otherwise, show the "Choose Study" page
    return render_template('choose_study.html',
                           allowed_studies=allowed_studies,
                           system_admin=admin_is_system_admin())


@admin_pages.route('/view_study/<string:study_id>', methods=['GET'])
@authenticate_admin_study_access
def view_study(study_id=None):
    study = Study(study_id)
    patients = {user['_id']: patient_dict(user) for user in Users( study_id = study_id )}
    tracking_survey_ids = study.get_survey_ids_for_study('tracking_survey')
    audio_survey_ids = study.get_survey_ids_for_study('audio_survey')
    return render_template('view_study.html', study=study, patients=patients,
                           audio_survey_ids=audio_survey_ids,
                           tracking_survey_ids=tracking_survey_ids,
                           study_name=study.name,
                           allowed_studies=get_admins_allowed_studies(),
                           system_admin=admin_is_system_admin())


def patient_dict(patient):
    return {'placeholder_field': 'placeholder field for future data',
            'has_device': patient['device_id'] is not None }


"""########################## Login/Logoff ##################################"""

@admin_pages.route('/')
@admin_pages.route('/admin')
def render_login_page():
    if admin_authentication.is_logged_in():
        return redirect("/choose_study")
    return render_template('admin_login.html')


@admin_pages.route("/logout")
def logout():
    admin_authentication.logout_loggedin_admin()
    return redirect("/")


@admin_pages.route("/validate_login", methods=["GET", "POST"])
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


@admin_pages.route('/reset_admin_password_form')
@authenticate_admin_login
def render_reset_admin_password_form():
    return render_template('reset_admin_password.html')

#TODO: Eli. Modify for use with data access system.
@admin_pages.route('/reset_admin_password', methods=['POST'])
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

