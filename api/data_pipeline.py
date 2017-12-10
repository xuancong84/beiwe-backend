import json

from flask import Blueprint, redirect, request

from libs.admin_authentication import authenticate_admin_study_access
from pipeline.boto_helpers import get_boto_client


data_pipeline = Blueprint('data_pipeline', __name__)


@data_pipeline.route('/run-manual-code', methods=["POST"])
@authenticate_admin_study_access
# AJK TODO annotate
def run_manual_code():
    client = get_boto_client('batch')
    with open('pipeline/aws-object-names.json') as fn:
        object_names = json.load(fn)

    # AJK TODO possibly use index.py post-merge (django-pipeline w/ pipeline) to reduce redundancy
    client.submit_job(
        jobName=object_names['job_name'].format(freq='manually'),
        jobDefinition=object_names['job_defn_name'],
        jobQueue=object_names['queue_name'],
        containerOverrides={
            'command': [
                '/bin/bash',
                'runner.sh',
                'Beiwe-Analysis/Pipeline/manually',
            ]
        }
    )
    
    study_id = request.values['study_id']
    # AJK TODO pass study id to job
    return redirect('/data-pipeline/{:s}'.format(study_id))
