# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Study(models.Model):
    name = models.CharField(max_length=128, null=False)
    # admins
    # super_admins
    # surveys
    # device_settings
    encryption_key = models.CharField(max_length=128, null=False)
    deleted = models.BooleanField(default=False)