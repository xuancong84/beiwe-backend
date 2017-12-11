import json

from flask import Blueprint, flash, jsonify, redirect, request

from db.study_models import Studies
from libs.admin_authentication import authenticate_admin_study_access
from pipeline.boto_helpers import get_boto_client


data_pipeline_api = Blueprint('data_pipeline_api', __name__)


# TODO when the django branch gets merged, the child of commit 183842fd3cc4c217e83719519d2bb1604c024f82 needs to be reverted
@data_pipeline_api.route('/run-manual-code/<string:study_id>', methods=['POST'])
@authenticate_admin_study_access
# AJK TODO annotate
def run_manual_code(study_id):
    client = get_boto_client('batch')
    with open('pipeline/aws-object-names.json') as fn:
        object_names = json.load(fn)
    
    client.submit_job(
        jobName=object_names['job_name'].format(freq='manually'),
        jobDefinition=object_names['job_defn_name'],
        jobQueue=object_names['queue_name'],
        containerOverrides={
            'command': [
                '/bin/bash',
                'runner.sh',
                'Beiwe-Analysis/Pipeline/manually',
                str(study_id),
            ]
        }
    )
    flash('Data pipeline code successfully initiated!', 'success')
    
    return redirect('/data-pipeline/{:s}'.format(study_id))


@data_pipeline_api.route('/list-all-study-ids', methods=['GET'])
def list_all_study_ids():
    """
    List all IDs of Study objects in the database that have not been deleted
    :return: A Response object containing a JSON blob of the form {study_ids: ['blah', 'blah']}
    """
    
    # Get the Study IDs and convert them to strings (they are ObjectIds initially)
    # Django: study_ids = Study.objects.filter(deleted=False).values_list('object_id', flat=True)
    study_ids_raw = Studies(deleted=False, field='_id')
    study_ids = map(str, study_ids_raw)
    
    # Using flask.json.jsonify, make a nice HTTP Response out of the list
    return jsonify(study_ids=study_ids)
