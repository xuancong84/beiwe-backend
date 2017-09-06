# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.core.validators import RegexValidator
from django.db import models
from django.db.models.fields.related import RelatedField

from config.constants import IOS_API, ANDROID_API, SURVEY_TYPES
from config.study_constants import (
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

# These validators are used by CharFields in the Admin and Participant models to ensure
# that those fields' values fit the regex below. The length requirement is handled by
# the CharField, but the validator ensures that only certain characters are present
# in the field value. If the ID or hashes are changed, be sure to modify or create a new
# validator accordingly.
id_validator = RegexValidator('^[1-9a-z]+$', message='Invalid Participant ID')
url_safe_base_64_validator = RegexValidator('^[0-9a-zA-Z_\-]+$')
standard_base_64_validator = RegexValidator('^[0-9a-zA-Z+/]+$')


class JSONTextField(models.TextField):
    """
    A TextField for holding JSON-serialized data. This is only different from models.TextField
    in AbstractModel.as_native_json, in that this is not JSON serialized an additional time.
    """
    pass


class AbstractModel(models.Model):

    def as_native_json(self):
        """
        Collect all of the fields of the model and return their values in a JSON dict.
        """
        field_list = self._meta.fields
        field_dict = {}
        for field in field_list:
            field_name = field.name
            if isinstance(field, RelatedField):
                # If the field is a relation, return the related object's primary key
                field_dict[field_name + '_id'] = getattr(self, field_name).id
            elif isinstance(field, JSONTextField):
                # If the field is a JSONTextField, load the field's value before returning
                field_raw_val = getattr(self, field_name)
                field_dict[field_name] = json.loads(field_raw_val)
            else:
                # Otherwise, just return the field's value
                field_dict[field_name] = getattr(self, field_name)

        return json.dumps(field_dict)

    def __str__(self):
        if hasattr(self, 'study'):
            return '{} {} of Study {}'.format(self.__class__.__name__, self.pk, self.study.name)
        elif hasattr(self, 'name'):
            return '{} {}'.format(self.__class__.__name__, self.name)
        else:
            return '{} {}'.format(self.__class__.__name__, self.pk)

    class Meta:
        abstract = True


# AJK TODO add annotations and help_texts (copy annotations from old _models.py files)
# AJK TODO reorder fields cleanly
class Study(AbstractModel):
    name = models.TextField()
    encryption_key = models.CharField(max_length=32)
    deleted = models.BooleanField(default=False)


# AJK TODO idea: add SurveyArchive model that gets created on Survey.save() (or with a signal)
class Survey(AbstractModel):
    SURVEY_TYPE_CHOICES = [(val, val) for val in SURVEY_TYPES]

    # AJK TODO test that the TextField can deal with arbitrarily large text (e.g. 1MB)
    content = JSONTextField(default='[]', help_text='JSON blob containing information about the survey questions.')
    timings = JSONTextField(default=json.dumps([[], [], [], [], [], [], []]),
                            help_text='JSON blob containing the times at which the survey is sent.')
    survey_type = models.CharField(max_length=16, choices=SURVEY_TYPE_CHOICES)
    settings = JSONTextField(default='{}', help_text='JSON blob containing settings for the survey.')

    study = models.ForeignKey('Study', on_delete=models.PROTECT, related_name='surveys')
    deleted = models.BooleanField(default=False)


class Participant(AbstractModel):
    OS_TYPE_CHOICES = (
        (IOS_API, IOS_API),
        (ANDROID_API, ANDROID_API),
    )

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
    password = models.CharField(max_length=44, validators=[url_safe_base_64_validator])
    salt = models.CharField(max_length=24, validators=[url_safe_base_64_validator])

    study = models.ForeignKey('Study', on_delete=models.PROTECT, related_name='participants', null=False)
    deleted = models.BooleanField(default=False)


class Admin(AbstractModel):
    username = models.CharField(max_length=32, unique=True)
    system_admin = models.BooleanField(default=False, help_text='Whether the admin is also a sysadmin')

    password = models.CharField(max_length=44, validators=[url_safe_base_64_validator])
    salt = models.CharField(max_length=24, validators=[url_safe_base_64_validator])

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
    consent_sections = JSONTextField(default=DEFAULT_CONSENT_SECTIONS_JSON)

    study = models.OneToOneField('Study', on_delete=models.PROTECT, related_name='device_settings')
    deleted = models.BooleanField(default=False)
