from flask import Blueprint, flash, jsonify, redirect, request

from db.study_models import Studies
from libs.admin_authentication import authenticate_admin_study_access
from pipeline.boto_helpers import get_boto_client, get_aws_object_names
from pipeline.index import create_one_job


data_pipeline_api = Blueprint('data_pipeline_api', __name__)


# TODO when the django branch gets merged, the child of commit 183842fd3cc4c217e83719519d2bb1604c024f82 needs to be reverted
@data_pipeline_api.route('/run-manual-code/<string:study_id>', methods=['POST'])
@authenticate_admin_study_access
def run_manual_code(study_id):
    """
    Create an AWS Batch job for the Study specified
    :param study_id: ObjectId of a Study
    """
    
    client = get_boto_client('batch')
    aws_object_names = get_aws_object_names()
    create_one_job('manually', str(study_id), aws_object_names, client)
    
    flash('Data pipeline code successfully initiated!', 'success')
    
    return redirect('/data-pipeline/{:s}'.format(study_id))
