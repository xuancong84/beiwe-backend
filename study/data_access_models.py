from datetime import datetime

from django.db import models

from config.constants import ALL_DATA_STREAMS, CHUNKABLE_FILES, CHUNK_TIMESLICE_QUANTUM
from libs.security import chunk_hash, low_memory_chunk_hash
from study.base_models import AbstractModel
from study.study_models import Study


class FileProcessingLockedError(Exception): pass


class ChunkRegistry(AbstractModel):

    DATA_TYPE_CHOICES = tuple([(stream_name, stream_name) for stream_name in ALL_DATA_STREAMS])

    is_chunkable = models.BooleanField()
    chunk_path = models.CharField(max_length=256)
    chunk_hash = models.CharField(max_length=25, blank=True)

    data_type = models.CharField(max_length=32, choices=DATA_TYPE_CHOICES)  # , db_index=True)
    time_bin = models.DateTimeField()  # db_index=True)
    # AJK TODO check that time_bin is preserved in migration to POSTGRES

    study = models.ForeignKey('Study', on_delete=models.PROTECT, related_name='chunk_registries')  # , db_index=True)
    participant = models.ForeignKey('Participant', on_delete=models.PROTECT, related_name='chunk_registries')  # , db_index=True)
    survey = models.ForeignKey('Survey', blank=True, null=True, on_delete=models.PROTECT, related_name='chunk_registries')  # , db_index=True)

    @classmethod
    def add_new_chunk(cls, data_type, time_bin, file_contents=None, **kwargs):
        is_chunkable = data_type in CHUNKABLE_FILES
        if is_chunkable:
            time_bin = int(time_bin) * CHUNK_TIMESLICE_QUANTUM
            chunk_hash_str = chunk_hash(file_contents)
        else:
            chunk_hash_str = ''

        cls.objects.create(
            is_chunkable=is_chunkable,
            chunk_hash=chunk_hash_str,
            data_type=data_type,
            time_bin=datetime.fromtimestamp(time_bin),
            **kwargs
        )

    @classmethod
    def get_chunks_time_range(cls, study_id, user_ids=None, data_types=None, start=None, end=None):
        """
        This function uses Django query syntax to provide datetimes and have Django do the
        comparison operation, and the 'in' operator to have Django only match the user list
        provided.
        """

        query = {'study_id': study_id}
        if user_ids:
            query['participant__patient_id__in'] = user_ids
        if data_types:
            query['data_type__in'] = data_types
        if start:
            query['time_bin__gte'] = start
        if end:
            query['time_bin__lte'] = end
        return cls.objects.filter(**query)

    def update_chunk_hash(self, data_to_hash):
        self.chunk_hash = chunk_hash(data_to_hash)
        self.save()

    def low_memory_update_chunk_hash(self, list_data_to_hash):
        self.chunk_hash = low_memory_chunk_hash(list_data_to_hash)
        self.save()


class FileToProcess(AbstractModel):

    s3_file_path = models.CharField(max_length=256, blank=False)

    study = models.ForeignKey('Study', on_delete=models.PROTECT, related_name='files_to_process')
    participant = models.ForeignKey('Participant', on_delete=models.PROTECT, related_name='files_to_process')

    @classmethod
    def append_file_for_processing(cls, file_path, study_value, **kwargs):
        # Get the study's ID
        # AJK TODO depending how this is used in the codebase, stick with passing a single type of study_value
        if Study.objects.filter(object_id=study_value).exists():
            # A Study object_id was passed (as a string)
            study_pk = Study.objects.filter(object_id=study_value).values_list('pk', flat=True).get()
            study_object_id = study_value
        else:
            # A Study primary key was passed
            study_pk = study_value
            study_object_id = Study.objects.filter(pk=study_value).values_list('object_id', flat=True).get()

        if file_path[:24] == study_object_id:
            cls.objects.create(s3_file_path=file_path, study_id=study_pk, **kwargs)
        else:
            cls.objects.create(s3_file_path=study_object_id + '/' + file_path, study_id=study_pk, **kwargs)


class FileProcessLock(AbstractModel):
    
    lock_time = models.DateTimeField(null=True)
    
    # In case of weirdness, ensure that there is only one lock object
    is_actual_lock = models.BooleanField(unique=True, help_text="This is True if the Lock is actually a lock")
    
    @classmethod
    def lock(cls):
        if cls.islocked():
            raise FileProcessingLockedError('File processing already locked')
        else:
            cls.objects.create(lock_time=datetime.utcnow(), is_actual_lock=True)
    
    @classmethod
    def unlock(cls):
        cls.objects.all().delete()
    
    @classmethod
    def islocked(cls):
        return cls.objects.filter(is_actual_lock=True).exists()
    
    @classmethod
    def get_time_since_locked(cls):
        return datetime.utcnow() - FileProcessLock.objects.get(is_actual_lock=True).lock_time
