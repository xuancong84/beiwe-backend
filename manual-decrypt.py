#!/usr/bin/env python2
import os, sys, argparse

import jinja2
from flask import Flask, render_template, redirect
from raven.contrib.flask import Sentry
from werkzeug.contrib.fixers import ProxyFix

from config import load_django

from api import (participant_administration, admin_api, copy_study_api, data_access_api,
    data_pipeline_api, mobile_api, survey_api)
from config.settings import SENTRY_ELASTIC_BEANSTALK_DSN, SENTRY_JAVASCRIPT_DSN
from libs.admin_authentication import is_logged_in
from libs.security import set_secret_key
from pages import (admin_pages, mobile_pages, survey_designer, system_admin_pages,
    data_access_web_form)
from libs import encryption

parser = argparse.ArgumentParser(usage='$0 study_id <encrypted-input 1>decrypted-output', description='perform master-key decryption')
parser.add_argument('study_id', help='study_id')
parser.add_argument('-key', help='use encryption key', action='store_true')
opt = parser.parse_args()
globals().update(vars(opt))

if key:
    sys.stdout.write(encryption.decrypt_server_by_key(sys.stdin.read(), study_id))
else:
    sys.stdout.write(encryption.decrypt_server(sys.stdin.read(), study_id))
