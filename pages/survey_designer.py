from datetime import datetime
from flask import Blueprint, request, render_template
from libs.admin_authentication import authenticate_admin
from libs.s3 import s3_list_files, s3_retrieve, s3_upload_handler_string


survey_designer = Blueprint('survey_designer', __name__)

################################################################################
############################### Setters ########################################
################################################################################

# TODO: Josh. make sure that uncommenting @authenticate_admin
# does not break survey editing.

@survey_designer.route('/update_daily_survey', methods=['GET', 'POST'])
# @authenticate_admin
def update_daily():
    return update_survey('daily', request)


@survey_designer.route('/update_weekly_survey', methods=['GET', 'POST'])
# @authenticate_admin
def update_weekly():
    return update_survey('weekly', request)


def update_survey(survey_type, request):
    survey_name = 'all_surveys/' + survey_type + '/'  # set filepath
    survey_name += datetime.now().isoformat() + '.json'  # set filename
    new_quiz = request.values['JSONstring']
    s3_upload_handler_string( survey_name, new_quiz )
    # TODO: Josh, only return 200 on success; otherwise something else
    return '200'


################################################################################
############################### Getters ########################################
################################################################################

def get_surveys(prefix):
    surveys = s3_list_files(prefix)
    return [survey_file for survey_file in surveys]


def get_latest_survey(survey_type):
    surveys = get_surveys('all_surveys/' + survey_type + '/')
    surveys = sorted(surveys, reverse=True)
    return s3_retrieve(surveys[0])


@survey_designer.route('/get_weekly_survey', methods=['GET', 'POST'])
def get_latest_weekly():
    """ Method responsible for fetching latest created weekly survey
        (frequency 1) """
    return get_latest_survey('weekly')


@survey_designer.route('/get_daily_survey', methods=['GET', 'POST'])
def get_latest_daily():
    """ Method responsible for fetching latest created daily survey (frequency 1) """
    return get_latest_survey('daily')


################################################################################
########################### Pure routes ########################################
################################################################################

@survey_designer.route('/survey_designer')
@authenticate_admin
def render_survey_builder():
    data = {}
    return render_template('survey_designer.html', data)

@survey_designer.route('/surveys')
@authenticate_admin
def render_surveys():
    data = {}
    return render_template('surveys.html', data)

@survey_designer.route('/survey_designer')
@authenticate_admin
def render_survey_designer():
    return render_template('survey_designer.html')

@survey_designer.route('/weekly_survey')
@authenticate_admin
def weekly_survey():
    return render_template('edit_survey.html', daily_or_weekly='weekly')

@survey_designer.route('/daily_survey')
@authenticate_admin
def daily_survey():
    return render_template('edit_survey.html', daily_or_weekly='daily')
