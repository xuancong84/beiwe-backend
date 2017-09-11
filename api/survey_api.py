from flask import abort, Blueprint, make_response, request, redirect, json
from libs.admin_authentication import authenticate_admin_study_access
from libs.json_logic import do_validate_survey

# Mongolia models
from db.study_models import Survey, Study

# Django models
from study.models import Survey as DSurvey

survey_api = Blueprint('survey_api', __name__)

################################################################################
############################## Creation/Deletion ###############################
################################################################################


@survey_api.route('/create_survey/<string:study_id>/<string:survey_type>', methods=['GET', 'POST'])
@authenticate_admin_study_access
def create_new_survey(study_id=None, survey_type='tracking_survey'):
    new_survey = DSurvey.create_with_settings(survey_type, study_id=study_id)
    return redirect('edit_survey/{:d}'.format(new_survey.id))


@survey_api.route('/delete_survey/<string:survey_id>', methods=['GET', 'POST'])
@authenticate_admin_study_access
# AJK TODO shouldn't this be POST only?
def delete_survey(survey_id=None):
    survey_set = DSurvey.objects.filter(pk=survey_id)
    if survey_set.exists():
        survey = survey_set.get()
    else:
        return abort(404)

    study = survey.study
    study.remove_survey(survey)
    survey.mark_deleted()
    return redirect('/view_study/{:d}'.format(study.id))

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
    content = make_slider_min_max_values_strings(content)
    if survey.survey_type == "tracking_survey":  # TODO:turn tracking_survey into a constant
        errors = do_validate_survey(content)
        if len(errors) > 1:
            return make_response(json.dumps(errors), 400)
    timings = json.loads(request.values['timings'])
    settings = json.loads(request.values['settings'])
    survey.update({'content': content, 'timings': timings, 'settings': settings})
    return make_response("", 201)


def make_slider_min_max_values_strings(json_content):
    """ Turns min/max int values into strings, because the iOS app expects strings. This is for
    backwards compatibility; when all the iOS apps involved in studies can handle ints,
    we can remove this function. """
    for question in json_content:
        if 'max' in question:
            question['max'] = str(question['max'])
        if 'min' in question:
            question['min'] = str(question['min'])
    return json_content
