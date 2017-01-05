from flask import abort, Blueprint, make_response, request, redirect, json
from libs.admin_authentication import authenticate_admin_study_access
from db.study_models import Survey, Study
from libs.json_logic import do_validate_survey

survey_api = Blueprint('survey_api', __name__)

################################################################################
############################## Creation/Deletion ###############################
################################################################################

@survey_api.route('/create_survey/<string:study_id>/<string:survey_type>',
                  methods=['GET','POST'])
@authenticate_admin_study_access
def create_new_survey(study_id=None,survey_type='tracking_survey'):
    study = Study(study_id)
    new_survey = Survey.create_default_survey(survey_type)
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

@survey_api.route('/update_survey/<string:survey_id>', methods=['GET', 'POST'])
@authenticate_admin_study_access
def update_survey(survey_id=None):
    survey = Survey(survey_id)
    if not survey:
        return abort(404)
    content = json.loads(request.values['content'])
    if survey.survey_type == "tracking_survey":  # TODO: ELI TURN TRACKINGSURVEYINTOAconsta..
        errors = do_validate_survey(content)
        if len(errors) > 1:
            return make_response(json.dumps(errors), 400)
    timings = json.loads(request.values['timings'])
    settings = json.loads(request.values['settings'])
    survey.update({'content': content, 'timings': timings, 'settings': settings})
    return make_response("", 201)
