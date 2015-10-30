from bson import ObjectId
from cronutils import ErrorHandler
from datetime import datetime
from flask import Blueprint, request, abort, json
from collections import defaultdict
from _collections import deque

data_access_api = Blueprint('data_access_api', __name__)

from db.data_access_models import FilesToProcess, ChunksRegistry,FileProcessLock
from db.study_models import Studies
from db.user_models import Admins
from libs.s3 import s3_retrieve, s3_list_files, s3_upload, s3_retreive_or_none_for_chunking, s3_upload_chunk

class HeaderMismatchException(Exception): pass

# def binify():
#    binifying is the process of separating elements into a predetermined bin
#    structure, e.g. stuffing all csv rows into their appropriate hourly bins.

API_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S"
"""1990-01-31T07:30:04 gets you jan 31 1990 at 7:30:04am
   human string is YYYY-01-31Thh:mm:ss """

CHUNKS_FOLDER = "CHUNKED_DATA"

CSV_FILES = ["accel", "bluetoothLog", "callLog", "gps", "powerState", "textsLog"]
CSV_FILES_WITH_PROBLEMS = ["callLog"]

CHUNK_TIMESLICE_QUANTUM = 3600 #each chunk represents 1 hour of data, and because unix time 0 is on an hour boundry our time codes will also be on nice, clean hour boundaries

ALL_DATA_STREAMS = []

LENGTH_OF_STUDY_ID = 24

# UNIX_EPOCH_START = datetime.fromtimestamp(0)
# def get_unix_time(dt):
#     return (dt - UNIX_EPOCH_START).totalseconds()

data_access_api.route("/get_data/v1", methods=['POST'])
def grab_data():
    """    required: access key
    required: access secret
    data streams (json blob) - default to all
    users (json blob) - defaults to all
    required: study
    date-start (define format)
    date-end (define format)
    top-up = a file (registry.dat)
    
    cases handled: 
    missing creds or study
    invalid admin
    invalid study
    study does not grant this admin access
    invalid creds (able to get admin via access key and secret is validated)"""
    
    if "access_key" not in request.values: abort(403)
    if "access_secret" not in request.values: abort(403)
    if "study_id" not in request.values: abort(400)
    
    access_key = request.values["access_key"]
    access_secret = request.values["access_secret"]
    study_id = ObjectId(request.values["study_id"])
    study_obj = Studies(study_id) 
    
    if not Studies(study_id): abort(400)
    
    admin = Admins(secret_key=access_key)
    if not admin: abort(403)
    if admin["_id"] not in study_obj['admins']: abort(403)
    if not admin.validate_access_credentials(access_secret): abort(403)
    
    query = {}
    
    if "data_streams" in request.values:
        query["data_streams"] = json.loads(request.values["data_streams"])
    else: query["data_streams"] = ALL_DATA_STREAMS
    
    if "user_ids" in request.values: 
        query["users_ids"] = [ObjectId(user) for user in json.loads(request.values["users"])]
    else: query["users_ids"] = study_obj.get_users_in_study()
    
    if "date_start" in request.values:
        query["start"] = datetime.strptime(request.values["date_start"])
    if "date_end" in request.values:
        query["end"] = datetime.strptime(request.values["date_end"])
    
    chunks_raw = ChunksRegistry.get_chunks_time_range(study_id, **query)
    chunks_processed = {user_id:{} for user_id in query["user_id"]}
    for chunk in chunks_raw:
        chunks_processed[chunk["user_id"]].update({chunk["s3_file_path"]:chunk["chunk_hash"]})
    
    print chunks_processed
    
    #TODO: 
    
#     chunk_data = {}
#     if "top_up" in request.values:
#         top_up = json.loads(request.values["top_up"])
    

################################ Hourly Update #################################
#TODO: Eli, for testing make this only run on a single user's data...
import sys
def process_file_chunks():
    FileProcessLock.lock()  #TODO: Eli. Don't forget about this.
    error_handler = ErrorHandler()
    binified_data = defaultdict(deque)
    for ftp in FilesToProcess()[:10]: #TODO: DON"T FORGET TO DELETE
#         with error_handler:
            data_type = file_path_to_data_type(ftp["s3_file_path"])
#             file_contents = s3_retrieve(ftp["s3_file_path"][LENGTH_OF_STUDY_ID:], ftp["study_id"])
            if data_type in CSV_FILES:
                file_contents = s3_retrieve(ftp["s3_file_path"][LENGTH_OF_STUDY_ID:], ftp["study_id"])
                newly_binified_data = handle_csv_data(ftp["study_id"],
                                     ftp["user_name"], data_type, file_contents)
                append_binified_csvs(binified_data, newly_binified_data)
                print "working..."
                continue
#             if data_type == "wifiLog": pass #requires file timestamp, redirect or bin?
#             if data_type == "identifiers": pass #work out how to concat
#             if data_type == "surveyAnswers": pass #redirect
#             if data_type == "surveyTimings": pass #redirect
#             if data_type == "voiceRecording": pass #redirect
#             if data_type == "logFile": pass #I have literally no clue.
    print "======== PART 2 ========"
    for bin, deque_rows in binified_data.items():  #TODO: pretty sure that rows var is not going to unpack correctly...
        study_id, user_name, data_type, time_bin, header = bin
        rows = list(deque_rows)
        file_path = construct_s3_chunk_path(study_id, user_name, data_type, time_bin) 
#         with error_handler:
        s3_file_data = s3_retreive_or_none_for_chunking( file_path, study_id )
        if not s3_file_data:
            ensure_sorted_by_timestamp(rows)
            s3_upload_chunk( file_path, construct_csv_string(header, rows), study_id ) #TODO: Eli. This study_id requires an ObjectId
        else:
            old_header, old_rows = csv_to_list(s3_file_data) 
            if old_header != header: raise HeaderMismatchException
            #binified_old_rows = binify_csv_rows(old_rows, study_id, user_name, data_type) #TODO: THis is ... I.m pretty sure, not necessary.
            old_rows.extend(rows)
            ensure_sorted_by_timestamp(old_rows)
            #TODO: check overwriting behavior when uploading this file to existing s3 path.
            s3_upload_chunk( file_path, construct_csv_string(header, old_rows), study_id)
#     error_handler.raise_errors()
    
def construct_s3_chunk_path(study_id, user_name, data_type, time_bin):
    """ S3 file paths for chunks are of the form
        CHUNKED_DATA/study_id/user_name/data_type/time_bin.csv """
    return "%s/%s/%s/%s/%s.csv" % (CHUNKS_FOLDER, study_id, user_name,
                                   data_type, time_bin)

def reverse_s3_chunk_path(path):
    (CHUNKS_FOLDER, study_id, user_name, data_type, time_bin) = path.split("/")
    
################################# Standard CSVs #################################

def handle_csv_data(study_id, user_name, data_type, file_contents):
    """ Constructs a binified dict of a given list of a csv rows,
        catches csv files with known problems and runs the correct logic. """
    header, csv_rows_list = csv_to_list(file_contents)
    # INSERT more data fixes below as we encounter them.
    if data_type == "callLog":
        fix_call_log_csv(header, csv_rows_list)
    # Binify!
    return binify_csv_rows(csv_rows_list, study_id, user_name, data_type, header)

def binify_csv_rows(rows_list, study_id, user_name, data_type, header):
    """ Assumes a clean csv with element 0 in the rows list as a unix(ish) timestamp.
        sorts data points into the appropriate bin based on the rounded down hour
        value of the entry's unix(ish) timestamp.
        Returns a dict of form {(study_id, user_name, data_type, time_bin, heeader):rows_lists}. """
    ret = defaultdict(deque)
    for row in rows_list:
        ret[(study_id, user_name, data_type, #This does not really have a way to speed up the dict hashing...
             binify_from_timecode(row[0]), header)].append(row)
    return ret
    
# CSV fixes
def fix_call_log_csv(header, rows_list):
    """ The call log has poorly ordered columns, the first column should always be
        the timestamp, it has it in column 3. """
    header_list = header.split(",")
    header_list.insert(0, header_list.pop(2))
    header = ",".join(header_list)
    #TODO: Eli. insert is O(n), not O(1), consider using a deque.
    (row.insert(0, row.pop(2)) for row in rows_list) 

# CSV transforms
def csv_to_list(csv_string):
    """ Grab a list elements from of every line in the csv, strips off trailing
        whitespace. dumps them into a new list (of lists), and returns the header
        line along with the list of rows. """ 
    lines = [ line for line in csv_string.splitlines() ]
    return lines[0], [row.split(",") for row in lines[1:]]

def construct_csv_string(header, rows_list):
    """ Takes a header list and a csv and returns a single string of a csv"""
    return header + "\n" + "\n".join( [",".join(row) for row in rows_list ] )

#################################### Key #######################################

def file_path_to_data_type(file_path):
    if "/accel/" in file_path: return "accel"
    if "/bluetoothLog/" in file_path: return "bluetoothLog"
    if "/callLog/" in file_path: return "callLog"
    if "/gps/" in file_path: return "gps"
    if "/logFile/" in file_path: return "logFile"
    if "/powerState/" in file_path: return "powerState"
    if "/surveyAnswers/" in file_path: return "surveyAnswers"
    if "/surveyTimings/" in file_path: return "surveyTimings"
    if "/textsLog/" in file_path: return "textsLog"
    if "/wifiLog/" in file_path: return "wifiLog"
    if "/identifiers" in file_path: return "identifiers"
    if "/voiceRecording" in file_path: return "voiceRecording"
    raise TypeError("data type unknown: %s" % file_path)

from operator import itemgetter
def ensure_sorted_by_timestamp(l):
    """ According to the docs the sort method on a list is in place and should
        faster, this is how to declare a sort by the first column (timestamp). """
    l.sort(key = lambda x: int(x[0]))

def binify_from_timecode(unix_ish_time_code):
    """ Takes a unix-ish time code (accepts unix millisecond), and returns an
        integer value of the bin it should go in. """
    actually_a_timecode = int(unix_ish_time_code[:10]) # clean java time codes...
    return actually_a_timecode / CHUNK_TIMESLICE_QUANTUM #separate into nice, clean hourly chunks!

def append_binified_csvs(old_binified_rows, new_binified_rows):
    """ Appends binified rows to an existing binified row data structure.
        Should be in-place. """
    #ignore the overwrite builtin namespace warning.
    for bin, rows in new_binified_rows.items():
        old_binified_rows[bin].extend(rows)
