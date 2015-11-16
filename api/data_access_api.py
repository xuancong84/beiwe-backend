from bson import ObjectId
from bson.errors import InvalidId
from collections import defaultdict, deque
from cronutils import ErrorHandler
from datetime import datetime
from flask import Blueprint, request, abort, json
from StringIO import StringIO
from zipfile import ZipFile, ZIP_DEFLATED
from db.data_access_models import FilesToProcess, ChunksRegistry,FileProcessLock,\
    FileToProcess, ChunkRegistry
from db.study_models import Study
from db.user_models import Admin, User
from libs.s3 import s3_retrieve, s3_upload
from config.constants import (API_TIME_FORMAT, CHUNKS_FOLDER, ACCELEROMETER,
    BLUETOOTH, CALL_LOG, GPS, IDENTIFIERS, LOG_FILE, POWER_STATE,
    SURVEY_ANSWERS, SURVEY_TIMINGS, TEXTS_LOG, VOICE_RECORDING,
    WIFI, ALL_DATA_STREAMS, CHUNKABLE_FILES, CHUNK_TIMESLICE_QUANTUM,
    LENGTH_OF_STUDY_ID, HUMAN_READABLE_TIME_LABEL)

# Data Notes
# The call log has the timestamp column as the 3rd column instead of the first.
# The Wifi and Identifiers have timestamp in the file name.
# The debug log has many lines without timestamps.

data_access_api = Blueprint('data_access_api', __name__)

@data_access_api.route("/get-data/v1", methods=['POST', "GET"])
def grab_data():
    """
    required: access key, access secret, study_id
    JSON blobs: data streams, users - default to all
    Strings: date-start, date-end - format as "YYYY-MM-DDThh:mm:ss" 
    optional: top-up = a file (registry.dat)
    cases handled: 
        missing creds or study, invalid admin or study, admin does not have access
        admin creds are invalid 
        (Flask automatically returns a 400 response if a parameter is accessed
        (Flask automatically returns a 400 response if a parameter is accessed
        but does not exist in request.values() )
    Returns a zip file of all data files found by the query. """
    #Case: bad study id
    try: study_id = ObjectId(request.values["study_id"])
    except InvalidId: study_id = None
    study_obj = Study(study_id)
    if not study_obj: return abort(404)
    #Cases: invalid access creds
    access_key = request.values["access_key"]
    access_secret = request.values["secret_key"]
    admin = Admin(access_key_id=access_key)
    if not admin: return abort(403) #access key DNE
    if admin._id not in study_obj['admins']:
        return abort(403) #admin is not credentialed for this study
    if not admin.validate_access_credentials(access_secret):
        return abort(403) #incorrect secret key
    query = {}
    #select data streams
    if "data_streams" in request.values: #note: researchers use the term "data streams" instead of "data types"
        query["data_types"] = json.loads(request.values["data_streams"])
        for data_stream in query['data_types']:
            if data_stream not in ALL_DATA_STREAMS: return abort(404)
    #select users
    if "user_ids" in request.values:
        query["user_ids"] = [user for user in json.loads(request.values["user_ids"])]
        for user_id in query["user_ids"]: #Case: one of the user ids was invalid
            if not User(user_id): return abort(404)
    #construct time ranges
    if "time_start" in request.values: query["start"] = str_to_datetime(request.values["time_start"])
    if "time_end" in request.values: query["end"] = str_to_datetime(request.values["time_end"])
    registry = {}
    if "registry" in request.values:
        registry = parse_registry(request.values["registry"]) 
    #Do Query
    chunks = ChunksRegistry.get_chunks_time_range(study_id, **query)
    f = StringIO()
    z = ZipFile(f, mode="w", compression=ZIP_DEFLATED)
    ret_reg = {}
    for chunk in chunks:
        if (str(chunk._id) in registry and
            registry[str(chunk._id)] == chunk["chunk_hash"]): continue
        file_name = ( ("%s/%s.csv" if chunk['data_type'] != VOICE_RECORDING else "%s/%s.mp4")
                      % (chunk["data_type"], chunk["time_bin"] ) )
        print file_name
        file_data = s3_retrieve(chunk['chunk_path'], chunk["study_id"], raw_path=True)
        ret_reg[str(chunk._id)] = chunk["chunk_hash"]
        z.writestr(file_name, file_data)
    z.writestr("registry", json.dumps(ret_reg))
    z.close()
    return f.getvalue()


def parse_registry(reg_dat):
    """ Parses the provided registry.dat file and returns a dictionary of chunk
    file names and hashes.  The registry file is a json dictionary containing a
    list of file names and hashes""" 
    return json.loads(reg_dat)

"""############################# Hourly Update ##############################"""

def process_file_chunks():
    """ This is the function that is called from cron.  It runs through all new
    files that have been uploaded and 'chunks' them. Handles logic for skipping
    bad files, raising errors appropriately. """ 
    FileProcessLock.lock()
    error_handler = ErrorHandler()
#     error_handler = null_error_handler
    number_bad_files = 0
    while True:
        starting_length = len(FilesToProcess())
        print starting_length
        number_bad_files += do_process_file_chunks(1000, error_handler, number_bad_files)
        if starting_length == len(FilesToProcess()): break
    FileProcessLock.unlock()
    print len(FilesToProcess())
    error_handler.raise_errors()

def do_process_file_chunks(count, error_handler, skip_count):
    """
    Run through the files to process, pull their data, put it into s3 bins.
    Run the file through the appropriate logic path based on file type.
    
    If a file is empty put its ftp object to the empty_files_list, we can't
        delete objects in-place while iterating over the db. 
    
    All files except for the audio recording mp4 file are in the form of CSVs,
    most of those files can be separated by "time bin" (separated into one-hour
    chunks) and concatenated and sorted trivially. A few files, call log,
    identifier file, and wifi log, require some triage beforehand.  The debug log
    cannot be correctly sorted by time for all elements, because it was not
    actually expected to be used by researchers, but is apparently quite useful.
    
    Any errors are themselves concatenated using the passed in error handler.
    """
    #this is how you declare a defaultdict containing a tuple of two deques.
    binified_data = defaultdict( lambda : ( deque(), deque() ) )
    ftps_to_remove = set([]);
    
    for ftp in FilesToProcess()[skip_count:count+skip_count]:
        with error_handler:
            s3_file_path = ftp["s3_file_path"]
#             print s3_file_path
            data_type = file_path_to_data_type(ftp["s3_file_path"])
            if data_type in CHUNKABLE_FILES:
                file_contents = s3_retrieve(s3_file_path[LENGTH_OF_STUDY_ID:], ftp["study_id"])
                newly_binified_data = process_csv_data(ftp["study_id"],
                                     ftp["user_id"], data_type, file_contents,
                                     s3_file_path)
                if newly_binified_data:
                    append_binified_csvs(binified_data, newly_binified_data, ftp)
                else: # delete empty files from FilesToProcess
                    ftps_to_remove.add(ftp._id)
                continue
            else:
                timestamp = clean_java_timecode( s3_file_path.rsplit("/", 1)[-1][:-4])
#                 print timestamp
                ChunkRegistry.add_new_chunk(ftp["study_id"], ftp["user_id"],
                                            data_type, s3_file_path, timestamp)
                ftps_to_remove.add(ftp._id)
    more_ftps_to_remove, number_bad_files = upload_binified_data(binified_data, error_handler)
    ftps_to_remove.update(more_ftps_to_remove)
    for ftp_id in ftps_to_remove:
        FileToProcess(ftp_id).remove()
    return number_bad_files
    
def upload_binified_data(binified_data, error_handler):
    """ Takes in binified csv data and handles uploading/downloading+updating
        older data to/from S3 for each chunk.
        Returns a set of concatenations that have succeeded and can be removed.
        Returns the number of failed FTPS so that we don't retry them.
        Raises any errors on the passed in ErrorHandler."""
    failed_ftps = set([])
    ftps_to_remove = set([])
    for binn, values in binified_data.items():
        data_rows_deque, ftp_deque = values
        with error_handler:
            study_id, user_id, data_type, time_bin, header = binn
            rows = list(data_rows_deque)
            header = convert_unix_to_human_readable_timestamps(header, rows)
            chunk_path = construct_s3_chunk_path(study_id, user_id, data_type, time_bin) 
            chunk = ChunkRegistry(chunk_path=chunk_path)
            if not chunk:
                ensure_sorted_by_timestamp(rows)
                new_contents = construct_csv_string(header, rows)
                s3_upload( chunk_path, new_contents, study_id, raw_path=True )
                ChunkRegistry.add_new_chunk(study_id, user_id, data_type,
                                chunk_path,time_bin, file_contents=new_contents )
            else:
                s3_file_data = s3_retrieve( chunk_path, study_id, raw_path=True )
                old_header, old_rows = csv_to_list(s3_file_data) 
                if old_header != header:
                    failed_ftps.update(ftp_deque)
                    #TODO: this does not add to the delete queue due to the error... is this correct? I think its fine, handling this using sets.... walk through logic anddetermin if this is correct...
                    raise HeaderMismatchException('%s\nvs.\n%s\nin\n%s' %
                                                  (old_header, header, chunk_path) )
                old_rows.extend(rows)
                ensure_sorted_by_timestamp(old_rows)
                new_contents = construct_csv_string(header, old_rows)
                s3_upload( chunk_path, new_contents, study_id, raw_path=True)
                chunk.update_chunk_hash(new_contents)
            ftps_to_remove.update(ftp_deque)
    #The things in ftps to removed that are not in failed ftps.
    return ftps_to_remove.difference(failed_ftps), len(failed_ftps)


"""################################ S3 Stuff ################################"""

def construct_s3_chunk_path(study_id, user_id, data_type, time_bin):
    """ S3 file paths for chunks are of this form:
        CHUNKED_DATA/study_id/user_id/data_type/time_bin.csv """
    return "%s/%s/%s/%s/%s.csv" % (CHUNKS_FOLDER, study_id, user_id, data_type,
        unix_time_to_string(time_bin*CHUNK_TIMESLICE_QUANTUM) )

"""################################# Key ####################################"""

def file_path_to_data_type(file_path):
    if "/accel/" in file_path: return ACCELEROMETER
    if "/bluetoothLog/" in file_path: return BLUETOOTH
    if "/callLog/" in file_path: return CALL_LOG
    if "/gps/" in file_path: return GPS
    if "/identifiers" in file_path: return IDENTIFIERS
    if "/logFile/" in file_path: return LOG_FILE
    if "/powerState/" in file_path: return POWER_STATE
    if "/surveyAnswers/" in file_path: return SURVEY_ANSWERS
    if "/surveyTimings/" in file_path: return SURVEY_TIMINGS
    if "/textsLog/" in file_path: return TEXTS_LOG
    if "/voiceRecording" in file_path: return VOICE_RECORDING
    if "/wifiLog/" in file_path: return WIFI
    raise Exception("data type unknown: %s" % file_path)

def ensure_sorted_by_timestamp(l):
    """ According to the docs the sort method on a list is in place and should
        faster, this is how to declare a sort by the first column (timestamp). """
    l.sort(key = lambda x: int(x[0]))

def convert_unix_to_human_readable_timestamps(header, rows):
    """ Adds a new column to the end which is the unix time represented in
    a human readable time format.  Returns an appropriately modified header. """
    #lists are implemented as vectors with some proportionally extra space, append should be fine.
    for row in rows:
        unix_millisecond = int(row[0])
        time_string = unix_time_to_string(unix_millisecond / 1000 )
        time_string += "." + str( unix_millisecond % 1000 )
        row.append(time_string)
    return header + HUMAN_READABLE_TIME_LABEL
    

def binify_from_timecode(unix_ish_time_code_string):
    """ Takes a unix-ish time code (accepts unix millisecond), and returns an
        integer value of the bin it should go in. """
    actually_a_timecode = clean_java_timecode(unix_ish_time_code_string) # clean java time codes...
    return actually_a_timecode / CHUNK_TIMESLICE_QUANTUM #separate into nice, clean hourly chunks!

"""############################## Standard CSVs #############################"""

def binify_csv_rows(rows_list, study_id, user_id, data_type, header):
    """ Assumes a clean csv with element 0 in the rows column as a unix(ish) timestamp.
        Sorts data points into the appropriate bin based on the rounded down hour
        value of the entry's unix(ish) timestamp. (based CHUNK_TIMESLICE_QUANTUM)
        Returns a dict of form {(study_id, user_id, data_type, time_bin, heeader):rows_lists}. """
    ret = defaultdict(deque)
    for row in rows_list:
        ret[(study_id, user_id, data_type,
             binify_from_timecode(row[0]), header)].append(row)
    return ret

def append_binified_csvs(old_binified_rows, new_binified_rows, file_to_process):
    """ Appends binified rows to an existing binified row data structure.
        Should be in-place. """
    #ignore the overwrite builtin namespace warning.
    for binn, rows in new_binified_rows.items():
        old_binified_rows[binn][0].extend(rows)  #Add data rows
        old_binified_rows[binn][1].append(file_to_process._id)  #add ftp id

def process_csv_data(study_id, user_id, data_type, file_contents, file_path):
    """ Constructs a binified dict of a given list of a csv rows,
        catches csv files with known problems and runs the correct logic.
        Returns None If the csv has no data in it. """
    header, csv_rows_list = csv_to_list(file_contents)
    if data_type == CALL_LOG: fix_call_log_csv(header, csv_rows_list)
    if data_type == WIFI: header = fix_wifi_csv(header, csv_rows_list, file_path)
    if data_type == IDENTIFIERS: header = fix_identifier_csv(header, csv_rows_list, file_path)
    if csv_rows_list: return binify_csv_rows(csv_rows_list, study_id, user_id, data_type, header)
    else: return None

""" CSV Fixes """
def fix_call_log_csv(header, rows_list):
    """ The call log has poorly ordered columns, the first column should always be
        the timestamp, it has it in column 3.
        Note: older versions of the app name the timestamp column "date". """
    header_list = header.split(",")
    header_list.insert(0, header_list.pop(2))
    header = ",".join(header_list)
    (row.insert(0, row.pop(2)) for row in rows_list)

def fix_identifier_csv(header, rows_list, file_name):
    """ The identifiers file has its timestamp in the file name. """
    time_stamp = file_name.rsplit("_", 1)[-1][:-4]
    return insert_timestamp_single_row_csv(header, rows_list, time_stamp)

def insert_timestamp_single_row_csv(header, rows_list, time_stamp):
    """ Inserts the timestamp field into the header of a csv, inserts the timestamp
        value provided into the first column.  Returns the new header string."""
    header_list = header.split(",")
    header_list.insert(0, "timestamp")
    rows_list[0].insert(0, time_stamp)
    return ",".join(header_list)

def fix_wifi_csv(header, rows_list, file_name):
    """ Fixing wifi requires inserting the same timestamp on EVERY ROW.
    The wifi file has its timestamp in the filename. """
    time_stamp = file_name.rsplit("/", 1)[-1][:-4]
    for row in rows_list[:-1]: #uhg, the last row is a new line.
        row = row.insert(0, time_stamp)
    rows_list.pop(-1) #remove last row
    return "timestamp," + header

""" CSV Utils """
def csv_to_list(csv_string):
    """ Grab a list elements from of every line in the csv, strips off trailing
        whitespace. dumps them into a new list (of lists), and returns the header
        line along with the list of rows. """
    lines = [ line for line in csv_string.splitlines() ]
    return lines[0], [row.split(",") for row in lines[1:]]

def construct_csv_string(header, rows_list):
    """ Takes a header list and a csv and returns a single string of a csv"""
    return header + "\n" + "\n".join( [",".join(row) for row in rows_list ] )

""" Time Handling """
def str_to_datetime(time_string):
    try: return datetime.strptime(time_string, API_TIME_FORMAT)
    except ValueError as e:
        #TODO: document this error (for mat) or change this error 
        if "does not match format" in e.message: abort(400)

def clean_java_timecode(java_time_code_string):
    """ converts millisecond time (string) to an integer normal unix time. """
    return int(java_time_code_string[:10])

def unix_time_to_string(unix_time):
    return datetime.utcfromtimestamp(unix_time).strftime( API_TIME_FORMAT )

""" Exceptions """
class HeaderMismatchException(Exception): pass
