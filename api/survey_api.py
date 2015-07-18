from flask import abort, Blueprint, request, redirect
from libs.admin_authentication import authenticate_admin_study_access
from db.study_models import Survey, Study

survey_api = Blueprint('survey_api', __name__)

################################################################################
############################# Creation/Deletion ##############################
################################################################################

@survey_api.route('/create_survey/<string:study_id>', methods=['GET','POST'])
@authenticate_admin_study_access
def create_new_survey(study_id=None):
    study = Study(study_id)
    new_survey = Survey.create_default_survey('android_survey')
    study.add_survey(new_survey)
    return redirect('edit_survey/' + str(new_survey._id))

@survey_api.route('/delete_survey/<string:survey_id>', methods=['GET', 'POST'])
@authenticate_admin_study_access
def delete_survey(survey_id=None):
    survey = Survey(survey_id)
    if not survey:
        return abort(404)
    study = Study(surveys=survey_id)
    study.remove_survey(survey)
    survey.remove()
    return redirect('/view_study/' + str(study._id))

################################################################################
############################# Setters and Editors ##############################
################################################################################

#TODO: Everyone. test.
@survey_api.route('/update_survey/<string:survey_id>', methods=['GET', 'POST'])
@authenticate_admin_study_access
def update_survey(survey_id=None):
    survey = Survey(survey_id)
    if not survey:
        return abort(404)
    survey.update({'content': request.values['questions']})
    #TODO: Eli. investigate how timings are sent to the device.
    #TODO: Josh, consider making this NOT AJAX; just make it a regular submit
    return '200'
    """TODO: Eli/Josh: UnicodeEncodeErrors no longer happen, but we don't know
    if the Android app will support Unicode. If it doesn't, we need to warn the
    admin here if the admin tries to use Unicode.""" 
