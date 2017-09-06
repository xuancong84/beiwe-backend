# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# AJK TODO create other models and Foreign Keys: Admin, Participant, Survey, StudyDeviceSettings
# AJK TODO create file processing models and FKs: ChunkRegistry, FileToProcess
# AJK TODO create profiling models (see db/profiling.py)
# AJK TODO when all that is done, collapse migrations


# AJK TODO add annotations and help_texts
class Study(models.Model):
    name = models.CharField(max_length=128)
    encryption_key = models.CharField(max_length=128)
    deleted = models.BooleanField(default=False)


class Survey(models.Model):
    content = []  # probably a JSON blob
    timings = []  # int-list of length 7. maybe also a JSON blob
    survey_type = []  # char field, choice between 'audio_survey' and 'tracking_survey' <-- make these local
                      # constants, null=False
    settings = []  # JSON blob

    study = models.ForeignKey('Study', on_delete=models.CASCADE, related_name='surveys')


class Participant(models.Model):
    patient_id = []  # char field, unique, max=8 (min=8)  # replacing the PK
    device_id = []  # char field? FK?
    os_type = []  # char field, choice between 'ANDROID' and 'IOS', null=True
    password = []  # use Django passwords for this
    salt = []  # see above

    study = models.ForeignKey('Study', on_delete=models.CASCADE, related_name='participants')


class Admin(models.Model):
    admin_name = []  # char field, unique, e.g. JP, Eli, etc.  # replacing the PK
    system_admin = models.BooleanField(default=False)
    password = []  # use Django passwords
    salt = []  # ditto
    access_key_id = []  # uh maybe make a model for this?
    access_key_secret = []
    access_key_secret_salt = []

    studies = models.ManyToManyField('Study', related_name='admins')
    super_studies = models.ManyToManyField('Study', related_name='super_admins')  # This is not currently used
