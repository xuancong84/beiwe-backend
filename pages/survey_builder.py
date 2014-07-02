from flask import Blueprint, request, abort, jsonify
from frontend import templating, auth


survey_builder = Blueprint('survey_builder', __name__)


@admin.route('/survey_builder/')
@auth.authenticated()
@templating.template('survey_builder.html')
def render_survey_builder():
    data = {}
    return data


#TODO: eventually, enable the system to 
@admin.route('/surveys/')
@auth.authenticated()
@templating.template('surveys.html')
def render_surveys():
    data = {
            #"sms_cohorts": [c for c in Cohorts()],
            #"email_cohorts": [ec for ec in EmailCohorts()]
           }
    return data


