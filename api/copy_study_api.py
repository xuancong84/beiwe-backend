from bson.json_util import dumps, loads
from bson.objectid import ObjectId
from flask import Blueprint, flash, redirect, request, Response

from db.study_models import Study, StudyDeviceSettings, Survey
from libs.admin_authentication import authenticate_system_admin
from libs.copy_study import add_new_surveys, allowed_filename, update_device_settings

copy_study_api = Blueprint('copy_study_api', __name__)

""" JSON structure for exporting and importing study surveys and settings:
    {
     'device_settings': {},
     'surveys': [{}, {}, ...]
    }
    Also, purge all _id keys! """


@copy_study_api.route('/export_study_settings_file/<string:study_id>', methods=['GET'])
@authenticate_system_admin
def export_study_settings_file(study_id):
    study = Study(ObjectId(study_id))
    filename = study['name'].replace(' ', '_') + "_surveys_and_settings.json"
    output = {'surveys': []}
    output['device_settings'] = StudyDeviceSettings(study['device_settings'])
    for survey_id in study['surveys']:
        output['surveys'].append(Survey(survey_id))
    return Response(dumps(output),
                    mimetype="application/json",
                    headers={'Content-Disposition':'attachment;filename=' + filename})


@copy_study_api.route('/import_study_settings_file/<string:study_id>', methods=['POST'])
@authenticate_system_admin
def import_study_settings_file(study_id):
    study = Study(ObjectId(study_id))
    file = request.files['upload']
    if not allowed_filename(file.filename):
        flash("You can only upload .json files!", 'danger')
        return redirect(request.referrer)
    study_data = loads(file.read())
    msg = update_device_settings(study_data['device_settings'], study, file.filename)
    msg += " \n" + add_new_surveys(study_data['surveys'], study, file.filename)
    flash(msg, 'success')
    return redirect('/edit_study/' + str(study_id))
