from flask import Blueprint, request, abort, jsonify, render_template
from frontend import templating, auth

survey_designer = Blueprint('survey_designer', __name__)

@survey_designer.route('/survey_designer/')
@auth.authenticated()
@templating.template('survey_designer.html')
def render_survey_builder():
    data = {}
    return data

@survey_designer.route('/surveys/')
@auth.authenticated()
@templating.template('surveys.html')
def render_surveys():
    data = {
            #"sms_cohorts": [c for c in Cohorts()],
            #"email_cohorts": [ec for ec in EmailCohorts()]
           }
    return data


@survey_designer.route('/survey_designer/')
@auth.authenticated()
@templating.template('survey_designer.html')
def render_survey_designer():
    return render_template('survey_designer.html')

@survey_designer.route('/question_designer/')
@auth.authenticated()
@templating.template('question_designer.html')
def question_designer():
    return render_template('question_designer.html')
