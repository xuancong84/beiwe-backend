from flask import Blueprint, request, abort, jsonify, render_template, json, redirect
from frontend import templating, auth
from utils.s3 import list_s3_files, s3_retrieve, s3_upload_handler
from datetime import datetime

survey_designer = Blueprint('survey_designer', __name__)

def get_surveys(prefix="survey/"):
    surveys = list_s3_files(prefix)
    return [i.strip(prefix).strip(".json") for i in surveys]

def get_latest_weekly():
    weeklies = get_surveys("survey/weekly/")
    weeklies = sorted(weeklies, reverse=True)
    return jsonify(s3_retrieve(weeklies[0]))

def get_latest_daily():
    dailies = get_surveys("survey/daily/")
    dailies = sorted(dailies, reverse=True)
    return jsonify(s3_retrieve(dailies[0]))

@survey_designer.route('/update_weekly')
@auth.authenticated()
def save_new_weekly():
    weeklies = get_surveys("survey/weekly/")
    key_name = "survey/weekly/{0}/{1}.json".format(datetime.now().strftime("%Y-%m-%d-%H:%M:%S"), len(weeklies) + 1)
    s3_upload_handler(key_name, json.dumps(request.files["json"]))
    return redirect("/weekly_survey/")

@survey_designer.route('/update_daily')
@auth.authenticated()
def save_new_daily():
    dailies = get_surveys("survey/daily/")
    key_name = "survey/daily/{0}/{1}.json".format(datetime.now().strftime("%Y-%m-%d-%H:%M:%S"), len(dailies) + 1)
    s3_upload_handler(key_name, json.dumps(request.files["json"]))
    return redirect("/daily_survey/")

@survey_designer.route('/survey_designer')
@auth.authenticated()
@templating.template('survey_designer.html')
def render_survey_builder():
    data = {}
    return data

@survey_designer.route('/surveys')
@auth.authenticated()
@templating.template('surveys.html')
def render_surveys():
    data = {
            #"sms_cohorts": [c for c in Cohorts()],
            #"email_cohorts": [ec for ec in EmailCohorts()]
           }
    return data

@survey_designer.route('/survey_designer')
@auth.authenticated()
@templating.template('survey_designer.html')
def render_survey_designer():
    return render_template('survey_designer.html')

@survey_designer.route('/question_designer')
@auth.authenticated()
@templating.template('question_designer.html')
def question_designer():
    return render_template('question_designer.html')

@survey_designer.route('/weekly_survey')
@auth.authenticated()
@templating.template('weekly_survey.html')
def weekly_survey():
    return render_template('weekly_survey.html')

@survey_designer.route('/daily_survey')
@auth.authenticated()
@templating.template('daily_survey.html')
def daily_survey():
    return render_template('daily_survey.html')
