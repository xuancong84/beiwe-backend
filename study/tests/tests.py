from django.test import TestCase


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
    
    # Participant tests
    def test_participant_create_with_password(self): pass
    
    def test_participant_validate_password(self): pass
    
    def test_participant_debug_validate_password(self): pass
    
    def test_participant_reset_password(self): pass
    
    def test_participant_set_device(self): pass
    
    def test_participant_set_os_type(self): pass
    
    def test_participant_clear_device(self): pass
    
    def test_participant_set_password(self): pass
    
    
    # Researcher Tests
    def test_researcher_create_with_password(self): pass

    def test_researcher_check_password(self): pass
        
    def test_researcher_validate_password(self): pass
        
    def test_researcher_set_password(self): pass
        
    def test_researcher_elevate_to_admin(self): pass
        
    def test_researcher_validate_access_credentials(self): pass
        
    def test_researcher_reset_access_credentials(self): pass


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