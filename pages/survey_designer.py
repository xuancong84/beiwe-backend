from flask import Blueprint, request, render_template, session
from libs.admin_authentication import authenticate_admin_login, authenticate_admin_study_access
from flask.helpers import make_response
from db.study_models import Surveys, Study
from libs.user_authentication import authenticate_user


survey_designer = Blueprint('survey_designer', __name__)

#TODO: refactor to use the <string:survey_id> url argument
#TODO: implement "study does not exist" page.
#TODO: implement "survey does not exist" page.

################################################################################
############################# Setters and Editers ##############################
################################################################################

#TODO: implement new survey creation
def create_new_survey():
    pass

#TODO: implement delete survey
def delete_survey():
    pass

#TODO: redirect any urls in javascript to point at the arbitrarily typed survey.
# @survey_designer.route('/update_daily_survey', methods=['GET', 'POST'])
# @authenticate_admin_login
# def update_daily():
#     return update_survey('daily', request)

# @survey_designer.route('/update_weekly_survey', methods=['GET', 'POST'])
# @authenticate_admin_login
# def update_weekly():
#     return update_survey('weekly', request)

#TODO: make sure that this url, which is directed to by javascript, contains the session cookie.
#TODO: test
@survey_designer.route('/update_survey/<string:survey_id>', methods=['GET', 'POST'])
@authenticate_admin_study_access
def update_survey(survey_id=None):
    """TODO: the original code inside the try was:
        survey_name = 'all_surveys/' + survey_type + '/'  # set filepath
        survey_name += datetime.now().isoformat() + '.json'  # set filename
        new_quiz = request.values['JSONstring']
        s3_upload( survey_name, new_quiz )
    We don't know where the error occurred in those lines. We have entirely
    different code now, I don't know if/where a unicode error can occur. """
    try:
        new_content = request.values['JSONstring']
        survey = Surveys(survey_id)
        survey['content'] = new_content
        #TODO: investigate how timings are sent to the device.
        return '200'
    except UnicodeEncodeError as e:
        print "UnicodeEncodeError in update_survey().\nError:\n", e
        error_msg = ("There is a Unicode character in the text of one of the "
                     "questions you submitted. Make sure the question text "
                     "includes only ASCII characters.")
        return make_response(error_msg, 400)

#TODO: point this at a real template
@survey_designer.route('/participants')
@authenticate_admin_login
def render_surveys():
    """Provides a list of studies that the current admin has access to."""
    studies = Study.get_studies_for_admin(session['admin_username'])
    users_by_study = {}
    for study in studies:
        users_by_study[study.name] = study.get_users_in_study()
    return render_template('surveys.html', users_by_study)

#TODO: purge any usage of weekly and daily urls (below), use this instead.
@survey_designer.route('/<string:survey_id>/weekly_survey')
@authenticate_admin_study_access
def render_edit_survey(survey_id=None):
    return render_template('edit_survey.html', survey=Surveys(survey_id) )

# @survey_designer.route('/weekly_survey')
# @authenticate_admin_login
# def weekly_survey():
#     return render_template('edit_survey.html', daily_or_weekly='weekly')
# 
# @survey_designer.route('/daily_survey')
# @authenticate_admin_login
# def daily_survey():
#     return render_template('edit_survey.html', daily_or_weekly='daily')


################################################################################
########################### Device Survey Getters ##############################
################################################################################

#TODO: make sure that this url is pointed at correctly by the app
#TODO: check that the authenticate_user decorator is correctly used.
@survey_designer.route('/<string:survey_id>/download/', methods=['GET', 'POST'])
@authenticate_user
def get_latest_survey(survey_id):
    #TODO: another reminder about checking on how timings are sent to the app
    # and if the need to be sent inside of this function (probably yes)
    return Surveys(survey_id)['content']

#TODO: Purge any use of the commented urls below
# @survey_designer.route('/get_weekly_survey', methods=['GET', 'POST'])
# def get_latest_weekly():
#     """ Method responsible for fetching latest created weekly survey
#         (frequency 1) """
#     return get_latest_survey('weekly')

# @survey_designer.route('/get_daily_survey', methods=['GET', 'POST'])
# def get_latest_daily():
#     """ Method responsible for fetching latest created daily survey (frequency 1) """
#     return get_latest_survey('daily')
# def get_surveys(prefix):
#     surveys = s3_list_files(prefix)
#     return [survey_file for survey_file in surveys]
