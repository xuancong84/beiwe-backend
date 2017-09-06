# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.db import models
from django.core.validators import RegexValidator

# AJK TODO create file processing models and FKs: ChunkRegistry, FileToProcess
# AJK TODO create profiling models (see db/profiling.py)
# AJK TODO when all that is done, collapse migrations
# We're keeping Flask for the frontend stuff; Django is only for the database interactions.
# AJK TODO write a script to convert the Mongolia database to Django

# AJK TODO move from the installed pbkdf2 to the python 2.7.10+ builtin, and
# test that everything still works.


# AJK TODO add annotations and help_texts
# AJK TODO reorder fields cleanly
class Study(models.Model):
    name = models.TextField()
    encryption_key = models.CharField(max_length=32)
    deleted = models.BooleanField(default=False)


class Survey(models.Model):
    AUDIO = 'audio'
    TRACKING = 'tracking'
    SURVEY_TYPE_CHOICES = (
        (AUDIO, 'audio_survey'),
        (TRACKING, 'tracking_survey'),
    )

    # AJK TODO test that the TextField can deal with arbitrarily large text (e.g. 1MB)
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
    username = models.CharField(max_length=32, unique=True)
    system_admin = models.BooleanField(default=False, help_text='Whether the admin is also a sysadmin')

    password = []  # use Django passwords, see Participant
    salt = []  # ditto

    access_key_id = []  # uh maybe make a model for this?
    access_key_secret = []  # this should be Django passwords again
    access_key_secret_salt = []

    studies = models.ManyToManyField('Study', related_name='admins')


class DeviceSettings(models.Model):
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
    about_page_text = models.TextField(
        default='The Beiwe application runs on your phone and helps researchers collect information about '
                'your behaviors. Beiwe may ask you to fill out short surveys or to record your voice. '
                'It may collect information about your location (using phone GPS) and how much you move '
                '(using phone accelerometer). Beiwe may also monitor how much you use your phone for '
                'calling and texting and keep track of the people you communicate with. Importantly, '
                'Beiwe never records the names or phone numbers of anyone you communicate with. While '
                'it can tell if you call the same person more than once, it does not know who that '
                'person is. Beiwe also does not record the content of your text messages or phone calls. '
                'Beiwe may keep track of the different Wi-Fi networks and Bluetooth devices around your '
                'phone, but the names of those networks are replaced with random codes.\n\n'
                'Although Beiwe collects large amounts of data, the data is processed to protect your '
                'privacy. This means that it does not know your name, your phone number, or anything '
                'else that could identify you. Beiwe only knows you by an identification number. '
                'Because Beiwe does not know who you are, it cannot communicate with your clinician '
                'if you are ill or in danger. Researchers will not review the data Beiwe collects '
                'until the end of the study. To make it easier for you to connect with your '
                'clinician, the \'Call my Clinician\' button appears at the bottom of every page.\n\n'
                'Beiwe was conceived and designed by Dr. Jukka-Pekka \'JP\' Onnela at the Harvard '
                'T.H. Chan School of Public Health. Development of the Beiwe smartphone application '
                'and data analysis software is funded by NIH grant 1DP2MH103909-01 to Dr. Onnela. '
                'The smartphone application was built by Zagaran, Inc., in Cambridge, Massachusetts.'
    )
    call_clinician_button_text = models.TextField(default='Call My Clinician')
    consent_form_text = models.TextField(
        default='I have read and understood the information about the study and all of my '
                'questions about the study have been answered by the study researchers.'
    )
    survey_submit_success_toast_text = models.TextField(
        default='Thank you for completing the survey. A clinician will not see your answers '
                'immediately, so if you need help or are thinking about harming yourself, '
                'please contact your clinician. You can also press the \'Call My Clinician\' button.'
    )

    # Consent sections
    default_consent_sections = {
        "welcome": {"text": "", "more": ""}, "data_gathering": {"text": "", "more": ""},
        "privacy": {"text": "", "more": ""}, "data_use": {"text": "", "more": ""},
        "time_commitment": {"text": "", "more": ""}, "study_survey": {"text": "", "more": ""},
        "study_tasks": {"text": "", "more": ""}, "withdrawing": {"text": "", "more": ""}
    }
    consent_sections = models.TextField(default=json.dumps(default_consent_sections))

    study = models.OneToOneField('Study', on_delete=models.CASCADE, related_name='device_settings')
