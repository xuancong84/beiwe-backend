import mongolia

from datetime import datetime
from mongobackup import backup

from config.secure_settings import (S3_BACKUPS_AWS_KEY_ID as BACKUP_ID,
         S3_BACKUPS_AWS_SECRET_ACCESS_KEY as BACKUP_KEY,S3_BACKUPS_BUCKET,
         MONGO_USERNAME, MONGO_PASSWORD, LOCAL_BACKUPS_DIRECTORY)

def run_database_tasks():
    """ Runs a database optimize (which should speed up the backup),
        and then runs a backup.  If the optimize fails we run the backup
        anyway and raise the failure at the end. """
    error = None
    try:
        optimize_db()
    except Exception as e: #we want to catch any kind of error here
        error = e
        
    print str(datetime.now()), "started backup"
    run_backup()
    print str(datetime.now()), "finished backup"

    if error is not None:
        print "Optimize db failed with the following:"
        raise error
    
def run_backup():
    """ Simple an explicit function. """
    backup(MONGO_USERNAME, MONGO_PASSWORD, LOCAL_BACKUPS_DIRECTORY,
           s3_bucket=S3_BACKUPS_BUCKET, s3_access_key_id=BACKUP_ID,
           s3_secret_key=BACKUP_KEY, purge_local=1)

def optimize_db():
    """ Performs operations that improve database performance, and reduce drive usage. """
    db = mongolia.mongo_connection.CONNECTION.get_connection()['beiwe']
    
    names = [name for name in db.collection_names() if "system.indexes" != name]
    for name in names:
        start = datetime.utcnow()
        print str(start), "compacting %s..." % name,
        db.command("compact", name)
        delta = datetime.utcnow() - start
        print delta.total_seconds()
    
    #This command can take time, causes a write-block.
    # start = datetime.utcnow()
    # print str(datetime.now()), "running repair database..."
    # db.command("repairDatabase")
    # end = datetime.utcnow()
    # delta = end - start
    # print str(end), "finished database repair in %s." % delta.total_seconds()

def get_mongo_settings():
    db = mongolia.mongo_connection.CONNECTION.get_connection()['admin']
    db.command({"getCmdLineOpts":1})