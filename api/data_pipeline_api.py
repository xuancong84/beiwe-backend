from flask import Blueprint, flash, redirect

from libs.admin_authentication import authenticate_admin_study_access
from pipeline.index import create_one_job


data_pipeline_api = Blueprint('data_pipeline_api', __name__)


@data_pipeline_api.route('/run-manual-code/<string:study_id>', methods=['POST'])
@authenticate_admin_study_access
def run_manual_code(study_id):
    """
    Create an AWS Batch job for the Study specified
    :param study_id: ObjectId of a Study
    """
    
    create_one_job('manually', study_id)
    
    # The success message gets displayed to the user upon redirect
    flash('Data pipeline code successfully initiated!', 'success')
    
    return redirect('/data-pipeline/{:s}'.format(study_id))
