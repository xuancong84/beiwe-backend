from flask import Blueprint
from libs.admin_authentication import authenticate_admin_login
from flask.templating import render_template
from db.study_models import Study
from flask.globals import session
from db.user_models import Admin, Users

data_access_web_form = Blueprint('data_access_web_form', __name__)

@authenticate_admin_login
@data_access_web_form.route("/data_access_web_form")
def data_api_web_form_page():
    admin_id = session['admin_username']
    if not Admin(admin_id)['access_key_id']:
        return render_template("data_api_web_form_fail.html")
    # list of [study objects]
    studies = Study.get_studies_for_admin(admin_id)
    # dict of {study ids : list of user ids}
    users_by_study = {study["_id"] :
                      [user["_id"] for user in Users(study_id=study['_id'])]
                      for study in studies }
    print studies
    print users_by_study
#     return render_template("data_api_web_form.html", studies=studies,
#                            users_by_study=users_by_study)