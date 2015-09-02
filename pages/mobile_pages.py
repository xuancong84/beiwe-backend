from flask import request
from flask.blueprints import Blueprint
from flask.templating import render_template
from libs.user_authentication import authenticate_user
from libs.graph_data import get_survey_results
from db.user_models import User
from db.study_models import Study

mobile_pages = Blueprint('mobile_pages', __name__)

@mobile_pages.route('/graph', methods=['GET', 'POST'])
@authenticate_user
def fetch_graph():
    """ Fetches the patient's answers to the most recent survey, marked by
        survey ID. The results are dumped into a jinja template and pushed
        to the device."""
    patient_id = request.values['patient_id']
    user = User(patient_id)
    #see docs in config manipulations for details.
    study_id = user['study_id']
    study = Study(study_id)
    surveys = study['surveys']
    data = []
    for survey_id in surveys:
        data.append( get_survey_results(study_id, patient_id, survey_id, 7) )
    return render_template("phone_graphs.html", data=data)

# TODO: production. disable this page.
#  this is a debugging function, it displays the user graph for a given user.
# @mobile_pages.route("/fake", methods=["GET"] )
# def fake_survey():
#     patient_id = request.values['patient_id']
#     user = User(patient_id)
#     #see docs in config manipulations for details.
#     study_id = user['study_id']
#     study = Study(study_id)
#     surveys = study['surveys']
#     data = []
#     for survey_id in surveys:
#         data.append( get_survey_results(study_id, patient_id, survey_id, 7) )
#     return render_template("phone_graphs.html", data=data)
