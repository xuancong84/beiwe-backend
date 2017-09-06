# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# AJK TODO create other models and Foreign Keys: Admin, Participant, Survey, StudyDeviceSettings
# AJK TODO create file processing models and FKs: ChunkRegistry, FileToProcess
# AJK TODO create profiling models (see db/profiling.py)
# AJK TODO when all that is done, collapse migrations


# Create your models here.
class Study(models.Model):
    name = models.CharField(max_length=128, null=False)
    # admins
    # super_admins
    # surveys
    # device_settings
    encryption_key = models.CharField(max_length=128, null=False)
    deleted = models.BooleanField(default=False)