# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.db import models
from django.core.validators import RegexValidator

from study.text_constants import (
    ABOUT_PAGE_TEXT, CONSENT_FORM_TEXT, DEFAULT_CONSENT_SECTIONS_JSON,
    SURVEY_SUBMIT_SUCCESS_TOAST_TEXT
)

# AJK TODO create file processing models and FKs: ChunkRegistry, FileToProcess
# AJK TODO create profiling models (see db/profiling.py)
# AJK TODO when all that is done, collapse migrations
# We're keeping Flask for the frontend stuff; Django is only for the database interactions.
# AJK TODO write a script to convert the Mongolia database to Django

# AJK TODO move from the installed pbkdf2 to the python 2.7.10+ builtin, and
# test that everything still works.


class AbstractModel(models.Model):

    class Meta:
        abstract = True


# AJK TODO add annotations and help_texts (copy annotations from old _models.py files)
# AJK TODO reorder fields cleanly
class Study(models.Model):
    name = models.TextField()
    encryption_key = models.CharField(max_length=32)
    deleted = models.BooleanField(default=False)


# AJK TODO idea: add SurveyArchive model that gets created on Survey.save()
class Survey(AbstractModel):
    # AJK TODO ensure that JSON-blobbification returns the _survey version of the type
    AUDIO = 'audio'
    TRACKING = 'tracking'
    SURVEY_TYPE_CHOICES = (
        (AUDIO, 'audio_survey'),
        (TRACKING, 'tracking_survey'),
    )

    # AJK TODO test that the TextField can deal with arbitrarily large text (e.g. 1MB)
    content = models.TextField(default='[]', help_text='JSON blob containing information about the survey questions.')
    timings = models.TextField(default=json.dumps([[], [], [], [], [], [], []]),
                               help_text='JSON blob containing the times at which the survey is sent.')
    survey_type = models.CharField(max_length=16, choices=SURVEY_TYPE_CHOICES)
    settings = models.TextField(default='{}', help_text='JSON blob containing settings for the survey.')

    study = models.ForeignKey('Study', on_delete=models.PROTECT, related_name='surveys')
    deleted = models.BooleanField(default=False)


class Participant(AbstractModel):
    ANDROID = 'ANDROID'
    IOS = 'IOS'
    OS_TYPE_CHOICES = (
        (ANDROID, 'ANDROID'),
        (IOS, 'IOS'),
    )

    id_validator = RegexValidator('^[1-9a-z]+$', message='Invalid Participant ID')
    patient_id = models.CharField(max_length=8, unique=True, validators=[id_validator],
                                  help_text='Eight-character unique ID with characters chosen from 1-9 and a-z')

    device_id = models.CharField(
        max_length=256,
        null=True,
        help_text='The ID of the device that the participant is using for the study, provided by the mobile API.',
    )
    os_type = models.CharField(max_length=16, choices=OS_TYPE_CHOICES, null=True)

    # AJK TODO look into doing password stuff automatically through Django:
    # https://docs.djangoproject.com/en/1.11/topics/auth/passwords/
    url_safe_base_64_validator = RegexValidator('^[0-9a-zA-Z_\-]+$')
    password = models.CharField(max_length=44, validators=[url_safe_base_64_validator])
    salt = models.CharField(max_length=24, validators=[url_safe_base_64_validator])

    study = models.ForeignKey('Study', on_delete=models.PROTECT, related_name='participants', null=False)
    deleted = models.BooleanField(default=False)


class Admin(AbstractModel):
    username = models.CharField(max_length=32, unique=True)
    system_admin = models.BooleanField(default=False, help_text='Whether the admin is also a sysadmin')

    # AJK TODO annotation explaining the validators, make them local to models.py
    url_safe_base_64_validator = RegexValidator('^[0-9a-zA-Z_\-]+$')
    password = models.CharField(max_length=44, validators=[url_safe_base_64_validator])
    salt = models.CharField(max_length=24, validators=[url_safe_base_64_validator])

    standard_base_64_validator = RegexValidator('^[0-9a-zA-Z+/]+$')
    access_key_id = models.CharField(max_length=64, validators=[standard_base_64_validator])
    access_key_secret = models.CharField(max_length=44, validators=[url_safe_base_64_validator])
    access_key_secret_salt = models.CharField(max_length=24, validators=[url_safe_base_64_validator])

    studies = models.ManyToManyField('Study', related_name='admins')
    deleted = models.BooleanField(default=False)


class DeviceSettings(AbstractModel):
    # Whether various device options are turned on
    accelerometer = models.BooleanField(default=True)
    gps = models.BooleanField(default=True)
    calls = models.BooleanField(default=True)
    texts = models.BooleanField(default=True)
    wifi = models.BooleanField(default=True)
    bluetooth = models.BooleanField(default=False)
    power_state = models.BooleanField(default=True)

    # Whether iOS-specific data streams are turned on
    proximity = models.BooleanField(default=False)
    gyro = models.BooleanField(default=False)
    magnetometer = models.BooleanField(default=False)
    devicemotion = models.BooleanField(default=False)
    reachability = models.BooleanField(default=True)

    # Upload over cellular data or only over WiFi (WiFi-only is default)
    allow_upload_over_cellular_data = models.BooleanField(default=False)

    # Timer variables
    accelerometer_off_duration_seconds = models.PositiveIntegerField(default=10)
    accelerometer_on_duration_seconds = models.PositiveIntegerField(default=10)
    bluetooth_on_duration_seconds = models.PositiveIntegerField(default=60)
    bluetooth_total_duration_seconds = models.PositiveIntegerField(default=300)
    bluetooth_global_offset_seconds = models.PositiveIntegerField(default=0)
    check_for_new_surveys_frequency_seconds = models.PositiveIntegerField(default=3600 * 6)
    create_new_data_files_frequency_seconds = models.PositiveIntegerField(default=15 * 60)
    gps_off_duration_seconds = models.PositiveIntegerField(default=600)
    gps_on_duration_seconds = models.PositiveIntegerField(default=60)
    seconds_before_auto_logout = models.PositiveIntegerField(default=600)
    upload_data_files_frequency_seconds = models.PositiveIntegerField(default=3600)
    voice_recording_max_time_length_seconds = models.PositiveIntegerField(default=240)
    wifi_log_frequency_seconds = models.PositiveIntegerField(default=300)

    # iOS-specific timer variables
    gyro_off_duration_seconds = models.PositiveIntegerField(default=600)
    gyro_on_duration_seconds = models.PositiveIntegerField(default=60)
    magnetometer_off_duration_seconds = models.PositiveIntegerField(default=600)
    magnetometer_on_duration_seconds = models.PositiveIntegerField(default=60)
    devicemotion_off_duration_seconds = models.PositiveIntegerField(default=600)
    devicemotion_on_duration_seconds = models.PositiveIntegerField(default=60)

    # Text strings
    about_page_text = models.TextField(default=ABOUT_PAGE_TEXT)
    call_clinician_button_text = models.TextField(default='Call My Clinician')
    consent_form_text = models.TextField(default=CONSENT_FORM_TEXT)
    survey_submit_success_toast_text = models.TextField(default=SURVEY_SUBMIT_SUCCESS_TOAST_TEXT)

    # Consent sections
    consent_sections = models.TextField(default=DEFAULT_CONSENT_SECTIONS_JSON)

    # AJK TODO add a signals.py to ensure a DeviceSettings object is created upon Study creation
    study = models.OneToOneField('Study', on_delete=models.PROTECT, related_name='device_settings')
    deleted = models.BooleanField(default=False)
