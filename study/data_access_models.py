# AJK TODO not clear how exactly I want to do this. Options include:
# 1. have multiple Django apps (be sure to rename the ForeignKeys in that case)
# B. make a single /models directory and put several X_models.py files in it, then have models.py call them all
# iii. keep everything in one models.py file (this seems like a bad idea)

from django.db import models


class ChunkRegistry(models.Model):

    # {u'audio_recordings', u'gps', u'identifiers', u'power_state', u'proximity', u'reachability', u'survey_answers',
    #  u'survey_timings'} and others. It's in a constants file.
    DATA_TYPE_CHOICES = (('stuff', 'things'),)

    # AJK TODO rearrange these in logical order rather than alphabetical
    # AJK TODO add validators, make this subclass AbstractModel (requires some refactoring)
    chunk_hash = models.CharField(max_length=25, blank=True)
    chunk_path = models.CharField(max_length=256)
    data_type = models.CharField(max_length=32, choices=DATA_TYPE_CHOICES, db_index=True)
    is_chunkable = models.BooleanField()
    time_bin = models.DateTimeField(db_index=True)

    study = models.ForeignKey('Study', on_delete=models.PROTECT, related_name='chunk_registries', db_index=True)
    participant = models.ForeignKey('Participant', on_delete=models.PROTECT, related_name='chunk_registries', db_index=True)
    survey = models.ForeignKey('Survey', on_delete=models.PROTECT, related_name='chunk_registries', db_index=True)


class FileToProcess(models.Model):

    # AJK TODO maybe add a validator that it's a valid S3 path or at least looks like a filepath ([0-9a-zA-z/]+\.csv)
    s3_file_path = models.CharField(max_length=256, blank=False)

    # AJK TODO do I need to make these indexes?
    study = models.ForeignKey('Study', on_delete=models.PROTECT, related_name='files_to_process')
    participant = models.ForeignKey('Participant', on_delete=models.PROTECT, related_name='files_to_process')
