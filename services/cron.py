import imp as _imp
from os.path import abspath as _abspath

_current_folder_init = _abspath(__file__).rsplit('/', 1)[0]+ "/__init__.py"
_imp.load_source("__init__", _current_folder_init)

from sys import argv
from cronutils import run_tasks

from services.db_maintenance import run_database_tasks
from celery_data_processing.data_processing_tasks import create_file_processing_tasks
from pipeline import index

# FIXME: this file is from pipeline, determine what needs to be merged into the new cron_target.py file.

FIVE_MINUTES = "five_minutes"
HOURLY = "hourly"
FOUR_HOURLY = "four_hourly"
DAILY = "daily"
WEEKLY = "weekly"
MONTHLY = "monthly"
VALID_ARGS = [FIVE_MINUTES, HOURLY, FOUR_HOURLY, DAILY, WEEKLY, MONTHLY]

# Crontab used for the current VALID_ARGS:
# # m h dom mon dow   command
# */5 * * * * : five_minutes; cd $PROJECT_PATH; chronic python cron.py five_minutes
# 19 * * * * : hourly; cd $PROJECT_PATH; chronic python cron.py hourly
# 30 */4 * * * : four_hourly; cd $PROJECT_PATH; chronic python cron.py four_hourly
# @daily : daily; cd $PROJECT_PATH; chronic python cron.py daily
# 0 2 * * 0 : weekly; cd $PROJECT_PATH; chronic python cron.py weekly
# 48 4 1 * * : monthly; cd $PROJECT_PATH; chronic python cron.py monthly

TASKS = {
    FIVE_MINUTES: [create_file_processing_tasks],
    HOURLY: [index.hourly],
    FOUR_HOURLY: [],
    DAILY: [run_database_tasks, index.daily],
    WEEKLY: [index.weekly],
    MONTHLY: [index.monthly],
}

# We run the hourly task... hourly.  When multiples of this job overlap we disallow it and get
# the error report notification. So, we set the time limit very high to avoid the extra
# notification.
TIME_LIMITS = {
    FIVE_MINUTES: 60*60*24*365,    # 1 year (never kill)
    HOURLY: 60*60*24*365,          # 1 year (never kill)
    FOUR_HOURLY: 60*60*24*365,     # 1 year (never kill)
    DAILY: 60*60*24*365,           # 1 year (never kill)
    WEEKLY: 60*60,                 # 1 hour - if database cleanup takes... time, we have problems.
    MONTHLY: 60*60*24*365,         # 1 year (never kill)
}

KILL_TIMES = {
    FIVE_MINUTES: 60*60*24*365,    # 1 year (never kill)
    HOURLY: 60*60*24*365,          # 1 year (never kill)
    FOUR_HOURLY: 60*60*24*365,     # 1 year (never kill)
    DAILY: 60*60*24*365,           # 1 year (never kill)
    WEEKLY: 60*60,                 # 1 hour - if database cleanup takes... time, we have problems.
    MONTHLY: 60*60*24*365,         # 1 year (never kill)
}

if __name__ == "__main__":
    if len(argv) <= 1:
        raise Exception("Not enough arguments to cron\n")
    elif argv[1] in VALID_ARGS:
        cron_type = argv[1]
        if cron_type in KILL_TIMES:
            run_tasks(TASKS[cron_type], TIME_LIMITS[cron_type], cron_type, KILL_TIMES[cron_type])
        else:
            run_tasks(TASKS[cron_type], TIME_LIMITS[cron_type], cron_type)
    else:
        raise Exception("Invalid argument to cron\n")
