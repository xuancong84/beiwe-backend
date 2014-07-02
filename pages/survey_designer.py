from flask import Blueprint, request, abort, jsonify
from frontend import templating, auth


survey_designer = Blueprint('survey_designer', __name__)


@survey_designer.route('/survey_designer/')
@auth.authenticated()
@templating.template('survey_designer.html')
def render_survey_builder():
    data = {}
    return data


#TODO: eventually, enable the system to
@survey_designer.route('/surveys/')
@auth.authenticated()
@templating.template('surveys.html')
def render_surveys():
    data = {
            #"sms_cohorts": [c for c in Cohorts()],
            #"email_cohorts": [ec for ec in EmailCohorts()]
           }
    return data


