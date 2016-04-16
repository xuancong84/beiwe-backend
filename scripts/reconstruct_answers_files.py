cpaste

import cPickle, os, collections
from bson.objectid import ObjectId
from datetime import datetime, timedelta
from mongolia.errors import NonexistentObjectError

from multiprocessing.pool import ThreadPool
from db.study_models import Studies, Survey
from db.user_models import Users
from libs.s3 import s3_list_files, s3_retrieve


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

def conditionally_setup_debug_stuff():
    global_vars = globals( )
    if 'debug_files' not in global_vars:
        debug_files = [f for f in get_all_timings_files() if "55d3826297013e3a1c9b8c3e" in f]
    else: debug_files = global_vars['debug_files']
    if "debug_file_data" not in global_vars:
        debug_file_data = get_data_for_raw_file_paths( debug_files )
    else: debug_file_data = global_vars['debug_file_data ']
    return debug_files, debug_file_data


############################### Administrative functions ###############################

def debug(old_surveys=None, ignore_unsubmitted=True):
    debug_files, debug_data_files = conditionally_setup_debug_stuff()
    uuids = get_uuids(debug_data_files)
    stuff = do_run( debug_data_files, old_surveys=old_surveys, ignore_unsubmitted=True )
    return uuids, stuff

def fo_realzies( old_surveys=None, ignore_unsubmitted=True ):
    data = get_data_for_raw_file_paths( get_all_timings_files() )
    uuids = get_uuids( data )
    stuff = do_run( data, old_surveys=old_surveys, ignore_unsubmitted=True )
    return uuids, stuff

def do_run(file_paths_and_contents, old_surveys=None, ignore_unsubmitted=True):
    ret = {}
    for data, fp in file_paths_and_contents:
        print fp
        study, timecode, csv = construct_answers_csv( data, fp,
                                                      old_surveys=old_surveys,
                                                      ignore_unsubmitted=ignore_unsubmitted)
        if study and timecode and csv: #drop any return where a value is None
            ret[study, timecode] = csv
    return ret


################################# Data Reconstruction ##################################

def construct_answers_csv(timings_csv_contents, full_s3_path, old_surveys=None,
                          ignore_unsubmitted=True):
    #setup vars
    survey_id_string = full_s3_path.split("/")[3]
    study_id_string = full_s3_path.split("/",1)[0]
    questions_answered, submission_time = parse_timings_file( timings_csv_contents )

    # if first_displayed_time is None: print "does not have first displayed time"

    if submission_time is None and ignore_unsubmitted:
        return None, None, None
        # we only really want to create answers files that would have been written
        # to a surveyanswers files, by default no false submissions
    # output_filename = submission_time.strftime('%Y-%m-%d %H_%M_%S') + ".csv"

    rows = ['question id,question type,question text,question answer options,answer']
    for question in sort_and_reconstruct_questions(questions_answered,
                                                   survey_id_string,
                                                   old_surveys=old_surveys,
                                                   submit_time=submission_time):
        rows.append(",".join([question['question_id'],  # construct row
                              question['question_type'],
                              question['question_text'],
                              question['question_answer_options'],
                              question['answer'] ] ) )
    if len(rows) == 1: #drop anything that consists of only the header
        return None, None, None
    return study_id_string, submission_time, "\n".join(rows) # construct csv


def sort_and_reconstruct_questions(questions_answered_dict, survey_id_string,
                                   old_surveys=None, submit_time=None):
    question_answers = []

    try:
        survey_questions = get_questions_from_survey( survey_id_string,
                                                      old_surveys=old_surveys,
                                                      submit_time=submit_time )

        current_survey_question_ids = [content["question_id"] for content in survey_questions]
        missing_question_ids = []
        for q_id in questions_answered_dict.keys():
            if q_id not in current_survey_question_ids:
                missing_question_ids.append(q_id)
        if missing_question_ids: print missing_question_ids
    except:
        print "unable to get any missing questions."
        return question_answers

    for survey_question in survey_questions:
        if survey_question['question_id'] in questions_answered_dict:
            question = questions_answered_dict[survey_question['question_id']]
            question['question_id'] = survey_question['question_id']
            question_answers.append(question)
        else:
            question_answers.append( reconstruct_unanswered_question( survey_question) )
    return question_answers


def get_questions_from_survey(survey_id_string, old_surveys=None, submit_time=None):
    survey_objid = ObjectId(survey_id_string)
    #TODO: can we propagate up two mismatched survey questions?
    if old_surveys:
        print submit_time
        try:
            return old_surveys.get_closest_survey_from_datetime(submit_time, survey_id_string)
        except UnableToFindSurveyError:
            pass

    try:
        # return [question for question in recursive_convert_to_unicode(Survey(survey_objid)["content"])
        return [question for question in Survey( survey_objid )["content"]
                if question['question_type'] != 'info_text_box' ]
    except NonexistentObjectError:
        raise UnableToFindSurveyError


def reconstruct_unanswered_question(survey_question):
    question = {}
    question['question_id'] = survey_question['question_id']
    question['question_type'] = question_type_map[survey_question['question_type']]
    question['question_text'] = survey_question['question_text']
    question['question_answer_options'] = reconstruct_answer_options(survey_question)
    question['answer'] = "NO_ANSWER_SELECTED"
    return question

def reconstruct_answer_options(question):
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

def parse_timings_file( timings_csv_contents ):
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


##################################################################################


############################## Data Acquisition ##################################

def get_all_timings_files():
    #get users associated with studies
    study_users = { str(s._id): Users(study_id=s._id, field='_id') for s in Studies() }
    all_user_timings = []
    for sid, users in study_users.items(): #construct prefixes
        all_user_timings.extend([sid + "/" + u + "/" + "surveyTimings" for u in users])
    #use a threadpool to efficiently get all those strings of s3 paths we will need
    pool = ThreadPool( len( all_user_timings ) )
    try:
        files_lists = pool.map( s3_list_files, all_user_timings )
    except Exception: raise
    finally:
        pool.close( )
        pool.terminate( )

    files_list = []
    for l in files_lists: files_list.extend(l)
    #we need to purge the occasional pre-multistudy file, and ensure it is utf encoded.
    return [ f.decode("utf8") for f in files_list if f.count('/') == 4 ]

def get_data_for_raw_file_paths(timings_files):
    #Pulls in (timings) files from s3
    pool = ThreadPool(50)
    def batch_retrieve(parameters): #need to handle parameters, ensure unicode
        return s3_retrieve(*parameters, raw_path=True).decode("utf8"), parameters[0]
    params = [(f, ObjectId( f.split( "/", 1)[0] )) for f in timings_files ]
    try: data = pool.map(batch_retrieve, params)
    except Exception: raise
    finally:
        pool.close( )
        pool.terminate( )
    return data


def conditionally_setup_old_surveys(global_vars=vars()):
    """ run this function in the global scope. """
    if "old_surveys" not in global_vars:
        return unconditionally_setup_old_survey()
    return global_vars["old_surveys"]

def unconditionally_setup_old_survey():
    old_surveys = OldSurveys( )
    old_surveys.__innit__( )
    return old_surveys

class ItemTooEarlyException( Exception ): pass
class ItemTooLateException( Exception ): pass
class NoBackupSurveysException( Exception ): pass
class UnableToFindSurveyError( Exception ): pass
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

        # try: # try direct match, if it works, awesome, we have our item
        #     return some_list.index( some_item ),
        # except KeyError:
        #     pass  # on failure we iterate for best (earliest) match

        previous = self.keys[0]
        for element in self.keys:
            if element > some_item: break
            previous = element

        if element == previous: #item provided comes before first item in list.
            # raise ItemTooEarlyException()
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

    def get_closest_survey_from_datetime(self, dt, survey_id):
        """ Searches through the backups for the best survey we have on file to
        reconstruct everything from. """
        # provide a datetime directly, get closest day
        search_d = datetime.date(dt) + timedelta(days=1)

        #day_before is the surveys the closest day before,
        # day_after is the surveys from end of THAT day.
        try:day_before, day_after = self._get_closest(search_d)
        except ItemTooLateException:
            print "GOOD NEWS: this survey is almost definitely fully recoverable."
            raise
        # except ItemTooEarlyException:
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
            print "probably about to fail..."
            closest_surveys =  { str(s['_id']):s for s in self.surveys[
                self._extaustive_reverse_lookup(search_d) ] }
            try: return old_surveys._extract_questions( closest_surveys[survey_id] )
            except KeyError: raise UnableToFindSurveyError()

        if questions_after is None and questions_before is not None: return questions_before
        if questions_after is not None and questions_before is None: return questions_after
        if questions_after is not None and questions_before is not None:
            if questions_after == questions_before: return questions_before
            else: raise Exception("Well. Shit.")

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


