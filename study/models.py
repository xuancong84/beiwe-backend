# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.code.validators import RegexValidator

# AJK TODO create file processing models and FKs: ChunkRegistry, FileToProcess
# AJK TODO create profiling models (see db/profiling.py)
# AJK TODO when all that is done, collapse migrations
# AJK TODO move from the installed pbkdf2 to the python 2.7.10+ builtin, and
# test that everything still works.


# AJK TODO add annotations and help_texts
# AJK TODO reorder fields cleanly
class Study(models.Model):
    name = models.CharField(max_length=128)
    encryption_key = models.CharField(max_length=128)
    deleted = models.BooleanField(default=False)


# AJK TODO this should be subsumed into Study -- bring up first with Eli
# class DeviceSettings(models.Model):
#     contents = []  # JSON blob
#     study = models.OneToOneField('Study', on_delete=models.CASCADE, related_name='device_settings')


class Survey(models.Model):
    AUDIO = 'audio'
    TRACKING = 'tracking'
    SURVEY_TYPE_CHOICES = (
        (AUDIO, 'audio_survey'),
        (TRACKING, 'tracking_survey'),
    )

    content = models.TextField(help_text='JSON blob containing information about the survey questions')
    timings = []  # int-list of length 7. maybe also a JSON blob, maybe a seven-part field
    survey_type = models.CharField(max_length=8, choices=SURVEY_TYPE_CHOICES)
    settings = models.TextField(help_text='JSON blob containing settings for the survey')

    study = models.ForeignKey('Study', on_delete=models.CASCADE, related_name='surveys')


class Participant(models.Model):
    ANDROID = 'ANDROID'
    IOS = 'IOS'
    OS_TYPE_CHOICES = (
        (ANDROID, 'ANDROID'),
        (IOS, 'IOS'),
    )

    id_validator = RegexValidator('^[1-9a-z]{8}$', message='Invalid Participant ID')
    patient_id = models.CharField(max_length=8, unique=True, validators=[id_validator],
                                  help_text='Eight-character unique ID with characters chosen from 1-9 and a-z')

    device_id = models.CharField(
        max_length=64,
        help_text='The ID of the device that the participant is using for the study, provided by the mobile API.',
    )
    os_type = models.CharField(max_length=7, choices=OS_TYPE_CHOICES, null=True)

    # AJK TODO look into doing password stuff automatically through Django:
    # https://docs.djangoproject.com/en/1.11/topics/auth/passwords/
    password = []
    salt = []

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
