from flask import abort, Blueprint, render_template
from libs.admin_authentication import authenticate_admin_study_access,\
    get_admins_allowed_studies, admin_is_system_admin
from study.models import Survey


survey_designer = Blueprint('survey_designer', __name__)

# TODO: Low Priority. implement "study does not exist" page.
# TODO: Low Priority. implement "survey does not exist" page.


@survey_designer.route('/edit_survey/<string:survey_id>')
@authenticate_admin_study_access
def render_edit_survey(survey_id=None):
    survey_set = Survey.objects.filter(pk=survey_id)
    if survey_set.exists():
        survey = survey_set.get()
    else:
        return abort(404)

    study = survey.study
    return render_template(
        'edit_survey.html',
        survey=survey,
        study=study,
        allowed_studies=get_admins_allowed_studies(),
        system_admin=admin_is_system_admin()
    )
