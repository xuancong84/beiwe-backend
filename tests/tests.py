# nosetests -v --nocapture
import unittest

# import flask
# app = flask.Flask(__name__)

from db import data_access_models, user_models, study_models, profiling

class DataAccessModelTests(unittest.TestCase):
    
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
    

class UserModelTests(unittest.TestCase):
    
    # Participant tests
    def test_participant_create(self): pass
    
    def test_participant_validate_password(self): pass
    
    def test_participant_debug_validate_password(self): pass
    
    def test_participant_reset_password(self): pass
    
    def test_participant_set_device(self): pass
    
    def test_participant_set_os_type(self): pass
    
    def test_participant_clear_device(self): pass
    
    def test_participant_set_password(self): pass
    
    
    # Admin Tests
    def test_admin_create(self): pass

    def test_admin_check_password(self): pass
        
    def test_admin_validate_password(self): pass
        
    def test_admin_set_password(self): pass
        
    def test_admin_elevate_to_system_admin(self): pass
        
    def test_admin_validate_access_credentials(self): pass
        
    def test_admin_reset_access_credentials(self): pass


class StudyModelTests(unittest.TestCase):
    
    # Study model tests:
    def test_create_default_study(self): pass
    
    def test_add_admin(self): pass
    
    def test_remove_admin(self): pass
    
    def test_add_survey(self): pass
    
    def test_remove_survey(self): pass
    
    def test_get_surveys_for_study(self): pass
    
    def test_get_survey_ids_for_study(self): pass
    
    def test_get_study_device_settings(self): pass
    
    
    # StudyDeviceSettings model tests:
    def test_create_default(self):   pass
        # does this even need a test? the django default values work.
    
    # Survey model tests:
    def test_create_default_survey(self): pass
        # this one is potentially complex and therefore needs a test.
    

class ProfilingModelTests(unittest.TestCase):
    
    # Upload model tests
    def test_get_trailing(self): pass
    
    def test_get_trailing_count(self): pass
    
    def test_weekly_stats(self): pass
    
    
    # DecryptionKeyError tests
    def decode(self): pass