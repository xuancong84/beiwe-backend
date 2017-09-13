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
from db.data_access_models import ChunksRegistry as MChunks
from db.study_models import (
    StudyDeviceSettings as MSettings, Studies as MStudySet,
    Survey as MSurvey, Surveys as MSurveySet
)
from db.user_models import Admins as MAdminSet, Users as MUserSet

# Import Django models
from study.models import (
    Researcher as DAdmin, DeviceSettings as DSettings, Participant as DUser,
    Study as DStudy, Survey as DSurvey, ChunkRegistry as DChunks
)


# Actual code begins here
def migrate_studies():

    m_study_list = MStudySet.iterator()

    d_study_list = []
    study_referents = {}

    for m_study in m_study_list:
        # Create a Django Study object modeled off the Mongolia Study
        study_name = m_study['name']
        d_study = DStudy(
            name=study_name,
            encryption_key=m_study['encryption_key'],
            object_id=m_study['_id'],
            deleted=m_study['deleted'],
        )

        # Validate the new Study object and add it to the bulk create list
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
    for m_study in MStudySet.iterator():
        m_study_id = m_study['_id']
        d_study_id = DStudy.objects.filter(name=m_study['name']).values('pk', 'deleted').get()
        study_id_dict[m_study_id] = d_study_id

    return study_referents


def migrate_study_relationships(study_referents):

    d_survey_list = []
    d_settings_list = []

    for study_name, object_ids in study_referents.iteritems():
        m_admin_id_list = object_ids['admin_list']
        m_survey_id_list = object_ids['survey_list']
        m_settings_id = object_ids['device_settings']
        d_study = DStudy.objects.get(name=study_name)

        for m_survey_id in m_survey_id_list:
            # Build a Django Survey matching the Mongolia Survey
            m_survey = MSurvey(m_survey_id)
            if not m_survey:
                # AJK TODO this is in case the survey does not exist: ask Eli if this is reasonable
                continue
            d_survey = DSurvey(
                content=json.dumps(m_survey['content']),
                survey_type=m_survey['survey_type'],
                settings=json.dumps(m_survey['settings']),
                timings=json.dumps(m_survey['timings']),
                object_id=m_survey['_id'],
                study_id=d_study.pk,
                deleted=d_study.deleted,
            )

            # Validate the new Survey and add it to the bulk_create list
            d_survey.full_clean()
            d_survey_list.append(d_survey)

        for m_admin_id in m_admin_id_list:
            # Add the Study-Researcher pair to the list of pairs
            d_study_admin_list.append((d_study.pk, m_admin_id))

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
            consent_sections=json.dumps(m_settings['consent_sections']),
            study_id=d_study.pk,
            deleted=d_study.deleted,
        )

        d_settings_list.append(d_settings)
    
    # Bulk_create the two sets of objects built above
    DSurvey.objects.bulk_create(d_survey_list)
    DSettings.objects.bulk_create(d_settings_list)

    for m_survey in MSurveySet.iterator():
        m_survey_id = m_survey['_id']
        d_survey_id = DSurvey.objects.filter(object_id=m_survey['_id']).values('pk').get()
        survey_id_dict[m_survey_id] = d_survey_id


def migrate_admins():
    
    d_admin_list = []
    
    # Build all Researchers
    for m_admin in MAdminSet.iterator():
        d_admin = DAdmin(
            username=m_admin['_id'],
            admin=m_admin['system_admin'],
            access_key_id=m_admin['access_key_id'] or None,  # access_key_id is unique and therefore nullable
            access_key_secret=m_admin['access_key_secret'] or '',
            access_key_secret_salt=m_admin['access_key_secret_salt'] or '',
            password=m_admin['password'],
            salt=m_admin['salt'],
            deleted=False,
        )
        
        # Validate the Researcher and add it to the bulk_create list
        d_admin.full_clean()
        d_admin_list.append(d_admin)
    
    # Bulk_create the list of Researchers
    DAdmin.objects.bulk_create(d_admin_list)
    
    # Now that the Researchers have primary keys, fill in the Study-Researcher ManyToMany relationship
    # Create a mapping from Researcher's username to primary key
    admin_username_to_pk_dict = dict(DAdmin.objects.values_list('username', 'pk'))
    
    d_study_admin_relation_list = []
    for study_id, admin_username in d_study_admin_list:
        admin_id = admin_username_to_pk_dict[admin_username]
        # Populate a list of database objects in the Study-Researcher relationship table
        new_relation = DAdmin.studies.through(study_id=study_id, researcher_id=admin_id)
        d_study_admin_relation_list.append(new_relation)
        
    # Bulk_create the Study-Researcher relationship objects
    DAdmin.studies.through.objects.bulk_create(d_study_admin_relation_list)


def migrate_users():

    m_user_list = MUserSet.iterator()
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

    for m_user in MUserSet.iterator():
        m_user_id = m_user['_id']
        d_user_id = DUser.objects.filter(patient_id=m_user['_id']).values('pk').get()
        user_id_dict[m_user_id] = d_user_id


def migrate_chunk_registries():

    m_chunk_iter = MChunks.iterator()

    # Calculate the number of chunks that will be used to go through all of MChunks()
    num_chunks = (MChunks.count() // CHUNK_SIZE) + 1
    for _ in xrange(num_chunks):

        # Empty d_chunk_list to ensure low memory usage
        d_chunk_list = []
        for _ in xrange(CHUNK_SIZE):
            try:
                m_chunk = m_chunk_iter.next()
            except StopIteration:
                # If the iterator is out of MChunk objects
                break

            d_study_info = study_id_dict[m_chunk.study_id]
            d_user_info = user_id_dict[m_chunk.user_id]
            if m_chunk.survey_id in survey_id_dict:
                d_survey_info = survey_id_dict[m_chunk.survey_id]
            else:
                # If there is no such survey, either because the MChunk has no MSurvey
                # or because it has one that has been deleted.
                # AJK TODO ask Eli if there's something else I should do in case 2
                d_survey_info = {'pk': None}

            chunk_hash = m_chunk.chunk_hash or ''

            d_chunk = DChunks(
                is_chunkable=m_chunk.is_chunkable,
                chunk_path=m_chunk.chunk_path,
                chunk_hash=chunk_hash,
                data_type=m_chunk.data_type,
                time_bin=m_chunk.time_bin,
                study_id=d_study_info['pk'],
                participant_id=d_user_info['pk'],
                survey_id=d_survey_info['pk'],
                deleted=d_study_info['deleted'],
            )

            d_chunk.full_clean()
            d_chunk_list.append(d_chunk)

        DChunks.objects.bulk_create(d_chunk_list)


def run_all_migrations():
    study_referents = migrate_studies()
    migrate_study_relationships(study_referents)
    migrate_admins()
    migrate_users()
    migrate_chunk_registries()


if __name__ == '__main__':
    study_id_dict = {}
    user_id_dict = {}
    survey_id_dict = {}
    d_study_admin_list = []  # A list of study-researcher pairs
    
    CHUNK_SIZE = 1000
    
    print(DStudy.objects.count(), DUser.objects.count(), DChunks.objects.count())
    run_all_migrations()
    print(DStudy.objects.count(), DUser.objects.count(), DChunks.objects.count())
