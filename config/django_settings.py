from os.path import dirname, join

from config.secure_settings import FLASK_SECRET_KEY


DB_PATH = join(dirname(dirname(__file__)), "private/beiwe_db.sqlite")

# THIS BIT IS REQUIRED BY THE DJANGO MANAGEMENT COMMANDS

SECRET_KEY = FLASK_SECRET_KEY

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DB_PATH
    },
}

TIME_ZONE = 'America/New_York'

INSTALLED_APPS = [
    'study.apps.StudyConfig',
    'django_extensions'
]

SHELL_PLUS = "ipython"

SHELL_PLUS_PRE_IMPORTS = []
SHELL_PLUS_POST_IMPORTS = []
