import time
from flask import *
from libs import admin_authentication
from libs.admin_authentication import authenticate_admin_login,\
    authenticate_admin_study_access, get_admins_allowed_studies, get_admins_allowed_studies_as_query_set,\
    admin_is_system_admin
from libs.security import check_password_requirements

from database.models import Researcher, Study, Participant


admin_pages = Blueprint('admin_pages', __name__)

# TODO: Document.


@admin_pages.route('/choose_study', methods=['GET'])
@authenticate_admin_login
def choose_study():
    username = session['admin_username']
    if username == 'moht':
        return redirect('/downloads')

    allowed_studies = get_admins_allowed_studies_as_query_set()

    # If the admin is authorized to view exactly 1 study, redirect to that study
    if allowed_studies.count() == 1:
        return redirect('/view_study/{:d}'.format(allowed_studies.values_list('pk', flat=True).get()))

    # Otherwise, show the "Choose Study" page
    allowed_studies_json = Study.query_set_as_native_json(allowed_studies)
    return render_template(
        'choose_study.html',
        studies=allowed_studies_json,
        allowed_studies=allowed_studies_json,
        system_admin=admin_is_system_admin()
    )


def parse_dashboards(study):
    try:
        obj = eval(study.device_settings.external_dashboards)
        assert type(obj)==dict
    except:
        return {}
    return obj


@admin_pages.route('/view_study/<path:study_id>', methods=['GET'])
@authenticate_admin_study_access
def view_study(study_id=None):
    if '/' in study_id:
        its = study_id.split('/')
        participant = its[1]
        study_id = its[0]
    else:
        participant = False
    study = Study.objects.get(pk=study_id)
    tracking_survey_ids = study.get_survey_ids_and_object_ids_for_study('tracking_survey')
    audio_survey_ids = study.get_survey_ids_and_object_ids_for_study('audio_survey')
    participants = study.participants.all()

    if participant != False:
        try:
            device_id = Participant.objects.get(patient_id=participant).device_id
        except:
            device_id = ''
        response_string = 'Participant with patient_id=%s ' % participant
        response_string += ('has been registered successfully!' if device_id != '' else 'has NOT been registered!')
        flash(response_string, 'success')

    return render_template(
        'view_study.html',
        study=study,
        dashboards=parse_dashboards(study),
        TZ=session["timezone"],
        patients=participants,
        audio_survey_ids=audio_survey_ids,
        tracking_survey_ids=tracking_survey_ids,
        allowed_studies=get_admins_allowed_studies(),
        system_admin=admin_is_system_admin()
    )


@admin_pages.route('/data-pipeline/<string:study_id>', methods=['GET'])
@authenticate_admin_study_access
def view_study_data_pipeline(study_id=None):
    study = Study.objects.get(pk=study_id)

    return render_template(
        'data-pipeline.html',
        study=study,
        allowed_studies=get_admins_allowed_studies(),
    )


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
    """ Authenticates administrator login, redirects to login page if authentication fails. """
    if request.method == 'POST':
        username = request.values["username"]
        password = request.values["password"]
        try:
            timezone = int(request.values["timezone"])
        except:
            timezone = 0
        if Researcher.check_password(username, password):
            admin_authentication.log_in_admin(username, timezone)
            return redirect("/downloads" if username=="moht" else "/choose_study")
        else:
            flash("Incorrect username & password combination; try again.", 'danger')

    return redirect("/")


@admin_pages.route('/manage_credentials')
@authenticate_admin_login
def manage_credentials():
    username = session['admin_username']
    if username == 'moht':
        flash("This user is created for downloading APP only, please do not change its password!", 'danger')
        return redirect('/downloads')
    else:
        return render_template('manage_credentials.html',
                           allowed_studies=get_admins_allowed_studies(),
                           system_admin=admin_is_system_admin())


@admin_pages.route('/reset_admin_password', methods=['POST'])
@authenticate_admin_login
def reset_admin_password():
    username = session['admin_username']
    current_password = request.values['current_password']
    new_password = request.values['new_password']
    confirm_new_password = request.values['confirm_new_password']
    if not Researcher.check_password(username, current_password):
        flash("The Current Password you have entered is invalid", 'danger')
        return redirect('/manage_credentials')
    if not check_password_requirements(new_password, flash_message=True):
        return redirect("/manage_credentials")
    if new_password != confirm_new_password:
        flash("New Password does not match Confirm New Password", 'danger')
        return redirect('/manage_credentials')
    Researcher.objects.get(username=username).set_password(new_password)
    flash("Your password has been reset!", 'success')
    return redirect('/manage_credentials')


@admin_pages.route('/reset_download_api_credentials', methods=['POST'])
@authenticate_admin_login
def reset_download_api_credentials():
    researcher = Researcher.objects.get(username=session['admin_username'])
    access_key, secret_key = researcher.reset_access_credentials()
    msg = """<h3>Your Data-Download API access credentials have been reset!</h3>
        <p>Your new <b>Access Key</b> is: 
          <div class="container-fluid">
            <textarea rows="1" cols="85" readonly="readonly" onclick="this.focus();this.select()">%s</textarea></p>
          </div>
        <p>Your new <b>Secret Key</b> is:
          <div class="container-fluid">
            <textarea rows="1" cols="85" readonly="readonly" onclick="this.focus();this.select()">%s</textarea></p>
          </div>
        <p>Please record these somewhere; they will not be shown again!</p>""" \
        % (access_key, secret_key)
    flash(Markup(msg), 'warning')
    return redirect("/manage_credentials")
