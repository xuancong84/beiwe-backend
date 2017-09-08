# Add the parent directory to the path in order to enable
# imports from sister directories
from os.path import abspath as _abspath
from sys import path as _path

_one_folder_up = _abspath(__file__).rsplit('/', 2)[0]
_path.insert(1, _one_folder_up)

import json

# Load the Django settings
from config import load_django

# Import Mongolia models
from db.study_models import StudyDeviceSettings as MSettings, Studies as MStudySet, Survey as MSurvey
from db.user_models import Admin as MAdmin, Users as MUserSet

# Import Django models
from study.models import (
    Researcher as DAdmin, DeviceSettings as DSettings, Participant as DUser,
    Study as DStudy, Survey as DSurvey
)


# Actual code begins here
# AJK TODO maximize for efficiency
# AJK TODO chunk bulk_creation, especially for the green models (ChunkRegistry, FileToProcess)
def migrate_studies():

    m_study_list = MStudySet()
    d_study_list = []
    study_referents = {}

    for m_study in m_study_list:
        # Create a Django Study object modeled off the Mongolia Study
        study_name = m_study['name']
        d_study = DStudy(
            name=study_name,
            encryption_key=m_study['encryption_key'],
            deleted=m_study['deleted'],
        )

        # Validate the new Study object and add it to the bulk create list
        # AJK TODO should I catch this exception?
        d_study.full_clean()
        d_study_list.append(d_study)

        # Get lists of Mongolia Surveys, Admins and StudyDeviceSettings attached to this Study
        m_survey_list = m_study['surveys']
        m_admin_list = m_study['admins']
        m_device_settings = m_study['device_settings']
        study_referents[study_name] = {
            'survey_list': m_survey_list,
            'admin_list': m_admin_list,
            'device_settings': m_device_settings,
        }

    # Bulk create the Django Studies
    DStudy.objects.bulk_create(d_study_list)

    # Create a reference from Mongolia Study IDs to Django Studies that doesn't require
    # any future database calls.
    study_id_dict = {}
    for m_study in m_study_list:
        m_study_id = m_study['_id']
        d_study_id = DStudy.objects.filter(name=m_study['name']).values('pk', 'deleted').get()
        study_id_dict[m_study_id] = d_study_id

    return study_referents, study_id_dict


def migrate_surveys_admins_and_settings(study_referents):

    m_admin_duplicate_set = set()
    d_study_admin_list = []  # A list of studies and their researchers
    d_admin_list = []
    d_survey_list = []
    d_settings_list = []

    for study_name, object_ids in study_referents.iteritems():
        m_admin_id_list = object_ids['admin_list']
        m_survey_id_list = object_ids['survey_list']
        m_settings_id = object_ids['device_settings']
        d_study = DStudy.objects.get(name=study_name)

        # Create a new element in the Study-Researcher list for d_study
        d_study_admin_list.append([d_study, []])

        for m_survey_id in m_survey_id_list:
            # Build a Django Survey matching the Mongolia Survey
            m_survey = MSurvey(m_survey_id)
            if not m_survey:
                # AJK TODO this is in case the survey does not exist
                # This is probably not a long-term solution
                continue
            d_survey = DSurvey(
                content=json.dumps(m_survey['content']),
                survey_type=m_survey['survey_type'],
                settings=json.dumps(m_survey['settings']),
                timings=json.dumps(m_survey['timings']),
                study_id=d_study.pk,
                deleted=d_study.deleted,
            )

            # Validate the new Survey and add it to the bulk_create list
            d_survey.full_clean()
            d_survey_list.append(d_survey)

        for m_admin_id in m_admin_id_list:
            # Add the Researcher to d_study's list of researchers
            d_study_admin_list[-1][1].append(m_admin_id)

            # If the Researcher has not yet been built, build it
            if m_admin_id not in m_admin_duplicate_set:
                m_admin = MAdmin(m_admin_id)
                d_admin = DAdmin(
                    username=m_admin_id,
                    admin=m_admin['system_admin'],
                    access_key_id=m_admin['access_key_id'],
                    access_key_secret=m_admin['access_key_secret'],
                    access_key_secret_salt=m_admin['access_key_secret_salt'],
                    password=m_admin['password'],
                    salt=m_admin['salt'],
                    deleted=d_study.deleted,
                )
                m_admin_duplicate_set.add(m_admin_id)

                # Validate the Researcher and add it to the bulk_create list
                d_admin.full_clean()
                d_admin_list.append(d_admin)

        # Build a new DeviceSettings object
        m_settings = MSettings(m_settings_id)
        d_settings = DSettings(
            accelerometer=m_settings['accelerometer'],
            gps=m_settings['gps'],
            calls=m_settings['calls'],
            texts=m_settings['texts'],
            wifi=m_settings['wifi'],
            bluetooth=m_settings['bluetooth'],
            power_state=m_settings['power_state'],
            proximity=m_settings['proximity'],
            gyro=m_settings['gyro'],
            magnetometer=m_settings['magnetometer'],
            devicemotion=m_settings['devicemotion'],
            reachability=m_settings['reachability'],
            allow_upload_over_cellular_data=m_settings['allow_upload_over_cellular_data'],
            accelerometer_off_duration_seconds=m_settings['accelerometer_off_duration_seconds'],
            accelerometer_on_duration_seconds=m_settings['accelerometer_on_duration_seconds'],
            bluetooth_on_duration_seconds=m_settings['bluetooth_on_duration_seconds'],
            bluetooth_total_duration_seconds=m_settings['bluetooth_total_duration_seconds'],
            bluetooth_global_offset_seconds=m_settings['bluetooth_global_offset_seconds'],
            check_for_new_surveys_frequency_seconds=m_settings['check_for_new_surveys_frequency_seconds'],
            create_new_data_files_frequency_seconds=m_settings['create_new_data_files_frequency_seconds'],
            gps_off_duration_seconds=m_settings['gps_off_duration_seconds'],
            gps_on_duration_seconds=m_settings['gps_on_duration_seconds'],
            seconds_before_auto_logout=m_settings['seconds_before_auto_logout'],
            upload_data_files_frequency_seconds=m_settings['upload_data_files_frequency_seconds'],
            voice_recording_max_time_length_seconds=m_settings['voice_recording_max_time_length_seconds'],
            wifi_log_frequency_seconds=m_settings['wifi_log_frequency_seconds'],
            gyro_off_duration_seconds=m_settings['gyro_off_duration_seconds'],
            gyro_on_duration_seconds=m_settings['gyro_on_duration_seconds'],
            magnetometer_off_duration_seconds=m_settings['magnetometer_off_duration_seconds'],
            magnetometer_on_duration_seconds=m_settings['magnetometer_on_duration_seconds'],
            devicemotion_off_duration_seconds=m_settings['devicemotion_off_duration_seconds'],
            devicemotion_on_duration_seconds=m_settings['devicemotion_on_duration_seconds'],
            about_page_text=m_settings['about_page_text'],
            call_clinician_button_text=m_settings['call_clinician_button_text'],
            consent_form_text=m_settings['consent_form_text'],
            survey_submit_success_toast_text=m_settings['survey_submit_success_toast_text'],
            consent_sections=m_settings['consent_sections'],
            study_id=d_study.pk,
            deleted=d_study.deleted,
        )

        d_settings_list.append(d_settings)

    # Bulk_create the three sets of objects built above
    DAdmin.objects.bulk_create(d_admin_list)
    DSurvey.objects.bulk_create(d_survey_list)
    DSettings.objects.bulk_create(d_settings_list)

    # Now that the Researchers have primary keys, fill in the Study-Researcher ManyToMany relationship
    for study, admin_username_list in d_study_admin_list:
        admin_id_set = DAdmin.objects.filter(username__in=admin_username_list).values_list('pk', flat=True)
        study.researchers.add(*admin_id_set)  # add takes *args, not an iterable


def migrate_users(study_id_dict):

    m_user_list = MUserSet()[:18]
    d_user_list = []

    for m_user in m_user_list:

        # Get information about the Participant's Study
        m_study_id = m_user['study_id']
        d_study_info = study_id_dict[m_study_id]

        # Django convention is to use the empty string rather than None in CharFields
        device_id = m_user['device_id'] or ''
        os_type = m_user['os_type'] or ''

        # Build a new Django Participant
        d_user = DUser(
            patient_id=m_user['_id'],
            device_id=device_id,
            os_type=os_type,
            study_id=d_study_info['pk'],
            password=m_user['password'],
            salt=m_user['salt'],
            deleted=d_study_info['deleted'],
        )

        # Validate the Participant and add it to the bulk_create list
        d_user.full_clean()
        d_user_list.append(d_user)

    # Bulk_create the Participants
    DUser.objects.bulk_create(d_user_list)


def run_all_migrations():
    """
    A function that runs all the other functions. This is to prevent any of the variables
    being passed through here from being global and possibly causing issues in the other
    functions.
    """
    study_referents, study_id_dict = migrate_studies()
    migrate_surveys_admins_and_settings(study_referents)
    migrate_users(study_id_dict)


if __name__ == '__main__':
    print(DStudy.objects.count(), DUser.objects.count())
    run_all_migrations()
    print(DStudy.objects.count(), DUser.objects.count())
