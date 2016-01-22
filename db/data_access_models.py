from datetime import datetime
from db.mongolia_setup import DatabaseObject, DatabaseCollection, REQUIRED #, ID_KEY
from libs.security import chunk_hash
from config.constants import CHUNKABLE_FILES, CHUNK_TIMESLICE_QUANTUM, SURVEY_TIMINGS, SURVEY_ANSWERS
from mongolia.constants import REQUIRED_STRING

class EverythingsGoneToHellException(Exception): pass

class ChunkRegistry(DatabaseObject):
    PATH = "beiwe.chunk_registry"
    DEFAULTS = {"study_id":REQUIRED,
                "user_id":REQUIRED_STRING,
                "data_type": "",
                #todo: check datetime support in mongolia
                "time_bin": REQUIRED,
                "chunk_hash": None,
                "chunk_path": REQUIRED_STRING,
                "is_chunkable": REQUIRED }

    @classmethod
    def add_new_chunk(cls, study_id, user_id, data_type, s3_file_path,
                      time_bin, file_contents=None):
        is_chunkable = data_type in CHUNKABLE_FILES
        if is_chunkable: time_bin = int(time_bin)*CHUNK_TIMESLICE_QUANTUM

        ChunkRegistry.create(
            {"study_id": study_id,
            "user_id": user_id,
            "data_type": data_type,
            "chunk_path": s3_file_path,
            "chunk_hash": chunk_hash(file_contents) if is_chunkable else None,
            "time_bin": datetime.fromtimestamp(time_bin),
            "is_chunkable": is_chunkable },
            random_id=True )
#         print "new chunk:", s3_file_path
    
    def update_chunk_hash(self, data_to_hash):
        self["chunk_hash"] = chunk_hash(data_to_hash)
        self.save()
#         print "upd chunk", self['chunk_path']
    
class FileToProcess(DatabaseObject):
    PATH = "beiwe.file_to_process"
    DEFAULTS = { "s3_file_path":REQUIRED_STRING,
                 "study_id": REQUIRED,
                 "user_id": REQUIRED_STRING }
    @classmethod
    def append_file_for_processing(cls, file_path, study_id, user_id):
        if file_path[:24] == str(study_id): 
            FileToProcess.create( {"s3_file_path":file_path, "study_id":study_id,
                                    "user_id":user_id}, random_id=True)
        else: FileToProcess.create( {"s3_file_path":str(study_id)+'/'+file_path,
                                     "study_id":study_id, "user_id":user_id},
                                     random_id=True)

class FileProcessLock(DatabaseObject):
    PATH = "beiwe.file_process_running"
    DEFAULTS = {"mark":""}
    @classmethod
    def lock(cls):
        if len(FileProcessLockCollection()) > 0: raise EverythingsGoneToHellException
        FileProcessLock.create({"mark":"marked"}, random_id=True)
    @classmethod
    def unlock(cls):
        for f in FileProcessLockCollection(mark="marked"):
            f.remove()
#     @classmethod
#     def islocked(cls):
#         if len(FileProcessLockCollection()) > 0: return False
#         return True

################################################################################

class ChunksRegistry(DatabaseCollection):
    OBJTYPE = ChunkRegistry
    
    @classmethod
    def get_chunks_time_range(cls, study_id, user_ids=None, data_types=None,
                              start=None, end=None):
        """ This function uses mongo query syntax to provide datetimes and have
            mongo do the comparison operation, and the 'in' operator to have
            mongo only match the user list provided. """
        query = {"study_id":study_id}
        if user_ids: query["user_id"] = { "$in":user_ids }
        if data_types: query["data_type"] = { "$in":data_types }
        #TODO: test whether this query is exclusive or inclusive, document on api query page.
        if start and end: query["time_bin"] = {"$gt": start, "$lt": end }
        if start and not end: query["time_bin"] = { "$gt": start}
        if end and not start: query["time_bin"] = { "$lt": end }
        print query
        return cls(query=query)

class FilesToProcess(DatabaseCollection):
    OBJTYPE = FileToProcess
class FileProcessLockCollection(DatabaseCollection):
    OBJTYPE = FileProcessLock