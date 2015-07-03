from flask import Blueprint, request, render_template, session, redirect
from libs.admin_authentication import authenticate_admin_login, authenticate_admin_study_access
from flask.helpers import make_response
from db.study_models import Surveys, Study, Studies, Survey
from libs.user_authentication import authenticate_user

survey_designer = Blueprint('survey_designer', __name__)

#TODO: josh/alvin. implement "study does not exist" page.
#TODO: josh/alvin. implement "survey does not exist" page.

################################################################################
############################# Creation/Deletion ##############################
################################################################################

#TODO: josh/alvin. in javascript, point a post request with a 'survey_type' parameter.
#TODO: josh/alvin. make the create survey page a real page.
@survey_designer.route('/create_survey/<string:study_id>', methods=['GET','POST'])
@authenticate_admin_study_access
def create_new_survey(study_id=None):
    if request.method == 'POST':
        study = Studies(_id=study_id)
        new_survey = Survey.create_default_survey( request.values['survey_type'] )
        study.add_survey(new_survey._id)
        return redirect('edit_survey/' + new_survey._id)
    if request.method == 'GET':
        return render_template("create_survey.html")

#TODO: josh/alvin. make a... button... somewhere that points to this function, suppling a survey id in the url
#TODO: Eli. return redirect to the study page or /
@survey_designer.route('/delete_survey/<string:survey_id>', methods=['POST'])
@authenticate_admin_study_access
def delete_survey(survey_id=None):
    survey = Surveys(_id=survey_id)
    survey.remove()
    study=Study(surveys=survey_id)
    study.remove_survey(survey_id)
    #return redirect()

################################################################################
############################# Setters and Editers ##############################
################################################################################

# @survey_designer.route('/update_daily_survey', methods=['GET', 'POST'])
# @authenticate_admin_login
# def update_daily():
#     return update_survey('daily', request)

# @survey_designer.route('/update_weekly_survey', methods=['GET', 'POST'])
# @authenticate_admin_login
# def update_weekly():
#     return update_survey('weekly', request)

#TODO: Everyone. test.
""""TODO: josh/alvin. redirect any urls in javascript and html that point to
update_daily_survey or update_weekly_survey to instead point at this url, supplying
a survey_ID. """
@survey_designer.route('/update_survey/<string:survey_id>', methods=['GET', 'POST'])
@authenticate_admin_study_access
def update_survey(survey_id=None):
    """TODO: Eli. the original code inside the try statement was:
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
        #TODO: Eli. investigate how timings are sent to the device.
        return '200'
    except UnicodeEncodeError as e:
        print "UnicodeEncodeError in update_survey().\nError:\n", e
        error_msg = ("There is a Unicode character in the text of one of the "
                     "questions you submitted. Make sure the question text "
                     "includes only ASCII characters.")
        return make_response(error_msg, 400)


""""TODO: josh/alvin. any hardcoded instance of the edit survey functions
(weekly_survey and daily_survey) should point at edit_survey/survey_id instead.
we no longer have a distinction between weekly and daily"""
@survey_designer.route('/edit_survey/<string:survey_id>/')
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
