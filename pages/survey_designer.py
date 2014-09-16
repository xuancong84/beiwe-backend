from flask import Blueprint, request, abort, jsonify, render_template, json, redirect
from libs import admin_authentication
from libs.s3 import s3_list_files, s3_retrieve, s3_upload_handler_file
from datetime import datetime

survey_designer = Blueprint('survey_designer', __name__)

################################################################################
############################### Setters ########################################
################################################################################

#FIXME: Eli. determine if these will be used at all (as Josh has rewritten the submission pages, if not REMOVE THEM

@survey_designer.route('/update_weekly', methods=['GET', 'POST'])
@admin_authentication.authenticated
def save_new_weekly():
    """ Method responsible for saving newly created weekly survey (frequency 1) """
    print request.values, "\n-\n"
    print request.form, "\n-\n"
    print request
    weeklies = get_surveys("survey/weekly/")
#     print "weeklies done"
    key_name = "survey/weekly/{0}/{1}.json".format(datetime.now().strftime("%Y-%m-%d-%H:%M:%S"), len(weeklies) + 1)
#     print "key name done"
#     breaks here
#     from pprint import pprint
#     import pickle
#     pickle.dump(request.values, open('thingX.pickle', 'w'))
#     pprint (request.values)
#     print "\n\n", request.files["json"] , "\n\n"
#
#     try:
    s3_upload_handler_file(key_name, json.dumps(request.files["json"]))
#     except Exception as e:
#         print "\n", e
#         raise e
#     print "upload done"
    return redirect("/weekly_survey/")


@survey_designer.route('/update_daily')
@admin_authentication.authenticated
def save_new_daily():
    """ Method responsible for saving newly created daily survey (frequency 1) """
    dailies = get_surveys("survey/daily/")
    key_name = "survey/daily/{0}/{1}.json".format(datetime.now().strftime("%Y-%m-%d-%H:%M:%S"), len(dailies) + 1)
    s3_upload_handler_file(key_name, json.dumps(request.files["json"]))
    return redirect("/daily_survey/")


################################################################################
############################### Getters ########################################
################################################################################

def get_surveys(prefix="survey/"):
    surveys = s3_list_files(prefix)
    return [i.strip(prefix).strip(".json") for i in surveys]


def get_latest_weekly():
    """ Method responsible for fetching latest created weekly survey
        (frequency 1) """
    weeklies = get_surveys("survey/weekly/")
    weeklies = sorted(weeklies, reverse=True)
    return jsonify(s3_retrieve(weeklies[0]))


def get_latest_daily():
    """ Method responsible for fetching latest created daily survey (frequency 1) """
    dailies = get_surveys("survey/daily/")
    dailies = sorted(dailies, reverse=True)
    return jsonify(s3_retrieve(dailies[0]))


################################################################################
########################### Pure routes ########################################
################################################################################

@survey_designer.route('/survey_designer')
@admin_authentication.authenticated
def render_survey_builder():
    data = {}
    return render_template('survey_designer.html', data)

@survey_designer.route('/surveys')
@admin_authentication.authenticated
def render_surveys():
    data = {}
    return render_template('surveys.html', data)

@survey_designer.route('/survey_designer')
@admin_authentication.authenticated
def render_survey_designer():
    return render_template('survey_designer.html')

@survey_designer.route('/question_designer')
@admin_authentication.authenticated
def question_designer():
    return render_template('question_designer.html')

@survey_designer.route('/weekly_survey')
@admin_authentication.authenticated
def weekly_survey():
    return render_template('weekly_survey.html')

@survey_designer.route('/daily_survey')
@admin_authentication.authenticated
def daily_survey():
    return render_template('daily_survey.html')