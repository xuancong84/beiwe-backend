from db.mongolia_setup import DatabaseObject, DatabaseCollection, REQUIRED #, ID_KEY
from datetime import datetime

class ChunkRegistry(DatabaseObject):
    PATH = "beiwe.chunk_registry"
    DEFAULTS = {"study":REQUIRED,
                "user":REQUIRED,
                "data_stream": "",
                #todo: check datetime support in mongolia
                "datetime_start": REQUIRED,
                "chunk_hash": "",
                "s3_file_path": "" }


class FileToProcess(DatabaseObject):
    PATH = "beiwe.file_to_process"
    DEFAULTS = { "s3_file_path":"",
                 "study_id": REQUIRED,
                 "user_name": "" }
    @classmethod
    def append_file_for_processing(cls, file_path, study_id, user_name): 
        FileToProcess.create( {"s3_file_path":file_path, "study_id":study_id, "user_name":user_name}, random_id=True)

class FileProcessLock(DatabaseObject):
    PATH = "beiwe.file_process_running"
    DEFAULTS = {"mark":""}
    
    class EverythingsGoneToHellException(Exception): pass
    
    @classmethod
    def lock(cls):
        if len(FileProcessLockCollection) > 0: raise EverythingsGoneToHellException
        FileProcessLock.create({"mark":"marked"})
        
    @classmethod
    def unlock(cls):
        for f in FileProcessLock(mark="marked"):
            f.remove()

class FileProcessLockCollection():
    OBJTYPE = FileProcessLock
################################################################################

class ChunksRegistry(DatabaseCollection):
    OBJTYPE = ChunkRegistry
    
    @classmethod
    def get_chunks_time_range(cls, study_id, user_ids=[],
                              start=datetime.fromtimestamp(0), end=datetime.utcnow()):
        """ This function uses mongo query syntax to provide datetimes and have
            mongo do the comparison operation, and the 'in' operator to have
            mongo only match the user list provided. """
        return cls(query={"chunk_start": {"$gt": start, "$lt": end },
                          "user_id":{"$in":user_ids }, "study_id": study_id } )
            
class FilesToProcess(DatabaseCollection):
    OBJTYPE = FileToProcess