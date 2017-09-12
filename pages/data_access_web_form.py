import json

from flask import Blueprint, flash, Markup, render_template, session

from config.constants import ALL_DATA_STREAMS
from libs.admin_authentication import (
    admin_is_system_admin, authenticate_admin_login,
    get_admins_allowed_studies, get_admins_allowed_studies_as_query_set
)
from study.models import Researcher


data_access_web_form = Blueprint('data_access_web_form', __name__)


@data_access_web_form.route("/data_access_web_form", methods=['GET'])
@authenticate_admin_login
def data_api_web_form_page():
    researcher = Researcher.objects.get(username=session['admin_username'])
    warn_researcher_if_hasnt_yet_generated_access_key(researcher)
    allowed_studies = get_admins_allowed_studies_as_query_set()
    # dict of {study ids : list of user ids}
    users_by_study = {
        study.pk: [user.patient_id for user in study.participants.all()]
        for study in allowed_studies
    }
    return render_template(
        "data_api_web_form.html",
        allowed_studies=get_admins_allowed_studies(),
        users_by_study=json.dumps(users_by_study),
        ALL_DATA_STREAMS=ALL_DATA_STREAMS,
        system_admin=admin_is_system_admin()
    )


def warn_researcher_if_hasnt_yet_generated_access_key(researcher):
    if not researcher.access_key_id:
        msg = """You need to generate an <b>Access Key</b> and a <b>Secret Key </b> before you
        can download data. Go to <a href='/manage_credentials'> Manage Credentials</a> and click
        'Reset Data-Download API Access Credentials'. """
        flash(Markup(msg), 'danger')
