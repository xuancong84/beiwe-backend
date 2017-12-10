from flask import Blueprint, redirect, request

from libs.admin_authentication import authenticate_admin_study_access


data_pipeline = Blueprint('data_pipeline', __name__)


@data_pipeline.route('/run-manual-code', methods=["POST"])
@authenticate_admin_study_access
# AJK TODO annotate
def create_new_patient():
    study_id = request.values['study_id']
    return redirect('/data-pipeline/{:s}'.format(study_id))
