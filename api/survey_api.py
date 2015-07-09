from bson import ObjectId
from flask import request, redirect
from flask.blueprints import Blueprint
from libs.admin_authentication import authenticate_admin_study_access
from db.study_models import Survey, Surveys, Study
from flask.helpers import make_response

survey_api = Blueprint('survey_api', __name__)

################################################################################
############################# Creation/Deletion ##############################
################################################################################

@survey_api.route('/create_survey/<string:study_id>', methods=['GET','POST'])
#@authenticate_admin_study_access
def create_new_survey(study_id=None):
    study = Study(_id=ObjectId(study_id))
    new_survey = Survey.create_default_survey('android_survey')
    study.add_survey(new_survey)
    return redirect('edit_survey/' + str(new_survey._id))

#TODO: Josh. make a... button... somewhere that points to this function, suppling a survey id in the url
#TODO: Eli. return redirect to the study page or /
@survey_api.route('/delete_survey/<string:survey_id>', methods=['POST'])
@authenticate_admin_study_access
def delete_survey(survey_id=None):
    survey = Surveys(_id=survey_id)
    survey.remove()
    study=Study(surveys=survey_id)
    study.remove_survey(survey)
    #return redirect()

################################################################################
############################# Setters and Editers ##############################
################################################################################

# @survey_api.route('/update_daily_survey', methods=['GET', 'POST'])
# @authenticate_admin_login
# def update_daily():
#     return update_survey('daily', request)

# @survey_api.route('/update_weekly_survey', methods=['GET', 'POST'])
# @authenticate_admin_login
# def update_weekly():
#     return update_survey('weekly', request)

#TODO: Everyone. test.
""""TODO: Josh. redirect any urls in javascript and html that point to
update_daily_survey or update_weekly_survey to instead point at this url, supplying
a survey_ID. """
@survey_api.route('/update_survey/<string:survey_id>', methods=['GET', 'POST'])
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
