from bson import ObjectId
from flask import abort, Blueprint, render_template

from db.study_models import Survey
from libs.admin_authentication import authenticate_admin_study_access

survey_designer = Blueprint('survey_designer', __name__)

#TODO: josh/alvin. implement "study does not exist" page.
#TODO: josh/alvin. implement "survey does not exist" page.

""""TODO: Josh. any hardcoded instance of the edit survey functions
(weekly_survey and daily_survey) should point at edit_survey/survey_id instead.
we no longer have a distinction between weekly and daily"""
@survey_designer.route('/edit_survey/<string:survey_id>')
@authenticate_admin_study_access
def render_edit_survey(survey_id=None):
    survey = Survey(ObjectId(survey_id))
    if not survey:
        return abort(404)
    return render_template('edit_survey.html', survey=survey)