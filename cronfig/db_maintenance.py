import mongolia
from datetime import datetime

#TODO: this probably only works as is (no password) because of the current configuration of the database.

def optimize_db():
    db = mongolia.mongo_connection.CONNECTION.get_connection()['beiwe']

    names = [name for name in db.collection_names() if "system.indexes" != name]
    for name in names:
        print str(datetime.now()), "compacting %s..." % name
        db.command("compact", name)

    print str(datetime.now()), "running repair database..."
    db.command("repairDatabase")
    print str(datetime.now()), "finished database repair."