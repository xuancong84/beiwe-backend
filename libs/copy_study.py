from os import path

from bson.objectid import ObjectId
from flask import flash, request

# Mongolia models
from db.study_models import Study, StudyDeviceSettings, Survey

# Django models
from study.models import Survey as DSurvey


def copy_existing_study_if_asked_to(new_study):
    if ((request.form.get('copy_existing_study') == "true") and
            (ObjectId.is_valid(request.form.get('existing_study_id')))):
        old_study = Study(ObjectId(request.form.get('existing_study_id')))
        msg = update_device_settings(StudyDeviceSettings(old_study['device_settings']),
                               new_study, old_study['name'])
        surveys_to_copy = [Survey(survey_id) for survey_id in old_study['surveys']]
        msg += " \n" + add_new_surveys(surveys_to_copy, new_study, old_study['name'])
        flash(msg, 'success')


def allowed_filename(filename):
    """ Does filename end with ".json" (case-insensitive) """
    return path.splitext(filename)[1].lower() == '.json'


def update_device_settings(new_device_settings, study, filename):
    if request.form.get('device_settings') == "true":
        # Don't copy the PK to the device settings to be updated
        new_device_settings.pop('id')
        study.device_settings.update(**new_device_settings)
        return "Overwrote %s's App Settings with the values from %s." % \
               (study.name, filename)
    else:
        return "Did not alter %s's App Settings." % study.name


def add_new_surveys(new_survey_settings, study, filename):
    surveys_added = 0
    audio_surveys_added = 0
    if request.form.get('surveys') == "true":
        for survey_settings in new_survey_settings:
            # Don't copy unique fields to the new Survey object
            survey_settings.pop('id')
            survey_settings.pop('object_id')
            DSurvey.create_with_object_id(study=study, **survey_settings)
            if survey_settings['survey_type'] == 'tracking_survey':
                surveys_added += 1
            elif survey_settings['survey_type'] == 'audio_survey':
                audio_surveys_added += 1

    return "Copied %i Surveys and %i Audio Surveys from %s to %s." % \
           (surveys_added, audio_surveys_added, filename, study.name)
