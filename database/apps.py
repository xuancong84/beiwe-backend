# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig


class DatabaseConfig(AppConfig):
    name = 'database'

    def ready(self):
        from database import signals
