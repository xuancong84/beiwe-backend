from bson import ObjectId
import json

from django.test import TestCase

from study.models import Researcher, Study, Survey, DeviceSettings, Participant

# Fields that we don't fill in in translation to django types.
class ReferenceReversed(Exception): pass
class IsMongoID(Exception): pass
class ReferenceRequired(Exception): pass


class CommonTestCase(TestCase):
    
    # Researcher
    @property
    def reference_researcher(self):
        """ Provide a copy of a reference object sourced from the original mongo database. """
        return {
            '_id': 'researcher',
            # this password should be single space
            'password': 'YCPk2RR8y6aJAB26vZQYieuYBr22GnNv52QLZ9swy_4=',
            'salt': '5_OlsDQ8V7JJyz3_LMIrQA==',
            # Data Access credentials
            'access_key_id': 'iJAqxDDgOC9Ca4/upLoy4HosTY4W67uqn5gdAX85DL2/yoJeJaL4WNtzmTIdoTc7',
            'access_key_secret_salt': 'aOV-pHBgbMOYk1j823Y_ng==',
            'access_key_secret': 'vQfRU8pYHm0PcNMr-sGYufVWV5rd1pNOzzg3LiCOQb4=',
            # not a system admin
            'system_admin': False
        }
    
    @property
    def translated_reference_researcher(self):
        researcher = self.reference_researcher
        researcher['username'] = researcher.pop('_id')
        researcher['admin'] = researcher.pop('system_admin')
        return researcher
    
    # Participant
    @property
    def reference_participant(self):
        return {
            '_id': "someparticipant7",
            'device_id': '_xjeWARoRevoDoL9OKDwRMpYcDhuAxm4nwedUgABxWA=',
            'password': '2oWT7-6Su2WMDRWpclT0q2glam7AD5taUzHIWRnO490=',
            'salt': '1NB2kCxOOYzayIYGZYlhHw==',
            'study_id': ReferenceRequired,
            'os_type': "ANDROID"
        }

    @property
    def translated_reference_participant(self):
        participant = self.reference_participant
        participant.pop('study_id')  # is a reference, and renamed to Study
        participant["patient_id"] = participant.pop('_id')
        return participant
    
    
    # Study
    @property
    def reference_study(self):
        return {
            'name': 'something, anything',
            'encryption_key': '12345678901234567890123456789012',
            'deleted': False,
            '_id': ObjectId('556677889900aabbccddeeff'),
            # The rest are refactored totally
            'admins': ReferenceReversed,
            'device_settings': ReferenceReversed,
            'super_admins': ReferenceReversed,
            'surveys': ReferenceReversed
        }

    @property
    def translated_reference_study(self):
        reference_study = self.reference_study
        reference_study["object_id"] = str(reference_study.pop("_id"))
        reference_study.pop("admins")
        reference_study.pop("super_admins")
        reference_study.pop("surveys")
        reference_study.pop("device_settings")
        return reference_study
    
    # Survey
    @property
    def reference_survey(self):
        return {
            '_id': IsMongoID,
            'content': [{'prompt': ''}],
            'settings': {'audio_survey_type': 'compressed',
                          'bit_rate': 64000,
                          'trigger_on_first_download': True},
            'survey_type': 'audio_survey',
            'timings': [[], [], [], [], [], [], []]
        }


    @property
    def translated_reference_survey(self):
        survey = self.reference_survey
        survey.pop("_id")
        survey["timings"] = json.dumps(survey.pop("timings"))
        survey["content"] = json.dumps(survey.pop("content"))
        survey["settings"] = json.dumps(survey.pop("settings"))
        return survey

    @property
    def reference_device_settings(self):
        return {
            '_id': IsMongoID,
            'about_page_text': "irrelevant string 1",
            'accelerometer': True,
            'accelerometer_off_duration_seconds': 10,
            'accelerometer_on_duration_seconds': 10,
            'allow_upload_over_cellular_data': False,
            'bluetooth': False,
            'bluetooth_global_offset_seconds': 0,
            'bluetooth_on_duration_seconds': 60,
            'bluetooth_total_duration_seconds': 300,
            'call_clinician_button_text': "irrelevant string 2",
            'calls': True,
            'check_for_new_surveys_frequency_seconds': 21600,
            'consent_form_text': "irrelevant string 3",
            'consent_sections': "{}", # needs to be a de/serializeable json object
            'create_new_data_files_frequency_seconds': 900,
            'devicemotion': False,
            'devicemotion_off_duration_seconds': 600,
            'devicemotion_on_duration_seconds': 60,
            'gps': True,
            'gps_off_duration_seconds': 600,
            'gps_on_duration_seconds': 60,
            'gyro': False,
            'gyro_off_duration_seconds': 600,
            'gyro_on_duration_seconds': 60,
            'magnetometer': False,
            'magnetometer_off_duration_seconds': 600,
            'magnetometer_on_duration_seconds': 60,
            'power_state': True,
            'proximity': False,
            'reachability': True,
            'seconds_before_auto_logout': 600,
            'survey_submit_success_toast_text': "irrelevant string 4",
            'texts': True,
            'upload_data_files_frequency_seconds': 3600,
            'voice_recording_max_time_length_seconds': 240,
            'wifi': True,
            'wifi_log_frequency_seconds': 300
        }

    @property
    def translated_reference_device_settings(self):
        settings = self.reference_device_settings
        settings.pop("_id")
        return settings


class ResearcherModelTests(CommonTestCase):
    
    # Researcher Tests
    def test_researcher_mongo_integrity(self):
        researcher = Researcher(**self.translated_reference_researcher)
        x = compare_dictionaries(self.translated_reference_researcher,
                                 researcher.as_native_python(),
                                 ignore=["deleted", "id"])
        self.assertTrue(x)
    
    def test_researcher_create_with_password(self): pass

    def test_researcher_check_password(self): pass
        
    def test_researcher_validate_password(self):pass
        
    def test_researcher_set_password(self): pass
        
    def test_researcher_elevate_to_admin(self): pass
        
    def test_researcher_validate_access_credentials(self): pass
        
    def test_researcher_reset_access_credentials(self): pass


class ParticipantModelTests(CommonTestCase):
    
    def test_participant_mongo_integrity(self):
        study = Study(**self.translated_reference_study)
        study.save()
    
        reference_participant = self.translated_reference_participant
        django_participant = Participant(study=study,
                                         **reference_participant).as_native_python()
        
        x = compare_dictionaries(reference_participant,
                                 django_participant,
                                 ignore=['id', 'deleted'])
        self.assertTrue(x)
    
    # Participant tests
    def test_participant_create(self): pass
    
    def test_participant_debug_validate_password(self): pass

    def test_participant_validate_password(self): pass
    
    def test_participant_reset_password(self): pass
    
    def test_participant_set_device(self): pass
    
    def test_participant_set_os_type(self): pass
    
    def test_participant_clear_device(self): pass
    
    def test_participant_set_password(self): pass


class StudyModelTests(CommonTestCase):
    
    def test_study_mongo_integrity(self):
        django_reference_study = Study(**self.translated_reference_study)
        x = compare_dictionaries(self.translated_reference_study,
                                 django_reference_study.as_native_python(),
                                 ignore=['id'])
        self.assertTrue(x)
    
    # Study model tests:
    def test_add_researcher(self): pass
    
    def test_remove_researcher(self): pass
    
    def test_add_survey(self): pass
    
    def test_remove_survey(self): pass
    
    def reference_participant(self): pass
    
    def translated_reference_participant(self): pass
    
    def create_django_reference_participant(self): pass
    
    def compare_participant(self, researcher): pass


class SurveyModelTests(CommonTestCase):
    
    def test_survey_mongo_integrity(self):
        study = Study(**self.translated_reference_study)
        study.save()
        
        mongo_reference_survey = self.translated_reference_survey
        mongo_reference_survey['study'] = study
        
        django_reference_survey = Survey(study=study, **self.translated_reference_survey)
        
        # This comparison requires the as_dict comparison because it has jsonfields
        x = compare_dictionaries(mongo_reference_survey,
                                 django_reference_survey.as_dict(),
                                 ignore=['deleted', 'id'])
        self.assertTrue(x)

    def test_get_surveys_for_study(self): pass
    
    def test_get_survey_ids_for_study(self): pass
    
    def test_get_study_device_settings(self): pass

    # Survey model tests:
    def test_survey_create_with_settings(self): pass
        # this one is potentially complex and therefore needs a test.


class DeviceSettingsTests(CommonTestCase):
    def test_settings_mongo_integrity(self):
        study = Study(**self.translated_reference_study)
        study.save()
        
        mongo_reference_settings = self.translated_reference_device_settings
        mongo_reference_settings['study'] = study
        django_settings = DeviceSettings(**mongo_reference_settings)
        x = compare_dictionaries(mongo_reference_settings,
                                 django_settings.as_dict(),
                                 ignore=['deleted', 'id'])
        self.assertTrue(x)


class DataAccessModelTests(CommonTestCase):
    # ChunkRegistry model tests:
    def test_add_new_chunk(self): pass
    
    def test_update_chunk_hash(self): pass
    
    def test_low_memory_update_chunk_hash(self): pass
    
    def test_get_chunks_time_range(self): pass
    
    # FileProcessLock tests:
    def test_lock(self): pass
    
    def test_unlock(self): pass
    
    def test_islocked(self): pass
    
    def test_get_time_since_locked(self): pass


class ProfilingModelTests(CommonTestCase):
    
    # Upload model tests
    def test_get_trailing(self): pass
    
    def test_get_trailing_count(self): pass
    
    def test_weekly_stats(self): pass
    
    
    # DecryptionKeyError tests
    def decode(self): pass
    
    
    
def compare_dictionaries(reference, comparee, ignore=None):
    if not isinstance(reference, dict):
        raise Exception("reference was %s, not dictionary" % type(reference))
    if not isinstance(comparee, dict):
        raise Exception("comparee was %s, not dictionary" % type(comparee))
    
    if ignore is None:
        ignore = []
    
    b = set((x, y) for x,y in comparee.iteritems() if x not in ignore)
    a = set((x, y) for x,y in reference.iteritems() if x not in ignore)
    differences_a = a - b
    differences_b = b - a
    
    if len(differences_a) == 0 and len(differences_b) == 0:
        return True
    
    try:
        differences_a = sorted(differences_a)
        differences_b = sorted(differences_b)
    except Exception:
        pass

    print "These dictionaries are not identical:"
    if differences_a:
        print "in reference, not in comparee:"
        for x,y in differences_a:
            print "\t", x, y
    if differences_b:
        print "in comparee, not in reference:"
        for x, y in differences_b:
            print "\t", x, y

    return False