import gc
from boto.exception import S3ResponseError
from bson.objectid import ObjectId
from collections import defaultdict, deque
from config.constants import (API_TIME_FORMAT, IDENTIFIERS, WIFI, CALL_LOG, LOG_FILE,
                              CHUNK_TIMESLICE_QUANTUM, FILE_PROCESS_PAGE_SIZE,
                              VOICE_RECORDING, TEXTS_LOG, SURVEY_TIMINGS, SURVEY_ANSWERS,
                              POWER_STATE, BLUETOOTH, ACCELEROMETER, GPS,
                              PROXIMITY, GYRO, MAGNETOMETER, ANDROID_API, IOS_API,
                              DEVICEMOTION, REACHABILITY, SURVEY_DATA_FILES,
                              CONCURRENT_NETWORK_OPS, CHUNKS_FOLDER, CHUNKABLE_FILES)
from cronutils.error_handler import ErrorHandler
from datetime import datetime
from multiprocessing.pool import ThreadPool

from db.data_access_models import (FileToProcess, FilesToProcess, ChunkRegistry,
                                   FileProcessLock)
from db.user_models import User

from libs.s3 import s3_retrieve, s3_upload


"""########################## Hourly Update Tasks ###########################"""

def process_file_chunks():
    """ This is the function that is called from cron.  It runs through all new
    files that have been uploaded and 'chunks' them. Handles logic for skipping
    bad files, raising errors appropriately. """ 
    error_handler = ErrorHandler()
    FileProcessLock.lock()
    number_bad_files = 0
    run_count = 0
    while True:
        previous_number_bad_files = number_bad_files
        starting_length = FilesToProcess.count()
        print str(datetime.now()), starting_length
        number_bad_files += do_process_file_chunks(FILE_PROCESS_PAGE_SIZE, error_handler, number_bad_files)
        if starting_length == FilesToProcess.count(): #zero files processed
            if previous_number_bad_files == number_bad_files: #every file broke.
                break
            else: continue
    FileProcessLock.unlock()
    print FilesToProcess.count()
    error_handler.raise_errors()

def do_process_file_chunks(count, error_handler, skip_count):
    """
    Run through the files to process, pull their data, put it into s3 bins.
    Run the file through the appropriate logic path based on file type.
    
    If a file is empty put its ftp object to the empty_files_list, we can't
        delete objects in-place while iterating over the db. 
    
    All files except for the audio recording files are in the form of CSVs,
    most of those files can be separated by "time bin" (separated into one-hour
    chunks) and concatenated and sorted trivially. A few files, call log,
    identifier file, and wifi log, require some triage beforehand.  The debug log
    cannot be correctly sorted by time for all elements, because it was not
    actually expected to be used by researchers, but is apparently quite useful.
    
    Any errors are themselves concatenated using the passed in error handler.
    """
    #this is how you declare a defaultdict containing a tuple of two deques.
    binified_data = defaultdict( lambda : ( deque(), deque() ) )
    ftps_to_remove = set([])
    pool = ThreadPool(CONCURRENT_NETWORK_OPS)
    survey_id_dict = {}
    for element in pool.map(batch_retrieve_for_processing,
                          FilesToProcess(page_size=count+skip_count)[skip_count:],
                          chunksize=1):
        with error_handler:
            #raise errors that we encountered in the s3 access threaded operations to the error_handler
            if isinstance(element, Exception): raise element
            file_to_process, data_type, chunkable, file_contents = element
            del element
            s3_file_path = file_to_process["s3_file_path"]
            if chunkable:
                newly_binified_data, survey_id_hash = process_csv_data(file_to_process["study_id"],
                                     file_to_process["user_id"], data_type, file_contents,
                                     s3_file_path)
                if data_type in SURVEY_DATA_FILES:
                    # print survey_id_hash
                    survey_id_dict[survey_id_hash] = resolve_survey_id_from_file_name(s3_file_path)
                if newly_binified_data:
                    append_binified_csvs(binified_data, newly_binified_data, file_to_process)
                else: # delete empty files from FilesToProcess
                    ftps_to_remove.add(file_to_process._id)
                continue
            else:
                timestamp = clean_java_timecode( s3_file_path.rsplit("/", 1)[-1][:-4])

                ChunkRegistry.add_new_chunk(file_to_process["study_id"],
                                            file_to_process["user_id"],
                                            data_type, s3_file_path, timestamp)
                ftps_to_remove.add(file_to_process._id)
    pool.close()
    pool.terminate()
    more_ftps_to_remove, number_bad_files = upload_binified_data(binified_data,error_handler, survey_id_dict)
    ftps_to_remove.update(more_ftps_to_remove)
    for ftp_id in ftps_to_remove:
        FileToProcess(ftp_id).remove()
    gc.collect()
    return number_bad_files
    
def upload_binified_data( binified_data, error_handler, survey_id_dict ):
    """ Takes in binified csv data and handles uploading/downloading+updating
        older data to/from S3 for each chunk.
        Returns a set of concatenations that have succeeded and can be removed.
        Returns the number of failed FTPS so that we don't retry them.
        Raises any errors on the passed in ErrorHandler."""
    failed_ftps = set([])
    ftps_to_retire = set([])
    upload_these = []
    for data_bin, values in binified_data.items():
        data_rows_deque, ftp_deque = values
        with error_handler:
            try:
                study_id, user_id, data_type, time_bin, original_header = data_bin
                rows = list(data_rows_deque)
                updated_header = convert_unix_to_human_readable_timestamps(original_header,
                                                                    rows)
                chunk_path = construct_s3_chunk_path(study_id, user_id, data_type, time_bin)
                chunk = ChunkRegistry(chunk_path=chunk_path)
                if not chunk:
                    ensure_sorted_by_timestamp(rows)
                    new_contents = construct_csv_string(updated_header, rows)
                    upload_these.append((chunk_path, new_contents, study_id))

                    if data_type in SURVEY_DATA_FILES:
                        survey_id_hash = ObjectId(study_id), user_id, data_type, original_header
                        survey_id = survey_id_dict[survey_id_hash]
                        #print survey_id_hash
                    else:
                        survey_id = None
                    ChunkRegistry.add_new_chunk(study_id,
                                                user_id,
                                                data_type,
                                                chunk_path,
                                                time_bin,
                                                file_contents=new_contents,
                                                survey_id=survey_id)
                else:
                    try:
                        s3_file_data = s3_retrieve( chunk_path, study_id, raw_path=True )
                    except S3ResponseError as e:
                        #The following check is correct for boto version 2.38.0
                        if "The specified key does not exist." == e.message:
                            chunk.remove()
                            #This error can only occur if the processing gets actually interrupted and
                            # data files fail to upload after DB entries are created.
                            #Encountered this condition 11pm feb 7 2016, cause unknown, there was
                            #no python stacktrace.  Best guess is mongo blew up.
                            raise ChunkFailedToExist("chunk %s does not actually point to a file, deleting DB entry, should run correctly on next index." % chunk_path)
                        raise #raise original error if not 404 s3 error
                    old_header, old_rows = csv_to_list(s3_file_data)
                    if old_header != updated_header:
#to handle the case where a file was on an hour boundry and placed in two separate
#chunks we need to FAIL to retire this file. If this happens AND ONE of the files
#DOES NOT have a header mismatch this may (will?) cause data duplication in the
#chunked file whenever the file processing occurs run.
                        raise HeaderMismatchException('%s\nvs.\n%s\nin\n%s' %
                                                      (old_header, updated_header, chunk_path) )
                    old_rows.extend(rows)
                    ensure_sorted_by_timestamp(old_rows)
                    new_contents = construct_csv_string(updated_header, old_rows)
                    upload_these.append(( chunk_path, new_contents, study_id ))
                    chunk.update_chunk_hash(new_contents)
            except Exception as e:
                failed_ftps.update(ftp_deque)
                print e
                print ("failed to update: study_id:%s, user_id:%s, data_type:%s, time_bin:%s, header:%s "
                       % (study_id, user_id, data_type, time_bin, updated_header) )
                raise
            ftps_to_retire.update(ftp_deque)
    pool = ThreadPool(CONCURRENT_NETWORK_OPS)
    pool.map(batch_upload, upload_these, chunksize=1)
    pool.close()
    pool.terminate()
    #The things in ftps to removed that are not in failed ftps.
    return ftps_to_retire.difference(failed_ftps), len(failed_ftps)

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
    if "/proximity/" in file_path: return PROXIMITY
    if "/gyro/" in file_path: return GYRO
    if "/magnetometer/" in file_path: return MAGNETOMETER
    if "/devicemotion/" in file_path: return DEVICEMOTION
    if "/reachability/" in file_path: return REACHABILITY
    raise Exception("data type unknown: %s" % file_path)

def ensure_sorted_by_timestamp(l):
    """ According to the docs the sort method on a list is in place and should
        faster, this is how to declare a sort by the first column (timestamp). """
    l.sort(key = lambda x: int(x[0]))

def convert_unix_to_human_readable_timestamps(header, rows):
    """ Adds a new column to the end which is the unix time represented in
    a human readable time format.  Returns an appropriately modified header. """
    for row in rows:
        unix_millisecond = int(row[0])
        time_string = unix_time_to_string(unix_millisecond / 1000 )
        time_string += "." + str( unix_millisecond % 1000 )
        row.insert(1, time_string)
    header = header.split(",")
    header.insert(1, "UTC time")
    return ",".join(header)

def binify_from_timecode(unix_ish_time_code_string):
    """ Takes a unix-ish time code (accepts unix millisecond), and returns an
        integer value of the bin it should go in. """
    actually_a_timecode = clean_java_timecode(unix_ish_time_code_string) # clean java time codes...
    return actually_a_timecode / CHUNK_TIMESLICE_QUANTUM #separate into nice, clean hourly chunks!

def resolve_survey_id_from_file_name(name):
    return name.rsplit("/", 2)[1]

"""############################## Standard CSVs #############################"""

def binify_csv_rows(rows_list, study_id, user_id, data_type, header):
    """ Assumes a clean csv with element 0 in the rows column as a unix(ish) timestamp.
        Sorts data points into the appropriate bin based on the rounded down hour
        value of the entry's unix(ish) timestamp. (based CHUNK_TIMESLICE_QUANTUM)
        Returns a dict of form {(study_id, user_id, data_type, time_bin, heeder):rows_lists}. """
    ret = defaultdict(deque)
    for row in rows_list:
        ret[(study_id, user_id, data_type,
             binify_from_timecode(row[0]), header)].append(row)
    return ret

def append_binified_csvs(old_binified_rows, new_binified_rows, file_to_process):
    """ Appends binified rows to an existing binified row data structure.
        Should be in-place. """
    for data_bin, rows in new_binified_rows.items():
        old_binified_rows[data_bin][0].extend(rows)  #Add data rows
        old_binified_rows[data_bin][1].append(file_to_process._id)  #add ftp

def process_csv_data(study_id, user_id, data_type, file_contents, file_path):
    """ Constructs a binified dict of a given list of a csv rows,
        catches csv files with known problems and runs the correct logic.
        Returns None If the csv has no data in it. """
    user = User(user_id)
    if user['os_type'] == ANDROID_API: #Do fixes for android
        if data_type == LOG_FILE: file_contents = fix_app_log_file(file_contents, file_path)
        header, csv_rows_list = csv_to_list(file_contents)
        if data_type == CALL_LOG: header = fix_call_log_csv(header, csv_rows_list)
        if data_type == WIFI: header = fix_wifi_csv(header, csv_rows_list, file_path)
    else: #do fixes for ios
        header, csv_rows_list = csv_to_list(file_contents)

    # And do these fixes for data regardless of source.
    if data_type == IDENTIFIERS: header = fix_identifier_csv(header, csv_rows_list, file_path)
    if data_type == SURVEY_TIMINGS: header = fix_survey_timings(header, csv_rows_list, file_path)

    #TODO: this is where I stick the strip trailing and leading whitespace per header element.
    header = ",".join([column_name.strip() for column_name in header.split(",")])
    if csv_rows_list:
        return ( binify_csv_rows(csv_rows_list, study_id, user_id, data_type, header ),
                 (study_id, user_id, data_type, header) )
    else: return None, None

"""############################ CSV Fixes #####################################"""

def fix_survey_timings(header, rows_list, file_path):
    """ Survey timings need to have a column inserted stating the survey id they come from."""
    survey_id = file_path.rsplit("/", 2)[1]
    for row in rows_list:
        row.insert(2, survey_id)
    header_list = header.split( "," )
    header_list.insert( 2, "survey id" )
    return ",".join(header_list)

def fix_call_log_csv(header, rows_list):
    """ The call log has poorly ordered columns, the first column should always be
        the timestamp, it has it in column 3.
        Note: older versions of the app name the timestamp column "date". """
    for row in rows_list:
        row.insert(0, row.pop(2))
    header_list = header.split(",")
    header_list.insert(0, header_list.pop(2))
    return ",".join(header_list)

def fix_identifier_csv(header, rows_list, file_name):
    """ The identifiers file has its timestamp in the file name. """
    time_stamp = file_name.rsplit("_", 1)[-1][:-4] + "000"
    return insert_timestamp_single_row_csv(header, rows_list, time_stamp)

def fix_wifi_csv(header, rows_list, file_name):
    """ Fixing wifi requires inserting the same timestamp on EVERY ROW.
    The wifi file has its timestamp in the filename. """
    time_stamp = file_name.rsplit("/", 1)[-1][:-4]
    for row in rows_list[:-1]: #uhg, the last row is a new line.
        row = row.insert(0, time_stamp)
    if rows_list: rows_list.pop(-1)  #remove last row (encountered an empty wifi log on sunday may 8 2016)
    return "timestamp," + header

def fix_app_log_file(file_contents, file_path):
    """ The log file is less of a csv than it is a time enumerated list of
        events, with the time code preceding each row.
        We insert a base value, a new row stating that a new log file was created,
        which allows us to guarantee at least one timestamp in the file."""
    time_stamp = file_path.rsplit("/", 1)[-1][:-4]
    rows_list = file_contents.splitlines()
    rows_list[0] = time_stamp + " New app log file created"
    new_rows = []
    for row in rows_list:
        row_elements = row.split(" ", 1) #split first whitespace, element 0 is a java timecode
        try:
            int(row_elements[0]) #grab first element, check if it is a valid int
            new_rows.append(row_elements)
        except ValueError as e:
            if ("Device does not" == row[:15] or
                "Trying to start Accelerometer" == row[:29] ):
                #use time stamp from previous row
                new_rows.append(new_rows[-1][0] + row)
                continue
            if ("bluetooth Failure" == row[:17] or
                "our not-quite-race-condition" == row[:28] or
                "accelSensorManager" in row[:18] or #this actually covers 2 cases
                "a sessionactivity tried to clear the" == row[:36] ):
                #Just drop matches to the above lines
                continue
            raise
    return "timestamp, event\n" + "\n".join(",".join(row) for row in new_rows)

"""###################################### CSV Utils ##################################"""

def insert_timestamp_single_row_csv(header, rows_list, time_stamp):
    """ Inserts the timestamp field into the header of a csv, inserts the timestamp
        value provided into the first column.  Returns the new header string."""
    header_list = header.split(",")
    header_list.insert(0, "timestamp")
    rows_list[0].insert(0, time_stamp)
    return ",".join(header_list)

def csv_to_list(csv_string):
    """ Grab a list elements from of every line in the csv, strips off trailing
        whitespace. dumps them into a new list (of lists), and returns the header
        line along with the list of rows. """
    #TODO: refactor so that we don't have 3x data memory usage mid-run
    lines = [ line for line in csv_string.splitlines() ]
    return lines[0], [row.split(",") for row in lines[1:]]

def construct_csv_string(header, rows_list):
    """ Takes a header list and a csv and returns a single string of a csv.
        Now handles unicode errors.  :D :D :D """
    #TODO: make the list comprehensions in-place map operations
    ret = header.decode("utf") + u"\n" + u"\n".join( [u",".join([x.decode("utf") for x in row]) for row in rows_list ] )
    return ret.encode("utf")

def clean_java_timecode(java_time_code_string):
    """ converts millisecond time (string) to an integer normal unix time. """
    return int(java_time_code_string[:10])

def unix_time_to_string(unix_time):
    return datetime.utcfromtimestamp(unix_time).strftime( API_TIME_FORMAT )

""" Batch Operations """
def batch_retrieve_for_processing(ftp):
    """ Used for mapping an s3_retrieve function. """
    data_type = file_path_to_data_type(ftp['s3_file_path'])
    if data_type in CHUNKABLE_FILES:
        #in the event of an error (boto error) we actually RETURN that error and
        # handle it back on the main thread.
        try: return ftp, data_type, True, s3_retrieve(ftp['s3_file_path'], ftp["study_id"], raw_path=True)
        except Exception as e: return e
    else: return ftp, data_type, False, ""
    
def batch_upload(upload):
    """ Used for mapping an s3_upload function. """
    s3_upload(*upload, raw_path=True)

""" Exceptions """
class HeaderMismatchException(Exception): pass
class ChunkFailedToExist(Exception): pass
