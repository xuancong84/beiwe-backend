from bson import ObjectId
from datetime import datetime
from flask import Blueprint, request, abort, json, Response
from multiprocessing.pool import ThreadPool
from zipfile import ZipFile, ZIP_DEFLATED

from bson.errors import InvalidId
from db.data_access_models import ChunksRegistry, FileToProcess
from db.study_models import Study, Studies
from db.user_models import Admin, User, Users
from libs.logging import email_system_administrators
from libs.s3 import s3_retrieve, s3_list_files, s3_upload
from libs.streaming_bytes_io import StreamingBytesIO
from config.constants import (API_TIME_FORMAT, VOICE_RECORDING, ALL_DATA_STREAMS,
                              CONCURRENT_NETWORK_OPS, SURVEY_ANSWERS, SURVEY_TIMINGS)
from boto.utils import JSONDecodeError

# Data Notes
# The call log has the timestamp column as the 3rd column instead of the first.
# The Wifi and Identifiers have timestamp in the file name.
# The debug log has many lines without timestamps.

data_access_api = Blueprint('data_access_api', __name__)

upload_stream_map = { "survey_answers":("surveyAnswers", "csv" ),
                      "audio":("voiceRecording", "mp4" ) }


#########################################################################################

def get_and_validate_study_id():
    """ Checks for a valid study id.
        No study id causes a 400 (bad request) error.
        Study id malformed (not 24 characters) causes 400 error.
        Study id otherwise invalid causes 400 error.
        Study id does not exist in our database causes _404_ error."""
    
    if "study_id" not in request.values:
        return abort(400)
    
    if len(request.values["study_id"]) != 24:
        #Don't proceed with large sized input.
        print "Received invalid length objectid as study_id in the data access API."
        return abort(400)
    
    try: #If the ID is of some invalid form, we catch that and return a 400
        study_id = ObjectId(request.values["study_id"])
    except InvalidId:
        return abort(400)
    
    study_obj = Study(study_id)
    #Study object will be None if there is no matching study id.
    if not study_obj: #additional case: if study object exists but is empty
        return abort(404)
        
    return study_obj

def get_and_validate_admin(study_obj):
    """ Finds admin based on the secret key provided, returns 403 if admin doesn't exist,
        is not credentialled on the study, or if the secret key does not match. """
    access_key = request.values["access_key"]
    access_secret = request.values["secret_key"]
    admin = Admin(access_key_id=access_key)
    if not admin:
        return abort(403)  # access key DNE
    if admin._id not in study_obj['admins']:
        return abort(403)  # admin is not credentialed for this study
    if not admin.validate_access_credentials(access_secret):
        return abort(403)  # incorrect secret key
    return admin

#########################################################################################

@data_access_api.route("/get-studies/v1", methods=['POST', "GET"])
def get_studies():
    #Cases: invalid access creds
    access_key = request.values["access_key"]
    access_secret = request.values["secret_key"]
    admin = Admin(access_key_id=access_key)
    if not admin: return abort(403) #access key DNE
    if not admin.validate_access_credentials(access_secret):
        return abort(403) #incorrect secret key
    return json.dumps({str(study._id):study.name for study in Studies( admins=str(admin._id) ) } )


@data_access_api.route("/get-users/v1", methods=['POST', "GET"])
def get_users_in_study():
    try: study_id = ObjectId(request.values["study_id"])
    except InvalidId: study_id = None
    study_obj = Study(study_id)
    if not study_obj: return abort(404)
    _ = get_and_validate_admin(study_obj)
    return json.dumps([str(user._id) for user in Users(study_id=study_id) ] )

def handle_database_query(study_id, query, registry=None):
    """ Does the database query as a generator. """
    chunks = ChunksRegistry.get_chunks_time_range(study_id, **query)
    # no registry, just return one by one.
    if not registry:
        for chunk in chunks:
            yield chunk
    
    # yes registry, we need to filter and then yield
    else:
        for chunk in chunks:
            if (chunk['chunk_path'] in registry
                and registry[chunk['chunk_path']] == chunk["chunk_hash"]):
                continue
            else:
                yield chunk


@data_access_api.route("/get-data/v1", methods=['POST', "GET"])
def grab_data():
    """ Required: access key, access secret, study_id
    JSON blobs: data streams, users - default to all
    Strings: date-start, date-end - format as "YYYY-MM-DDThh:mm:ss" 
    optional: top-up = a file (registry.dat)
    cases handled: 
        missing creds or study, invalid admin or study, admin does not have access
        admin creds are invalid 
        (Flask automatically returns a 400 response if a parameter is accessed
        but does not exist in request.values() )
    Returns a zip file of all data files found by the query. """
    
    #uncomment the following line when doing a reindex
    #return abort(503)
    study_obj = get_and_validate_study_id()
    _ = get_and_validate_admin(study_obj)
    
    query = {}
    determine_data_streams_for_db_query(query) #select data streams
    determine_users_for_db_query(query) #select users
    determine_time_range_for_db_query(query) #construct time ranges
    
    #Do query (this is actually a generator)
    if "registry" in request.values:
        get_these_files = handle_database_query(study_obj._id, query,
                                                registry=parse_registry(request.values["registry"]))
    else:
        get_these_files = handle_database_query(study_obj._id, query, registry=None)
    
    # If the request is from the web form we need to include mime information
    #and don't want to create a registry file.
    if 'web_form' in request.values:
        return Response(zip_generator(get_these_files, construct_registry=False),
                        mimetype="zip",
                        headers={'Content-Disposition':'attachment; filename="data.zip"'})
    else:
        return Response( zip_generator(get_these_files, construct_registry=True) )

#Note: you cannot access the request context inside a generator function
def zip_generator(files_list, construct_registry=False):
    """ Pulls in data from S3 in a multithreaded network operation, constructs a zip file of that data.
    This is a generator, advantage is it starts returning data (file by file, but wrapped in zip compression)
    almost immediately.
    """
    
    processed_files = set()
    duplicate_files = set()
    pool = ThreadPool(CONCURRENT_NETWORK_OPS)
    file_registry = {}
    zip_output = StreamingBytesIO()
    zip_input = ZipFile(zip_output, mode="w", compression=ZIP_DEFLATED, allowZip64=True)
    try:
        # chunks_and_content is a list of tuples, of the chunk and the content of the file.
        # chunksize (which is a keyword argument of imap, not to be confused with Beiwe Chunks)
        # is the size of the batches that are handed to the pool. We always want to add the next
        # file to retrieve to the pool asap, so we want a chunk size of 1.
        # (In the documentation there are comments about the timeout, it is irrelevant under this construction.)
        chunks_and_content = pool.imap_unordered(batch_retrieve_s3, files_list, chunksize=1)
        
        for chunk, file_contents in chunks_and_content:
            if construct_registry:
                file_registry[chunk['chunk_path']] = chunk["chunk_hash"]
            file_name = determine_file_name(chunk)
            if file_name in processed_files:
                duplicate_files.add((file_name,chunk['chunk_path']))
                continue
            processed_files.add(file_name)
            zip_input.writestr(file_name, file_contents)
            # These can be large, and we don't want them sticking around in memory as we wait for the yield
            del file_contents, chunk
            yield zip_output.getvalue() #yield the (compressed) file information
            zip_output.empty()
        
        if construct_registry:
            zip_input.writestr("registry", json.dumps(file_registry))
        
        # close, then yield all remaining data in the zip.
        zip_input.close()
        yield zip_output.getvalue()
    
    except None:
        # The try-except-finally block is here to guarantee the Threadpool is closed and terminated.
        # we don't handle any errors, we just re-raise any error that shows up.
        # (with statement does not work.)
        raise
    finally:
        # We rely on the finally block to ensure that the threadpool will be closed and terminated,
        # and also to print an error to the log if we need to.
        pool.close()
        pool.terminate()
        if duplicate_files:
            duplcate_file_message =  "encountered duplicate files: %s" % ",".join(str(name_path) for name_path in duplicate_files)
            email_system_administrators(duplcate_file_message,
                                        "encountered duplicate files in a data download")
            
#########################################################################################

def parse_registry(reg_dat):
    """ Parses the provided registry.dat file and returns a dictionary of chunk
    file names and hashes.  (The registry file is just a json dictionary containing
    a list of file names and hashes.) """
    return json.loads(reg_dat)

def determine_file_name(chunk):
    """ Generates the correct file name to provide the file with in the zip file.
        (This also includes the folder location files in the zip.) """
    extension = chunk["chunk_path"][-3:] #get 3 letter file extension from the source.
    if chunk["data_type"] == SURVEY_ANSWERS:
        #add the survey_id from the file path.
        return "%s/%s/%s/%s.%s" % (chunk["user_id"], chunk["data_type"], chunk["chunk_path"].rsplit("/", 2)[1],
                                str(chunk["time_bin"]).replace(":", "_"), extension)

    elif chunk["data_type"] == SURVEY_TIMINGS:
        #add the survey_id from the database entry.
        return "%s/%s/%s/%s.%s" % (chunk["user_id"], chunk["data_type"], chunk["survey_id"],
                                str(chunk["time_bin"]).replace(":", "_"), extension)

    elif chunk["data_type"] == VOICE_RECORDING:
        #Due to a bug that was not noticed until July 2016 audio surveys did not have the survey id
        # that they were associated with.  Later versions of the app (legacy update 1 and Android 6)
        # correct this.  We can identify those files by checking for the existence of the extra /.
        # When we don't find it, we revert to original behavior.
        if chunk["chunk_path"].count("/") == 4: #
            return "%s/%s/%s/%s.%s" % (chunk["user_id"], chunk["data_type"], chunk["chunk_path"].rsplit("/", 2)[1],
                                       str(chunk["time_bin"]).replace(":", "_"), extension)

    #all other files have this form:
    return "%s/%s/%s.%s" % (chunk["user_id"], chunk["data_type"],
                            str(chunk["time_bin"]).replace(":", "_"), extension)

def str_to_datetime(time_string):
    """ Translates a time string to a datetime object, raises a 400 if the format is wrong."""
    try: return datetime.strptime(time_string, API_TIME_FORMAT)
    except ValueError as e:
        if "does not match format" in e.message: return abort(400)

def batch_retrieve_s3(chunk):
    """ Data is returned in the form (chunk_object, file_data). """
    return chunk, s3_retrieve(chunk["chunk_path"], chunk["study_id"], raw_path=True)

#########################################################################################

def determine_data_streams_for_db_query(query):
    """ Determines, from the html request, the data streams that should go into the database query.
    Modifies the provided query object accordingly, there is no return value
    Throws a 404 if the data stream provided does not exist.
    :param query: expects a dictionary object. """
    if 'data_streams' in request.values:
        # the following two cases are for difference in content wrapping between
        # the CLI script and the download page.
        try:
            query['data_types'] = json.loads(request.values['data_streams'])
        except JSONDecodeError:
            query['data_types'] = request.form.getlist('data_streams')
        
        for data_stream in query['data_types']:
            if data_stream not in ALL_DATA_STREAMS:
                return abort(404)

def determine_users_for_db_query(query):
    """ Determines, from the html request, the users that should go into the database query.
    Modifies the provided query object accordingly, there is no return value.
    Throws a 404 if a user provided does not exist.
    :param query: expects a dictionary object. """
    if 'user_ids' in request.values:
        try:
            query['user_ids'] = [user for user in json.loads(request.values['user_ids'])]
        except JSONDecodeError:
            query['user_ids'] = request.form.getlist('user_ids')
        
        for user_id in query['user_ids']:  # Case: one of the user ids was invalid
            if not User(user_id):
                return abort(404)

def determine_time_range_for_db_query(query):
    """ Determines, from the html request, the time range that should go into the database query.
    Modifies the provided query object accordingly, there is no return value.
    Throws a 404 if a user provided does not exist.
    :param query: expects a dictionary object. """
    if 'time_start' in request.values:
        query['start'] = str_to_datetime(request.values['time_start'])
    if 'time_end' in request.values:
        query['end'] = str_to_datetime(request.values['time_end'])

#########################################################################################

#TODO: before reenabling, audio filenames on s3 were incorrectly enforced to have millisecond precision, remove trailing zeros
#this does not affect data downloading because those file times are generated from the chunk registry
# @data_access_api.route("/data-upload-apiv1", methods=['POST'])
# def data_upload():
#     print "got something!"
#     #Cases: invalid access creds
#     access_key = request.values["access_key"]
#     access_secret = request.values["secret_key"]
#     admin = Admin(access_key_id=access_key)
#     if not admin: return abort(403) #access key DNE
#     if not admin.validate_access_credentials( access_secret ):
#         return abort( 403 )  # incorrect secret key
#
#     if "study_id" in request.values: study_id = request.values["study_id"]
#     else: return "please provide a study_id"
#     study_obj = Study( ObjectId( study_id ) )
#     if admin._id not in study_obj['admins']: return abort(403)  # admin is not credentialed for this study
#
#     if "user_id" in request.values:user_id = request.values["user_id"]
#     else: return "please provide a user_id"
#
#     if "survey_id" in request.values: survey_id = request.values["survey_id"]
#     else: return "please provide a survey_id"
#
#     if "data_stream" in request.values: data_stream = request.values["data_stream"]
#     else: return "please provide a data_stream"
#
#     if data_stream not in upload_stream_map: return "invalid data stream: %s" % data_stream
#
#     if "unix_millisecond_timestamp_string" in request.values:
#         unix_millisecond_timestamp_string = request.values['unix_millisecond_timestamp_string']
#         if len( unix_millisecond_timestamp_string ) != 13:
#             return "invalid timestamp, check millisecond time length: %s" % unix_millisecond_timestamp_string
#         try: x = int( unix_millisecond_timestamp_string )
#         except ValueError: return "something went wrong with your timestamp: %s" % unix_millisecond_timestamp_string
#     else: return "please provide a unix_millisecond_timestamp_string"
#
#     data_stream_string, file_extension  = upload_stream_map[data_stream]
#
#     s3_file_path = "%s/%s/%s/%s/%s.%s" % (study_id, user_id, data_stream_string,
#                       survey_id, unix_millisecond_timestamp_string, file_extension)
#
#     if len(s3_list_files(s3_file_path)) > 0: return "a file matching your parameters already exists"
#     if 'file' in request.files: f = request.files['file']
#     print "%s uploading new files: %s" % (admin._id, s3_file_path)
#
#     s3_upload(s3_file_path, f.read(), study_obj._id, raw_path=True)
#     FileToProcess.append_file_for_processing( s3_file_path, study_obj._id, user_id )
#     return 'file successfully uploaded.'
