from flask import Blueprint, flash, Markup, render_template, session

from config.constants import ALL_DATA_STREAMS
from db.user_models import Admin, Users
from libs.admin_authentication import authenticate_admin_login,\
    get_admins_allowed_studies, admin_is_system_admin


data_access_web_form = Blueprint('data_access_web_form', __name__)

@data_access_web_form.route("/data_access_web_form", methods=['GET'])
@authenticate_admin_login
def data_api_web_form_page():
    # TODO: Josh, provide access to this route via a link in the top navbar
    admin = Admin(session['admin_username'])
    warn_admin_if_hasnt_yet_generated_access_key(admin)
    allowed_studies = get_admins_allowed_studies()
    # dict of {study ids : list of user ids}
    users_by_study = {str(study["_id"]) :
                      [user["_id"] for user in Users(study_id=study['_id'])]
                      for study in allowed_studies }
    return render_template("data_api_web_form.html",
                           allowed_studies=allowed_studies,
                           users_by_study=users_by_study,
                           ALL_DATA_STREAMS=ALL_DATA_STREAMS,
                           system_admin=admin_is_system_admin())


def warn_admin_if_hasnt_yet_generated_access_key(admin):
    if 'access_key_id' not in admin or not admin['access_key_id']:
        msg = """You need to generate an <b>Access Key</b> and a <b>Secret Key </b> before you
        can download data. Go to <a href='/manage_credentials'> Manage Credentials</a> and click
        'Reset Data-Download API Access Credentials'. """
        flash(Markup(msg), 'danger')
