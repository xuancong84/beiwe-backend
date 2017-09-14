from bson.objectid import ObjectId
from config.constants import (CONCURRENT_NETWORK_OPS, CHUNKS_FOLDER, CHUNKABLE_FILES,
                              PROCESSABLE_FILE_EXTENSIONS,
                              data_stream_to_s3_file_name_string,)
from datetime import datetime
from multiprocessing.pool import ThreadPool

from libs.files_to_process import process_file_chunks
from libs.s3 import s3_list_files, s3_delete, s3_upload

# Mongolia models
from db.data_access_models import FileToProcess, FilesToProcess, ChunkRegistry, ChunksRegistry
from db.study_models import Study, Survey, StudyDeviceSettings
from db.user_models import Users, User

# Django models
from study.models import ChunkRegistry as DCR, DeviceSettings as DDS, FileProcessLock, FileToProcess as DFTP, Participant, Study as DStudy, Survey as DSurvey


def reindex_all_files_to_process():
    """
    Totally clears the FilesToProcess DB, deletes all chunked files on S3,
    clears the ChunksRegistry DB, readds all relevant files on S3 to the
    FilesToProcess registry and then rechunks them.
    """
    
    # Delete all preexisting FTP and ChunkRegistry objects
    FileProcessLock.lock()
    print('{!s} purging FileToProcess: {:d}'.format(datetime.now(), DFTP.objects.count()))
    DFTP.objects.all().delete()
    print('{!s} purging ChunkRegistry: {:d}'.format(datetime.now(), DCR.objects.count()))
    DCR.objects.all().delete()
    
    pool = ThreadPool(CONCURRENT_NETWORK_OPS * 2)
    
    # Delete all preexisting chunked data files
    CHUNKED_DATA = s3_list_files(CHUNKS_FOLDER)
    print('{!s} deleting older chunked data: {:d}'.format(datetime.now(), len(CHUNKED_DATA)))
    pool.map(s3_delete, CHUNKED_DATA)
    del CHUNKED_DATA
    
    # Get a list of all S3 files to replace in the database
    print('{!s} pulling new files to process...'.format(datetime.now()))
    files_lists = pool.map(s3_list_files, DStudy.objects.values_list('object_id', flat=True))
    
    # For each such file, create an FTP object
    print("putting new files to process...")
    for i, l in enumerate(files_lists):
        print('{!s} {:d} of {:d}, {:d} files'.format(datetime.now(), i+1, Study.objects.count(), len(l)))
        for fp in l:
            if fp[-4:] in PROCESSABLE_FILE_EXTENSIONS:
                patient_id = fp.split('/', 2)[1]
                participant_pk = Participant.objects.filter(patient_id=patient_id).values_list('pk', flat=True).get()
                DFTP.append_file_for_processing(fp, fp.split("/", 1)[0], participant_id=participant_pk)
    
    # Clean up by deleting large variables, closing the thread pool and unlocking the file process lock
    del files_lists, l
    pool.close()
    pool.terminate()
    FileProcessLock.unlock()
    
    # Rechunk the newly created FTPs
    print("{!s} processing data.".format(datetime.now()))
    process_file_chunks()


def reindex_specific_data_type(data_type):
    FileProcessLock.lock()
    print("starting...")
    # Convert the data type; raise an error if something is wrong with it
    file_name_key = data_stream_to_s3_file_name_string(data_type)
    
    # Get all chunk paths of the given data type
    relevant_chunks = DCR.objects.filter(data_type=data_type)
    # list() ensures that the QuerySet is evaluated before all of its elements are deleted (otherwise it would be empty)
    relevant_indexed_files = list(relevant_chunks.values_list('chunk_path', flat=True))
    
    # Delete the old ChunkRegistry objects
    print("purging old data...")
    relevant_chunks.delete()

    pool = ThreadPool(20)
    pool.map(s3_delete, relevant_indexed_files)

    print("pulling files to process...")
    files_lists = pool.map(s3_list_files, DStudy.objects.values_list('object_id', flat=True))
    for i, l in enumerate(files_lists):
        print('{!s} {:d} of {:d}, {:d} files'.format(datetime.now(), i + 1, Study.objects.count(), len(l)))
        for fp in l:
            if fp[-4:] in PROCESSABLE_FILE_EXTENSIONS:
                patient_id = fp.split('/', 2)[1]
                participant_pk = Participant.objects.filter(patient_id=patient_id).values_list('pk', flat=True).get()
                DFTP.append_file_for_processing(fp, fp.split("/", 1)[0], participant_id=participant_pk)
    
    del files_lists, l
    pool.close()
    pool.terminate()
    FileProcessLock.unlock()

    print("{!s} processing data.".format(datetime.now()))
    process_file_chunks()
    print("Done.")


# def reindex_study(study_id):
#     if isinstance(study_id, (str, unicode)):
#         study_id = ObjectId(study_id)
#     study_id_string = str(study_id)
#     FileProcessLock.lock()
#     print "starting..."
#     #FIXME: this line is awful, it cause the data loss
#     raise Exception("ELI YOU ARE DUMB!")
#     # relevant_chunks = ChunksRegistry(study_id=study_id)
#     relevant_indexed_files = [ chunk["chunk_path"] for chunk in relevant_chunks ]
#     print "purging old data..."
#     for chunk in relevant_chunks: chunk.remove()
#
#     pool = ThreadPool(20)
#     pool.map(s3_delete, relevant_indexed_files)
#     pool.close( )
#     pool.terminate( )
#
#     print "pulling files to process..."
#     file_list = s3_list_files(study_id_string)
#     print "adding", len(file_list), "files to process"
#
#     for fp in file_list:
#         if fp[-4:] in PROCESSABLE_FILE_EXTENSIONS:
#             FileToProcess.append_file_for_processing(fp, study_id, fp.split("/", 2)[1])
#
#     del file_list, relevant_chunks, relevant_indexed_files, pool
#     print str(datetime.now()), "processing data..."
#     FileProcessLock.unlock()
#     process_file_chunks()
#     print "Done."


def check_for_bad_chunks():
    """ This function runs through all chunkable data and checks for invalid file pointers
    to s3. """
    chunked_data = set(s3_list_files("CHUNKED_DATA"))
    bad_chunks = []
    for entry in ChunksRegistry():
        if entry.data_type in CHUNKABLE_FILES and entry.chunk_path not in chunked_data:
            bad_chunks.append(entry)
    print("bad chunks:", len(bad_chunks))

    # for chunk in bad_chunks:
    #     u = chunk.user_id
    #     print Study(_id=u.study_id).name


def count_study_chunks():
    chunked_data = s3_list_files("CHUNKED_DATA")
    study_prefixes = { f[:38] for f in chunked_data }
    study_prefix_to_id = { study_prefix: ObjectId(study_prefix.split("/")[-2]) for study_prefix in study_prefixes }
    study_prefix_to_name= { study_prefix:Study(_id=study_id).name for study_prefix, study_id in study_prefix_to_id.items() }
    study_count = { study_prefix_to_name[study_prefix]: len([f for f in chunked_data if f[:38] == study_prefix]) for study_prefix in study_prefixes }
    return study_count
    #map study ids to names


def create_fake_mp4(number=10):
    for x in range(number):
        with open("thing", "r") as f:
            file_path = "55d3826297013e3a1c9b8c3e/h6fflp/voiceRecording/%s.mp4" % (1000000000 + x)
            s3_upload(file_path, f.read(), ObjectId("55d3826297013e3a1c9b8c3e"), raw_path=True)
            FileToProcess.append_file_for_processing(file_path, ObjectId("55d3826297013e3a1c9b8c3e"), "h6fflp")


def completely_purge_study(study_id, actually_delete=False):
    if not isinstance(study_id, ObjectId):
        study_id = ObjectId(study_id)
    study = Study(study_id)

    surveys = study["surveys"]
    device_settings = study["device_settings"]
    users = Users(study_id=study_id)
    chunks = ChunksRegistry(study_id=study_id)
    files_to_process = FilesToProcess(study_id=study_id)
    if not actually_delete:
        print("if you actually delete this you will not be able to decrypt anything " \
              "from this study.  Don't do it unless you know what you are doing.")
        print(study.name)
        # print len(study)
        # print len(device_settings)
        print(len(surveys))
        print(len(users))
        print(len(chunks))
        print(len(files_to_process))
    else:
        StudyDeviceSettings(device_settings).remove()
        [Survey(s).remove() for s in surveys]
        [User(u).remove() for u in users]
        [ChunkRegistry(c).remove() for c in chunks]
        [FileToProcess(f).remove() for f in files_to_process]
        study.remove()
