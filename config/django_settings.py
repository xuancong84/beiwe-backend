from os.path import dirname, join

from config.secure_settings import FLASK_SECRET_KEY

DB_PATH = join(dirname(dirname(__file__)), "private/beiwe_db.sqlite")
TEST_DATABASE_PATH = join(dirname(__file__), 'private/tests_db.sqlite')

# THIS BIT IS REQUIRED BY THE DJANGO MANAGEMENT COMMANDS

SECRET_KEY = FLASK_SECRET_KEY

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': DB_PATH,
        # TODO: The test database directive currently fails to create a database...
        # 'TEST': {'NAME': TEST_DATABASE_PATH}
    },
}

TIME_ZONE = 'UTC'
USE_TZ = True

INSTALLED_APPS = [
    'database.apps.DatabaseConfig',
    'django_extensions',
]

SHELL_PLUS = "ipython"

SHELL_PLUS_PRE_IMPORTS = []
SHELL_PLUS_POST_IMPORTS = []

# Using the default test runner
TEST_RUNNER = 'django.test.runner.DiscoverRunner'