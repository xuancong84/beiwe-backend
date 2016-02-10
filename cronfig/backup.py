from config.security import (S3_BACKUPS_AWS_KEY_ID as BACKUP_ID,
                             S3_BACKUPS_AWS_SECRET_ACCESS_KEY as BACKUP_KEY,
                             S3_BACKUPS_BUCKET, MONGO_USERNAME, MONGO_PASSWORD,
                             LOCAL_BACKUPS_DIRECTORY)
from mongobackup import backup

def run_backup():
    backup(MONGO_USERNAME, MONGO_PASSWORD, LOCAL_BACKUPS_DIRECTORY,
           s3_bucket=S3_BACKUPS_BUCKET, s3_access_key_id=BACKUP_ID,
           s3_secret_key=BACKUP_KEY, purge_local=30)