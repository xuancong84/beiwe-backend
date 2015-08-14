from flask import request
from libs import graph_data
from flask.blueprints import Blueprint
from libs.user_authentication import authenticate_user
from flask.templating import render_template
from config.constants import WEEKLY_SURVEY_NAME, DAILY_SURVEY_NAME

mobile_pages = Blueprint('mobile_pages', __name__)

@mobile_pages.route('/graph', methods=['GET', 'POST'])
@authenticate_user
def fetch_graph():
    """ Fetches the patient's answers to the most recent survey, marked by
        survey ID. The results are dumped into a jinja template and pushed
        to the device."""
    patient_id = request.values['patient_id']

    #see docs in config manipulations for details.
    daily_data = graph_data.get_survey_results(username=patient_id,
                                 survey_type=DAILY_SURVEY_NAME, number_points=7)
    
    weekly_data = graph_data.get_survey_results(username=patient_id,
                                 survey_type=WEEKLY_SURVEY_NAME, number_points=7)
    
    return render_template("phone_graphs.html", weekly_data=weekly_data, daily_data=daily_data)

#TODO: production. disable this page.
# this is a debugging function, it displays the user graph for a given user.
# @mobile_pages.route("/fake", methods=["GET"] )
# def fake_survey():
#     patient_id = request.values['patient_id']
#     daily_data = graph_data.get_survey_results(username=patient_id,
#                                  survey_type=DAILY_SURVEY_NAME, number_points=7)
#     
#     weekly_data = graph_data.get_survey_results(username=patient_id,
#                                  survey_type=WEEKLY_SURVEY_NAME, number_points=7)
#     
#     return render_template("phone_graphs.html", weekly_data=weekly_data, daily_data=daily_data)
