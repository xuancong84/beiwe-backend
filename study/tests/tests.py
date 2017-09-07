from pprint import pprint

from django.test import TestCase
from study.models import Researcher


class DataAccessModelTests(TestCase):
    
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
    

class ResearcherModelTests(TestCase):
    
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
    
    @property
    def create_django_reference_researcher(self):
        return Researcher(**self.translated_reference_researcher)
    
    def compare_researcher(self, researcher):
        ignore = ["deleted", "id"]
        return compare_dictionaries(self.translated_reference_researcher, researcher, ignore=ignore)
    
    # Researcher Tests
    def test_researcher_mongo_integrity(self):
        researcher = self.create_django_reference_researcher
        self.assertTrue(self.compare_researcher(researcher.as_native_python()))
    
    def test_researcher_create_with_password(self): pass

    def test_researcher_check_password(self): pass
        
    def test_researcher_validate_password(self):pass
        
    def test_researcher_set_password(self): pass
        
    def test_researcher_elevate_to_admin(self): pass
        
    def test_researcher_validate_access_credentials(self): pass
        
    def test_researcher_reset_access_credentials(self): pass


class ParticipantModelTests(TestCase):
    
    # Participant tests
    def test_participant_create(self): pass
    
    def test_participant_debug_validate_password(self): pass

    def test_participant_validate_password(self): pass
    
    def test_participant_reset_password(self): pass
    
    def test_participant_set_device(self): pass
    
    def test_participant_set_os_type(self): pass
    
    def test_participant_clear_device(self): pass
    
    def test_participant_set_password(self): pass


class StudyModelTests(TestCase):
    
    # Study model tests:
    def test_add_researcher(self): pass
    
    def test_remove_researcher(self): pass
    
    def test_add_survey(self): pass
    
    def test_remove_survey(self): pass
    
    def test_get_surveys_for_study(self): pass
    
    def test_get_survey_ids_for_study(self): pass
    
    def test_get_study_device_settings(self): pass
    
    # Survey model tests:
    def test_survey_create_with_settings(self): pass
        # this one is potentially complex and therefore needs a test.
    

class ProfilingModelTests(TestCase):
    
    # Upload model tests
    def test_get_trailing(self): pass
    
    def test_get_trailing_count(self): pass
    
    def test_weekly_stats(self): pass
    
    
    # DecryptionKeyError tests
    def decode(self): pass
    
    
    
def compare_dictionaries(reference, comparee, ignore=None):
    
    if ignore is None:
        ignore = []
    
    b = set((x, y) for x,y in comparee.iteritems() if x not in ignore)
    a = set((x, y) for x,y in reference.iteritems() if x not in ignore)
    
    differences_a = a - b
    differences_b = b - a
    if len(differences_a) == 0 and len(differences_b) == 0:
        return True

    print "These dictionaries are not identical:"
    
    try:
        differences_a = sorted(differences_a)
        differences_b = sorted(differences_b)
    except Exception:
        pass
    
    if differences_a:
        print "in reference, not in comparee:"
        for x,y in differences_a:
            print "\t", x, y
    if differences_b:
        print "in comparee, not in reference:"
        for x, y in differences_b:
            print "\t", x, y

    return False