from config.constants import ALL_DATA_STREAMS
from flask import Blueprint, request
from libs.admin_authentication import authenticate_admin_login,\
    get_admins_allowed_studies, admin_is_system_admin
from flask.templating import render_template
from flask.globals import session
from db.user_models import Admin, Users
from pprint import pprint

data_access_web_form = Blueprint('data_access_web_form', __name__)

@authenticate_admin_login
@data_access_web_form.route("/data_access_web_form", methods=['GET', 'POST'])
def data_api_web_form_page():
    # TODO: Josh, provide access to this route via a link in the top navbar
    admin = Admin(session['admin_username'])
    # TODO: Josh, fix this or replace it with a flash()
    if 'access_key_id' not in admin or not admin['access_key_id']:
        return render_template("data_api_web_form_fail.html")
    allowed_studies = get_admins_allowed_studies()
    # dict of {study ids : list of user ids}
    users_by_study = {str(study["_id"]) :
                      [user["_id"] for user in Users(study_id=study['_id'])]
                      for study in allowed_studies }
    if request.method == 'POST':
        # TODO: Josh, break this out into its own function and route
        access_key = request.form.get('access_key')
        secret_key = request.form.get('secret_key')
        study_id = request.form.get('study_selector')
        users = request.form.getlist('patient_selector')
        data_streams = request.form.getlist('data_stream_selector')
        start_datetime = request.form.get('start_datetime')
        end_datetime = request.form.get('end_datetime')
        pprint(access_key)
        pprint(secret_key)
        pprint(study_id)
        pprint(users)
        pprint(data_streams)
        pprint(start_datetime)
        pprint(end_datetime)
        # TODO: Josh, plug this into Eli's search API
    return render_template("data_api_web_form.html",
                           allowed_studies=allowed_studies,
                           users_by_study=users_by_study,
                           ALL_DATA_STREAMS=ALL_DATA_STREAMS,
                           system_admin=admin_is_system_admin())
