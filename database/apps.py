# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig


class StudyConfig(AppConfig):
    name = 'study'

    def ready(self):
        from database import signals
