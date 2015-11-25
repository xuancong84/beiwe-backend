from sys import argv
from cronutils import run_tasks
from cronfig.backup import run_backup 
from libs.files_to_process import process_file_chunks
FIVE_MINUTES = "five_minutes"
HOURLY = "hourly"
FOUR_HOURLY = "four_hourly"
DAILY = "daily"
WEEKLY = "weekly"

TASKS = {
    FIVE_MINUTES: [],
    HOURLY: [process_file_chunks],
    FOUR_HOURLY: [],
    DAILY: [run_backup],
    WEEKLY: []
}

TIME_LIMITS = {
    FIVE_MINUTES: 180, # 3 minutes
    HOURLY: 3600,      # 60 minutes
    FOUR_HOURLY: 5400, # 1.5 hours
    DAILY: 43200,      # 12 hours
    WEEKLY: 86400,     # 1 day
}

VALID_ARGS = [FIVE_MINUTES, HOURLY, FOUR_HOURLY, DAILY, WEEKLY]


if __name__ == "__main__":
    if len(argv) <= 1:
        raise Exception("Not enough arguments to cron\n")
    elif argv[1] in VALID_ARGS:
        cron_type = argv[1]
        run_tasks(TASKS[cron_type], TIME_LIMITS[cron_type], cron_type)
    else:
        raise Exception("Invalid argument to cron\n")
    
    
