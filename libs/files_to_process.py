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
                              CONCURRENT_NETWORK_OPS, CHUNKS_FOLDER, CHUNKABLE_FILES,
                              DATA_PROCESSING_NO_ERROR_STRING)
from cronutils.error_handler import ErrorHandler, null_error_handler
from datetime import datetime
from multiprocessing.pool import ThreadPool

from db.data_access_models import (FileToProcess, FilesToProcess, ChunkRegistry,
                                   FileProcessLock)
from db.user_models import User

from libs.s3 import s3_retrieve, s3_upload


class EverythingWentFine(Exception): pass
class ProcessingOverlapError(Exception): pass

"""########################## Hourly Update Tasks ###########################"""

def process_file_chunks():
    """ This is the function that is called from cron.  It runs through all new
    files that have been uploaded and 'chunks' them. Handles logic for skipping
    bad files, raising errors appropriately. """
    error_handler = ErrorHandler()
    if FileProcessLock.islocked():
        raise ProcessingOverlapError("Data processing overlapped with a previous data indexing run.")
    FileProcessLock.lock()
    number_bad_files = 0
    run_count = 0
    while True:
        previous_number_bad_files = number_bad_files
        starting_length = FilesToProcess.count()
        print str(datetime.now()), starting_length
        number_bad_files += do_process_file_chunks(FILE_PROCESS_PAGE_SIZE, error_handler, number_bad_files)
        if starting_length == FilesToProcess.count(): #zero files processed
            if previous_number_bad_files == number_bad_files:
                # Cases:
                # every file broke, would cause infinite loop.
                # no new files.
                break
            else: continue
    FileProcessLock.unlock()
    print FilesToProcess.count()
    error_handler.raise_errors()
    raise EverythingWentFine(DATA_PROCESSING_NO_ERROR_STRING)

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
    all_binified_data = defaultdict( lambda : ( deque(), deque() ) )
    ftps_to_remove = set([])
    pool = ThreadPool(CONCURRENT_NETWORK_OPS)
    survey_id_dict = {}

    for data in pool.map(batch_retrieve_for_processing,
                          FilesToProcess(page_size=count+skip_count)[skip_count:],
                          chunksize=1):
        with error_handler:
            #raise errors that we encountered in the s3 access threaded operations to the error_handler
            if data['exception']:
                raise data['exception']

            if data['chunkable']:
                # print "1a"
                newly_binified_data, survey_id_hash = process_csv_data(data)
                # print data, "\n1b"
                if data['data_type'] in SURVEY_DATA_FILES:
                    # print survey_id_hash
                    survey_id_dict[survey_id_hash] = resolve_survey_id_from_file_name(data['ftp']["s3_file_path"])
                if newly_binified_data:
                    # print "1c"
                    append_binified_csvs(all_binified_data, newly_binified_data, data['ftp'])
                else: # delete empty files from FilesToProcess
                    # print "1d"
                    ftps_to_remove.add(data['ftp']._id)
                continue

            else:#if not data['chunkable']
                # print "2a"
                timestamp = clean_java_timecode( data['ftp']["s3_file_path"].rsplit("/", 1)[-1][:-4])
                # print "2a"
                ChunkRegistry.add_new_chunk(data['ftp']["study_id"],
                                            data['ftp']["user_id"],
                                            data['data_type'],
                                            data['ftp']["s3_file_path"],
                                            timestamp)
                # print "2b"
                ftps_to_remove.add(data['ftp']._id)

    pool.close()
    pool.terminate()
    # print 3
    more_ftps_to_remove, number_bad_files = upload_binified_data(all_binified_data, error_handler, survey_id_dict)
    # print "X"
    ftps_to_remove.update(more_ftps_to_remove)
    for ftp_id in ftps_to_remove:
        FileToProcess(ftp_id).remove()
    # print "Y"
    gc.collect()
    # print "Z"
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
    for data_bin, (data_rows_deque, ftp_deque) in binified_data.items():
        # print 3
        with error_handler:
            try:
                # print 4
                study_id, user_id, data_type, time_bin, original_header = data_bin
                # print 5
                rows = list(data_rows_deque)
                updated_header = convert_unix_to_human_readable_timestamps(original_header, rows)
                # print 6
                chunk_path = construct_s3_chunk_path(study_id, user_id, data_type, time_bin)
                # print 7
                chunk = ChunkRegistry(chunk_path=chunk_path)
                if not chunk:
                    # print "7a"
                    ensure_sorted_by_timestamp(rows)
                    # print "7b"
                    if data_type == SURVEY_TIMINGS:
                        # print "7ba"
                        new_contents = construct_utf_safe_csv_string(updated_header, rows)
                    else:
                        # print "7bc"
                        new_contents = construct_csv_string(updated_header, rows)
                    # print "7c"
                    if data_type in SURVEY_DATA_FILES:
                        #We need to keep a mapping of files to survey ids, that is handled here.
                        # print "7da"
                        survey_id_hash = ObjectId(study_id), user_id, data_type, original_header
                        survey_id = survey_id_dict[survey_id_hash]
                        #print survey_id_hash
                    else:
                        # print "7db"
                        survey_id = None
                    # print "7e"
                    chunk_params = {"study_id":study_id,
                                    "user_id":user_id,
                                    "data_type":data_type,
                                    "chunk_path":chunk_path,
                                    "time_bin":time_bin,
                                    "survey_id":survey_id}
                    upload_these.append((chunk_params, chunk_path, new_contents.encode("zip"), study_id ))
                else:
                    try:
                        # print 8
                        # print chunk_path
                        s3_file_data = s3_retrieve( chunk_path, study_id, raw_path=True )
                        # print "finished s3 retrieve"
                    except S3ResponseError as e:
                        # print 9
                        #The following check is correct for boto version 2.38.0
                        if "The specified key does not exist." == e.message:
                            chunk.remove()
                            #This error can only occur if the processing gets actually interrupted and
                            # data files fail to upload after DB entries are created.
                            #Encountered this condition 11pm feb 7 2016, cause unknown, there was
                            #no python stacktrace.  Best guess is mongo blew up.
                            raise ChunkFailedToExist("chunk %s does not actually point to a file, deleting DB entry, should run correctly on next index." % chunk_path)
                        raise #raise original error if not 404 s3 error
                    # print 10
                    old_header, old_rows = csv_to_list(s3_file_data)
                    if old_header != updated_header:
#to handle the case where a file was on an hour boundry and placed in two separate
#chunks we need to FAIL to retire this file. If this happens AND ONE of the files
#DOES NOT have a header mismatch this may (will?) cause data duplication in the
#chunked file whenever the file processing occurs run.
                        raise HeaderMismatchException('%s\nvs.\n%s\nin\n%s' %
                                                      (old_header, updated_header, chunk_path) )
                    # print 11
                    old_rows = [_ for _ in old_rows]
                    # print "11a"
                    old_rows.extend(rows)
                    # print "11b"
                    del rows
                    # print 12
                    ensure_sorted_by_timestamp(old_rows)
                    # print 13

                    if data_type == SURVEY_TIMINGS:
                       # print "13a"
                        new_contents = construct_utf_safe_csv_string(updated_header, old_rows)
                    else:
                        # print "13b"
                        new_contents = construct_csv_string(updated_header, old_rows)
                    del old_rows
                    # print 14
                    upload_these.append((chunk, chunk_path, new_contents.encode("zip"), study_id ))
                    del new_contents
            except Exception as e:
                failed_ftps.update(ftp_deque)
                print e
                print ("failed to update: study_id:%s, user_id:%s, data_type:%s, time_bin:%s, header:%s "
                       % (study_id, user_id, data_type, time_bin, updated_header) )
                raise
            ftps_to_retire.update(ftp_deque)

    # pool = ThreadPool(CONCURRENT_NETWORK_OPS)
    # pool = ThreadPool(1)
    pool = dummy_threadpool()
    errors = pool.map(batch_upload, upload_these, chunksize=1)
    for e in errors:
        if isinstance(e, Exception):
            raise e

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
        # this line 0-pads millisecond values that have leading 0s.
        time_string += ".%03d" % ( unix_millisecond % 1000 )
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

def process_csv_data(data):
    #in order to reduce memory overhead this function was changed to take a dictionary instead of args
    """ Constructs a binified dict of a given list of a csv rows,
        catches csv files with known problems and runs the correct logic.
        Returns None If the csv has no data in it. """
    user = User(data['ftp']['user_id'])

    if user['os_type'] == ANDROID_API: #Do fixes for android
        if data["data_type"] == LOG_FILE:
            data['file_contents'] = fix_app_log_file(data['file_contents'], data['ftp']['s3_file_path'])

        header, csv_rows_list = csv_to_list(data['file_contents'])
        if data["data_type"] != ACCELEROMETER:
            #we only really care about memory safety in the accelerometer data file... probably
            csv_rows_list = [r for r in csv_rows_list]

        if data["data_type"] == CALL_LOG:
            header = fix_call_log_csv(header, csv_rows_list)
        if data["data_type"] == WIFI:
            header = fix_wifi_csv(header, csv_rows_list, data['ftp']['s3_file_path'])
    else: #do fixes for ios
        header, csv_rows_list = csv_to_list(data['file_contents'])
        if data["data_type"] != ACCELEROMETER:
            csv_rows_list = [r for r in csv_rows_list]

    del data['file_contents']

    # And do these fixes for data regardless of source.
    if data["data_type"] == IDENTIFIERS:
        header = fix_identifier_csv(header, csv_rows_list, data['ftp']['s3_file_path'])
    if data["data_type"] == SURVEY_TIMINGS:
        header = fix_survey_timings(header, csv_rows_list, data['ftp']['s3_file_path'])

    header = ",".join([column_name.strip() for column_name in header.split(",")])
    if csv_rows_list:
        return (
            #return item 1: the data
            binify_csv_rows(csv_rows_list,
                            data['ftp']['study_id'],
                            data['ftp']['user_id'],
                            data["data_type"],
                            header ),
            #return item 2: the tuple that we use as a convenient hash
            (data['ftp']['study_id'], data['ftp']['user_id'], data["data_type"], header) )
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
    if rows_list:rows_list.pop(-1)  #remove last row (encountered an empty wifi log on sunday may 8 2016)
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
    #rewitten to be more memory efficient than fast by making it a generator
    # Note that almost all of the time is spent in the per-row for-loop
    def split_yielder(l):
        for row in l:
            yield row.split(",")
    header = csv_string[:csv_string.find("\n")]
    lines = csv_string.splitlines()
    lines.pop(0) #this line is annoyingly slow, but its fine...
    del csv_string
    return header, split_yielder(lines)

def construct_csv_string(header, rows_list):
    """ Takes a header list and a csv and returns a single string of a csv.
        Now handles unicode errors.  :D :D :D """
    # the list comprehension was, it turned out, both nonperformant and of an incomprehensible memory order.
    # this is ~1.5x faster, and has a very clear
    #also, the unicode modification is an order of magnitude slower.
    def deduplicate(seq):
        #highly optimized order preserving deduplication function.
        # print "dedupling"
        seen = set()
        seen_add = seen.add
        return [x for x in seq if not (x in seen or seen_add(x))]
    # print "rows 1"
    rows = []
    for row_items in rows_list:
        rows.append(",".join(row_items))
    del rows_list, row_items
    #we need to ensure no duplicates
    # print "rows 2"
    rows = deduplicate(rows)
    # print "rows 3"
    ret = header
    for row in rows:
        ret += "\n" + row
    return ret

def construct_utf_safe_csv_string(header, rows_list):
    """ Takes a header list and a csv and returns a single string of a csv.
        Poor memory performances, but handles unicode errors.  :D :D :D """
    """ Takes a header list and a csv and returns a single string of a csv.
        Now handles unicode errors.  :D :D :D """
    # the list comprehension was, it turned out, both nonperformant and of an incomprehensible memory order.
    # this is ~1.5x faster, and has a very clear
    #also, the unicode modification is an order of magnitude slower.
    def deduplicate(seq):
        #highly optimized order preserving deduplication function.
        # print "dedupling"
        seen = set()
        seen_add = seen.add
        return [x for x in seq if not (x in seen or seen_add(x))]
    # print "rows 1"
    rows = []
    for row_items in rows_list:
        rows.append(u",".join([r.decode("utf") for r in row_items]))
    del rows_list, row_items
    #we need to ensure no duplicates
    # print "rows 2"
    rows = deduplicate(rows)
    # print "rows 3"
    ret = header.decode('utf')
    for row in rows:
        ret += u"\n" + row
    return ret.encode('utf')

def clean_java_timecode(java_time_code_string):
    """ converts millisecond time (string) to an integer normal unix time. """
    return int(java_time_code_string[:10])

def unix_time_to_string(unix_time):
    return datetime.utcfromtimestamp(unix_time).strftime( API_TIME_FORMAT )

""" Batch Operations """
def batch_retrieve_for_processing(ftp):
    """ Used for mapping an s3_retrieve function. """
    data_type = file_path_to_data_type(ftp['s3_file_path'])
    ret = {'ftp':ftp,
           "data_type":data_type,
           'exception':None,
           "file_contents":"" }
    if data_type in CHUNKABLE_FILES:
        ret['chunkable'] = True
        try: #handle s3 errors
            # print ftp['s3_file_path'], "\ngetting data..."
            ret['file_contents'] = s3_retrieve(ftp['s3_file_path'], ftp["study_id"], raw_path=True)
            # print "finished getting data"
        except Exception as e:
            ret['exception'] = e
    else:
        #We don't do anything with unchunkable data.
        ret['chunkable'] = False
        ret['data'] = ""
    return ret

def batch_upload(upload):
    """ Used for mapping an s3_upload function. """
    try:
        if len(upload) != 4:
            print upload
        chunk, chunk_path, new_contents, study_id = upload
        del upload
        new_contents = new_contents.decode("zip")
        s3_upload(chunk_path, new_contents, study_id, raw_path=True)
        # print "data uploaded!"
        if isinstance(chunk, ChunkRegistry):
            chunk.low_memory_update_chunk_hash( new_contents )
        else:
            ChunkRegistry.add_new_chunk(chunk['study_id'],
                                        chunk['user_id'],
                                        chunk['data_type'],
                                        chunk['chunk_path'],
                                        chunk['time_bin'],
                                        file_contents=new_contents, #unlikely to be huge.
                                        survey_id=chunk['survey_id'])
    except Exception as e:
        return e

""" Exceptions """
class HeaderMismatchException(Exception): pass
class ChunkFailedToExist(Exception): pass


class dummy_threadpool():
    def map(self, *args, **kwargs): #the existance of that self variable is key
        # we actually want to cut off any threadpool args, which is conveniently easy because map does not use kwargs!
        return map(*args)
    def terminate(self): pass
    def close(self): pass
