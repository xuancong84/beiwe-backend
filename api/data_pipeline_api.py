import json

from flask import Blueprint, flash, redirect, request

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
    
    # AJK TODO make a function common between this and index.py to reduce redundancy
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
