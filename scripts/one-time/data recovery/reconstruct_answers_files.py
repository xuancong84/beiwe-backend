from db.data_access_models import FileToProcess

cpaste
import cPickle, os, collections
from bson.objectid import ObjectId
from datetime import datetime, timedelta
from time import mktime
from mongolia.errors import NonexistentObjectError

from multiprocessing.pool import ThreadPool
from db.study_models import Studies, Survey, Study
from db.user_models import Users
from libs.s3 import s3_list_files, s3_retrieve, s3_upload


class UnableToReconcileError(Exception): pass
class ItemTooEarlyException( Exception ): pass
class ItemTooLateException( Exception ): pass
class NoBackupSurveysException( Exception ): pass
class UnableToFindSurveyError( Exception ): pass

"""
Cases:
    no submit button
        probably ignore them.
    missing questions:
        pretty good: compile data from all backups of surveys, use that survey as the
        canonical survey for that question for identifying missingn questions
        ~fuzzy: compile a survey is mapping to all uuids questions ever contained in that
"""
########################### annoying stuff to declare early ############################
#a map of the string value on the timings file to the answers file for question types
question_type_map ={'slider': "Slider Question",
                    'radio_button': "Radio Button Question",
                    'checkbox': "Checkbox Question",
                    'free_response': "Open Response Question"}
good_messages ={
    "no_answers":"there were no answered questions,", #not the same as no submit
    "everything_answered":"all questions answered,",
    "all_missing_recovered":"all missing questions recovered,",
    "no_extra_questions":"no extra questions.",
    "1_not_2_resolved":"all questions present in survey 1 but not in 2, resolved.",
    "2_not_1_resolved":"all questions present in survey 2 but not in 1, resolved.",
    "extra_1_resolved":"survey 1 would have had extra questions, resolved.",
    "extra_2_resolved":"survey 2 would have had extra questions, resolved.",
    "reordered_questions":"there were no missing or extra questions for either survey "
                       "this means question order was changed, and it is resolved. ",
    "no_extra_1":"but survey 1 has no extra questions, resolved.",
    "no_extra_2":"but survey 2 has no extra questions, resolved.",
}
bad_messages = {
    "has_no_submit":"this file did not contain a submission button press",
    "extra_questions":"encountered extra questions in answers",
    "only_header":"this file consisted only of a header",
    "no_mappings":"survey was changed and there were answers provided that did not map "
                  "to _either_ survey. Could not resolve.",
    "not_enough_answers":"survey was changed and user did not answer enough questions "
                         "to determine which survey. Could not resolve.",
}
other_messages = {
    "2_potential":"There are two potential surveys for this question...",
    "both_missing":"both surveys have missing answers...",
    "no_survey_1":"unable to find survey.",  #may still be recovered in live survey
    "no_survey_2":"could not find a survey in survey history"
}


def conditionally_setup_debug_stuff():
    global_vars = globals( )
    if 'debug_files' not in global_vars:
        debug_files = [f for f in get_all_timings_files() if "55d3826297013e3a1c9b8c3e" in f]
    else: debug_files = global_vars['debug_files']
    if "debug_file_data" not in global_vars:
        debug_file_data = get_data_for_raw_file_paths( debug_files )
    else: debug_file_data = global_vars['debug_file_data ']
    return debug_files, debug_file_data

def conditionally_setup_fo_realzies_stuff():
    global_vars = globals( )
    if 'all_files' not in global_vars:
        all_files = get_all_timings_files()
    else: all_files = global_vars['all_files']
    if "all_file_data" not in global_vars:
        all_file_data = get_data_for_raw_file_paths( all_files )
    else: all_file_data = global_vars['all_file_data']
    return all_files, all_file_data


############################### Administrative functions ###############################

def debug(old_surveys=None, ignore_unsubmitted=True):
    debug_files, debug_data_files = conditionally_setup_debug_stuff()
    # uuids = get_uuids(debug_data_files)
    stuff = do_run( debug_data_files, old_surveys=old_surveys, ignore_unsubmitted=True )
    return stuff


# def fo_realzies( old_surveys=None, ignore_unsubmitted=True ):
#     all_files, all_file_data = conditionally_setup_fo_realzies_stuff()
#     # uuids = get_uuids( all_file_data )
#     stuff = do_run( all_file_data, old_surveys=old_surveys, ignore_unsubmitted=True )
#     return stuff

def do_run(file_paths_and_contents, old_surveys=None, ignore_unsubmitted=True):
    if old_surveys == None: raise Exception( "OLD SURVEYS NOT PRESENT" )
    ret = {}
    for data, fp in file_paths_and_contents:
        study, timecode, csv, status_update = construct_answers_csv( data, fp,
                                                      old_surveys=old_surveys,
                                                      ignore_unsubmitted=ignore_unsubmitted)
        # if study and timecode and csv: #drop any return where a value is None
        ret[fp] = status_update
    return ret


def get_resolvable_survey_timings(from_do_run):
    ret = {}
    for k, v in from_do_run.items():
        for m in bad_messages.values():
            if m in v: break
        if m not in v:
            ret[k] = v
    return ret

def do_actually_run(file_paths, old_surveys=None):
    if old_surveys == None: raise Exception("OLD SURVEYS NOT PRESENT")
    file_paths_and_contents = get_data_for_raw_file_paths(file_paths)
    ret = {}
    for data, fp in file_paths_and_contents:
        study, timecode, csv, status_update = construct_answers_csv( data, fp,
                                                      old_surveys=old_surveys)
        # if study and timecode and csv: #drop any return where a value is None
        ret[fp] = csv,timecode
    return ret

def do_upload(file_paths_and_contents, data_type=None, forcibly_overwrite=False):
    if data_type == None: raise Exception("DATA TYPE!")
    upload_stream_map = { "survey_answers":("surveyAnswers", "csv"),
                          "audio":("voiceRecording", "mp4") }
    data_stream_string, file_extension = upload_stream_map[data_type]

    for timings_path, contents_and_timestamp in file_paths_and_contents.items():
        contents, timestamp = contents_and_timestamp
        study_id_string, user_id, _, survey_id, _ = timings_path.split("/")
        try:
            timestamp_string = str( int( mktime( timestamp.timetuple( ) ) ) ) + "000"
        except AttributeError:
            print "PROBLEM WITH TIMESTAMP FROM: %s" % timings_path
            continue
        if len(timestamp_string) != 13:
            raise Exception("LOL! No.")

        study_obj_id = Study(ObjectId(study_id_string))._id

        s3_file_path = "%s/%s/%s/%s/%s.%s" % (study_id_string,
                                              user_id,
                                              data_stream_string,
                                              survey_id,
                                              timestamp_string,
                                              file_extension)
        if len(s3_list_files(s3_file_path)) != 0:
            print "ALREADY_EXISTS: %s, %s" % (timings_path, s3_file_path)
            if forcibly_overwrite == False:
                continue
        else: print "yay!: ", s3_file_path
        contents = contents.encode("utf8") #maybe make this unicode-16?

        s3_upload(s3_file_path, contents, study_obj_id, raw_path=True)
        FileToProcess.append_file_for_processing( s3_file_path, study_obj_id, user_id )

def get_all_timings_files( ):
    # get users associated with studies
    study_users = { str( s._id ):Users( study_id=s._id, field='_id' ) for s in
                    Studies( ) }
    all_user_timings = []
    for sid, users in study_users.items( ):  # construct prefixes
        all_user_timings.extend(
                [sid + "/" + u + "/" + "surveyTimings" for u in users] )
    # use a threadpool to efficiently get all those strings of s3 paths we
    # will need
    pool = ThreadPool( len( all_user_timings ) )
    try:
        files_lists = pool.map( s3_list_files, all_user_timings )
    except Exception:
        raise
    finally:
        pool.close( )
        pool.terminate( )

    files_list = []
    for l in files_lists: files_list.extend( l )
    # we need to purge the occasional pre-multistudy file, and ensure it is utf encoded.
    return [f.decode( "utf8" ) for f in files_list if f.count( '/' ) == 4]

def get_data_for_raw_file_paths( timings_files ):
    # Pulls in (timings) files from s3
    pool = ThreadPool( 50 )

    def batch_retrieve( parameters ):  # need to handle parameters, ensure unicode
        return s3_retrieve( *parameters, raw_path=True ).decode( "utf8" ), \
               parameters[0]

    params = [(f, ObjectId( f.split( "/", 1 )[0] )) for f in timings_files]
    try:
        data = pool.map( batch_retrieve, params )
    except Exception:
        raise
    finally:
        pool.close( )
        pool.terminate( )
    return data

def get_file_paths_for_studies(list_of_study_id_strings):
    # get users associated with studies
    study_users = { s:Users(study_id=ObjectId(s), field="_id") for s in
                    list_of_study_id_strings }

    all_user_timings = []
    for sid, users in study_users.items( ):  # construct prefixes
        all_user_timings.extend(
                [sid + "/" + u + "/" + "surveyTimings" for u in users] )
    # use a threadpool to efficiently get all those strings of s3 paths we
    # will need
    pool = ThreadPool( len( all_user_timings ) )
    try:
        files_lists = pool.map( s3_list_files, all_user_timings )
    except Exception:
        raise
    finally:
        pool.close( )
        pool.terminate( )

    files_list = []
    for l in files_lists: files_list.extend( l )
    # we need to purge the occasional pre-multistudy file, and ensure it is utf encoded.
    return [f.decode( "utf8" ) for f in files_list if f.count( '/' ) == 4]


def remove_files_that_are_after_the_data_loss(file_list):
    #the server is in utc time, this will be a utc datetime object
    datetime_of_data_loss = datetime(year=2016,month=4,day=8, hour=22)
    ret = []
    for f in file_list:
        unix_timestamp_int = int(f.split("/")[-1][:-4]) / 1000
        if datetime.utcfromtimestamp(unix_timestamp_int) < datetime_of_data_loss:
            ret.append(f)
    return ret


def do_everything(list_of_files):
    print "getting files"
    list_of_files = remove_files_that_are_after_the_data_loss( list_of_files )
    # info = do_run( files, old_surveys=old_surveys)
    data = do_actually_run(list_of_files, old_surveys=old_surveys)
    do_upload(data, data_type="survey_answers", forcibly_overwrite=False)

################################# Data Reconstruction ##################################

def construct_answers_csv(timings_csv_contents, full_s3_path, old_surveys=None,
                          ignore_unsubmitted=True):
    #setup vars
    survey_id_string = full_s3_path.split("/")[3]
    study_id_string = full_s3_path.split("/",1)[0]
    status = []
    questions_answered, submission_time = parse_timings_file( timings_csv_contents,
                                                              status=status )

    if submission_time is None and ignore_unsubmitted:
        status.append(bad_messages["has_no_submit"])
        return None, None, None, status
        # we only really want to create answers files that would have been written
        # to a surveyanswers files, by default no false submissions
    # output_filename = submission_time.strftime('%Y-%m-%d %H_%M_%S') + ".csv"

    rows = ['question id,question type,question text,question answer options,answer']
    for question in sort_and_reconstruct_questions(questions_answered,
                                                   survey_id_string,
                                                   old_surveys=old_surveys,
                                                   submit_time=submission_time,
                                                   status=status):
        rows.append(",".join([question['question_id'],  # construct row
                              question['question_type'],
                              question['question_text'],
                              question['question_answer_options'],
                              question['answer'] ] ) )
    if len(rows) == 1: #drop anything that consists of only the header
        status.append(bad_messages["only_header"])
        return None, None, None, status
    return study_id_string, submission_time, "\n".join(rows), status


def sort_and_reconstruct_questions(questions_answered_dict, survey_id_string,
                                   old_surveys=None, submit_time=None, status=None):
    question_answers = []
    try: survey_questions = get_questions_from_survey(survey_id_string,
                                                      old_surveys=old_surveys,
                                                      submit_time=submit_time,
                                                      status=status)
    except UnableToFindSurveyError:
        status.append(other_messages["no_survey_1"])
        return question_answers
    #there is a corner case where a survey can have multiple source surveys:
    try:
        if not isinstance( survey_questions, tuple ):
            survey_questions = corral_question_ids( questions_answered_dict,
                                                    survey_questions, status=status )
        else: survey_questions = corral_question_ids( questions_answered_dict,
                             survey_questions[0], survey_questions[1], status=status)
    except UnableToReconcileError: return question_answers
    # now we reconstruct any unanswered questions using that survey.
    for survey_question in survey_questions:
        if survey_question['question_id'] in questions_answered_dict:
            question = questions_answered_dict[survey_question['question_id']]
            question['question_id'] = survey_question['question_id']
            question_answers.append(question)
        else: question_answers.append( reconstruct_unanswered_question(
                                       survey_question, status=status) )
    return question_answers


def corral_question_ids(questions_answered_dict, source_a, source_b=None, status=None):
    if len(questions_answered_dict) == 0:
        status.append(good_messages["no_answers"])

    timings_q_ids = questions_answered_dict.keys()
    q_ids_a = [q["question_id"] for q in source_a]
    missing_q_ids_a, extra_q_ids_a = compare_survey_questions_to_source(
                                                timings_q_ids, q_ids_a )
    if source_b is None:
        if not missing_q_ids_a: status.append(good_messages["everything_answered"])
        else: status.append( good_messages["all_missing_recovered"] )
        if not extra_q_ids_a: status.append( good_messages["no_extra_questions"])
        else:
            status.append(bad_messages["extra_questions"])
            status.append(extra_q_ids_a)
        return source_a

    status.append(other_messages["2_potential"])
    # else: we were handed 2 surveys and need to compare what we received.
    q_ids_b = [q["question_id"] for q in source_b]
    missing_q_ids_b, extra_q_ids_b = compare_survey_questions_to_source(
                                                    timings_q_ids, q_ids_b )

    #case: if everything is present in one but not the other, use that.
    #If missing questions in A but no missing questions in B, and there are no extras
    #  in B, return B
    if missing_q_ids_a and not missing_q_ids_b:
        if not extra_q_ids_b:
            status.append( good_messages["1_not_2_resolved"] )
            return source_b
        else: raise Exception( "A) extra questions." ) #yay never happens.
    #If missing questions in B but no missing questions in A, and there are no extras
    # in A, return A
    if not missing_q_ids_a and missing_q_ids_b:
        if not extra_q_ids_a:
            status.append( good_messages["2_not_1_resolved"] )
            return source_a
        else: raise Exception( "B) extra questions." ) #yay never happens.

    #case: someone added new questions, and then in that instance when the survey
    # had been updated the person answered only some of the questions.
    #if both are empty, check the extras, return the one that has zero extras
    if not missing_q_ids_a and not missing_q_ids_b:
        if not extra_q_ids_a and extra_q_ids_b:
            status.append( good_messages["extra_2_resolved"])
            return source_a
        if not extra_q_ids_b and extra_q_ids_a:
            status.append( good_messages["extra_1_resolved"])
            return source_b

    if not missing_q_ids_a and not extra_q_ids_a and not missing_q_ids_b and not extra_q_ids_b:
        status.append( good_messages["reordered_questions"] )
        if len(source_a) > len(source_b): return source_a
        else: return source_b

    if missing_q_ids_b and missing_q_ids_b:
        status.append(other_messages["both_missing"])
        if not extra_q_ids_a and extra_q_ids_b:
            status.append(good_messages["no_extra_1"])
            return source_a
        if not extra_q_ids_b and extra_q_ids_a:
            status.append(good_messages["no_extra_2"])
            return source_b
        if extra_q_ids_b and extra_q_ids_a:
            status.append(bad_messages["no_mappings"])
            raise UnableToReconcileError( )
        if not extra_q_ids_b and not extra_q_ids_a:
            status.append(bad_messages["not_enough_answers"])
            raise UnableToReconcileError()

    raise Exception("Unreachable code")


def compare_survey_questions_to_source(timing_questions, survey_questions, status=None):
    """ Provides the missing and extra questions from the provided answers with
        regards to the provided survey questions. """
    missing_q_ids = [q_id for q_id in survey_questions if q_id not in timing_questions]
    extra_q_ids = [q_id for q_id in timing_questions if q_id not in survey_questions]
    return missing_q_ids, extra_q_ids


def get_questions_from_survey(survey_id_string, old_surveys=None, submit_time=None,
                              status=None):
    survey_objid = ObjectId(survey_id_string)
    #TODO: can we propagate up two mismatched survey questions?
    if old_surveys:
        status.append(submit_time)
        try:
            return old_surveys.get_closest_survey_from_datetime(submit_time,
                                                                survey_id_string,
                                                                status=status)
        except (UnableToFindSurveyError, ItemTooLateException):
            #in both of these cases we want to pull from the most current survey,
            # in teh case of unabletofind this is a hail mary, in the case of itemtoolate
            # we want a time later than our survey backups provides.
            pass

    try:
        # return [question for question in recursive_convert_to_unicode(Survey(survey_objid)["content"])
        return [question for question in Survey( survey_objid )["content"]
                if question['question_type'] != 'info_text_box' ]
    except NonexistentObjectError:
        raise UnableToFindSurveyError


def reconstruct_unanswered_question(survey_question, status=None):
    """Does what it says"""
    question = {}
    question['question_id'] = survey_question['question_id']
    question['question_type'] = question_type_map[survey_question['question_type']]
    question['question_text'] = survey_question['question_text']
    question['question_answer_options'] = reconstruct_answer_options(survey_question)
    question['answer'] = "NO_ANSWER_SELECTED"
    return question


def reconstruct_answer_options(question, status=None):
    """ reconstructs the answer option portion of the questions to a hash-identical
     format to what would have been on the survey answers. """
    if 'max' in question and 'min' in question:
        return "min = " + question['min'] + "; max = " + question['max']
    elif 'text_field_type' in question:
        return "Text-field input type = " + question['text_field_type']
    elif 'answers' in question:
        answers = [ unicode(answer['text']) for answer in question['answers'] ]
        answer_string = "["
        for answer in answers: answer_string += answer + "; "
        return answer_string[:-2] + "]"
    return ""

################################## Data Parsing ######################################

def parse_timings_file( timings_csv_contents, status=None ):
    """ parses the timings file for question text and answers to questions.
    returns a tuple of questions and associated answers, and, submission time. """
    questions_answered = {}
    # first_displayed_time = None
    submit_time = None
    csv = csv_to_list(timings_csv_contents)
    for row in csv:
        if len(row) >= 5: #this row has question text and user answer
            question_id = row[1] #use the question id, thus overwriting updated answers.
            questions_answered[question_id] = {
                'question_type': row[2],
                'question_text': row[3],
                'question_answer_options': row[4],
                'answer': row[5] if len(row) > 5 else "" }
        #ended up not using the following
        # elif row[1] == "Survey first rendered and displayed to user":
        #     # potentially useful timestamp
        #     first_displayed_time = datetime.utcfromtimestamp(int(row[0])/1000.0)

        elif row[1] == "User hit submit":
            # used as file creation timestamp.
            submit_time = datetime.utcfromtimestamp(int(row[0])/1000.0)

    return questions_answered, submit_time


def csv_to_list(csv_string):
    """ turns a csv string into a list (drops the header, we don't use it)."""
    lines = [ line for line in csv_string.splitlines() ]
    return [row.split(",") for row in lines[1:]]



##################################################################################
# This is the UUID generation code, it simply runs through all the provided survey
# timings and extracts ALL question IDs and question texts.
# This code and data is almost totally useless.
def get_answers_text(timings_csv_contents):
    questions = { }
    csv = csv_to_list( timings_csv_contents )
    for row in csv:
        if len( row ) >= 5:
            question_id = row[1]
            questions[question_id] = { 'question_type':row[2],
                                       'question_text':row[3],
                                       'question_answer_options':row[4] }
    return questions

def handle_unicode_fixes(thing_a, thing_b):
    #these are the result of manual fixes to a database entry, we want the ascii
    # strings.
    correct_value = None
    try: recursive_convert_ascii( thing_a )
    except UnicodeEncodeError: correct_value = thing_b

    try: recursive_convert_ascii( thing_b )
    except UnicodeEncodeError:
        if correct_value is not None:
            raise Exception( "this error means there is not a unicode error" )
        correct_value = thing_a
    return correct_value

def get_uuids(file_paths_and_contents = None):
    if not file_paths_and_contents:
        files = get_all_timings_files( )
        file_paths_and_contents = [f for f in files if "55d3826297013e3a1c9b8c3e" in f]
    return do_get_uuids( file_paths_and_contents )

def do_get_uuids(file_paths_and_contents):
    uuids = {}
    for data, _ in file_paths_and_contents:
        new_uuids = get_answers_text( data )
        for uuid, content in new_uuids.items():
            if uuid in uuids and uuids[uuid] != content:
                handle_unicode_fixes(uuids[uuid], content)
        uuids.update(new_uuids)
    return uuids

def recursive_convert_ascii(data):
    #checks all nested elements for decode ascii compatibility, also returns an ascii
    # version of the data...
    if isinstance(data, basestring):
        return data.decode("ascii")
    elif isinstance(data, collections.Mapping):
        return dict(map(recursive_convert_ascii, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(recursive_convert_ascii, data))
    else:
        return data


############################## Data Acquisition ##################################


def unconditionally_setup_old_survey():
    old_surveys = OldSurveys( )
    old_surveys.__innit__( )
    return old_surveys


# Old surveys.  This is pulled in from a pickled load of all the survey db backups,
# the get_survey_bson_data_from_pickle function
class OldSurveys():
    surveys = {}
    keys = []

    def __innit__(self):
        self.surveys = OldSurveys.get_survey_bson_data_from_pickle()
        self.keys = sorted( self.surveys.keys() )
        self.keys_reverse = sorted( self.surveys.keys(), reverse=True )

    def _get_closest(self, some_item):
        if not self.keys: raise NoBackupSurveysException()

        previous = self.keys[0]
        for element in self.keys:
            if element > some_item: break
            previous = element

        if element == previous: #item provided comes before first item in list.
            # the best we can do is hope it is all in the earliest set of questions
            # that we have.
            return element, previous
        if element == self.keys[-1]: #item provided comes after last item in list.
            raise ItemTooLateException()
        return element, previous

    def _extaustive_reverse_lookup(self, day):
        #gets the closest day temporally before our target day.... if this ever happens
        #something is wrong with our source data....
        for d in self.keys_reverse:
            if d > day: continue #skip future days, those will never have it
            else: break #find closest day before, use that data
        return d #default is to retrn oldest data...

    @classmethod
    def _extract_questions(cls, survey):
        return [question for question in survey["content"] if question['question_type']
                                                                   != 'info_text_box' ]

    def get_closest_survey_from_datetime(self, dt, survey_id, status=None):
        """ Searches through the backups for the best survey we have on file to
        reconstruct everything from. """
        # provide a datetime directly, get closest day
        search_d = datetime.date(dt) + timedelta(days=1)

        #day_before is the surveys the closest day before,
        # day_after is the surveys from end of THAT day.
        day_before, day_after = self._get_closest(search_d)
        # except ItemTooLateException:
        #     print "GOOD NEWS: this survey is almost definitely fully recoverable."
        #     raise
        # # except ItemTooEarlyException:
        #     return None

        before_surveys = { str(s['_id']):s for s in self.surveys[day_before] }
        after_surveys = { str(s['_id']):s for s in self.surveys[day_after] }
        # print 'survey_id=', survey_id
        # print "before_surveys=", before_surveys.keys()
        # print "after_surveys=", after_surveys.keys()
        questions_before = None
        questions_after = None
        if survey_id in before_surveys:
            questions_before = old_surveys._extract_questions( before_surveys[survey_id] )

        if survey_id in after_surveys:
            questions_after = old_surveys._extract_questions( after_surveys[survey_id] )

        if questions_after is None and questions_before is None:
            #it is acceptable for an empty list to be returned for the questions texts,
            # we check explicitly for None
            closest_surveys =  { str(s['_id']):s for s in self.surveys[
                self._extaustive_reverse_lookup(search_d) ] }
            try: return old_surveys._extract_questions( closest_surveys[survey_id] )
            except KeyError:
                status.append(other_messages["no_survey_2"])
                raise UnableToFindSurveyError()

        if questions_after is None and questions_before is not None: return questions_before
        if questions_after is not None and questions_before is None: return questions_after
        if questions_after is not None and questions_before is not None:
            if questions_after == questions_before: return questions_before
            else: return questions_before, questions_after
        raise Exception("unreachable code? hunh?")

    @classmethod
    def get_survey_bson_data_from_pickle(cls):
        #does the read-in and transforms the date keys.
        os.chdir( "/home/ubuntu" )
        print "getting pickle...",
        with open( "bson_data.pickle" ) as f:
            data = cPickle.load( f )
            print "tickling pickle..."
            for key in data.keys( ):
                data[datetime.date(
                        datetime.strptime( key, "%Y-%m-%d_%H-%M" ) )] = data.pop(key)
        return data

# old_surveys = conditionally_setup_old_surveys()
# print isinstance(old_surveys, OldSurveys)
# if not isinstance(old_surveys, OldSurveys):
print "you are almost there..."
old_surveys = unconditionally_setup_old_survey()
# print isinstance(old_surveys, OldSurveys)
--
# x,y = debug(old_surveys=old_surveys)

# all_files, all_file_data = conditionally_setup_fo_realzies_stuff()

# x = fo_realzies(old_surveys=old_surveys)
# x = debug(old_surveys=old_surveys)