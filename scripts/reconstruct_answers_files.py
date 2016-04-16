import cPickle
import os
from multiprocessing.pool import ThreadPool

import collections
from bson.objectid import ObjectId
from datetime import datetime

from mongolia.errors import NonexistentObjectError

from db.study_models import Studies, Survey
from db.user_models import Users
from libs.s3 import s3_list_files, s3_retrieve

# what to do when there is no submit button
#    probably ignore them.
# check for the uuid in the dictionary

########################################################################################
# Administrative functions

def debug(old_surveys=None):
    debug_files = [f for f in get_all_timings_files() if "55d3826297013e3a1c9b8c3e" in f]
    data = get_data_for_raw_file_paths( debug_files )
    uuids = get_uuids(data)
    stuff = do_run( data, old_surveys=old_surveys ) #tuples of (file path, contents)
    return uuids, stuff

def fo_realzies(old_surveys=None):
    data = get_data_for_raw_file_paths( get_all_timings_files() )
    uuids = get_uuids( data )
    stuff = do_run( data, old_surveys=old_surveys )
    return uuids, stuff

def do_run(file_paths_and_contents, old_surveys=None):
    ret = {}
    for data, fp in file_paths_and_contents:
        print fp
        study, timecode, csv = construct_answers_csv( data, fp, old_surveys=old_surveys)
        if timecode and csv:
            ret[study, timecode] = csv
    return ret


########################################################################################
# business logic

def construct_answers_csv(timings_csv_contents, full_s3_path, old_surveys=None):
    survey_id_string = full_s3_path.split("/")[3]
    study = full_s3_path.split("/",1)[0]
    # file_creation_time = full_s3_path.rsplit("/", 1)[1][:-4]
    questions_answered, submit_time, first_displayed_time = \
        read_questions_and_submission_time(timings_csv_contents)

    if first_displayed_time is None:
        print "does not have first displayed time"
        pass

    if submit_time is None:
        print "does not have submit button..."
        return None, None, None #only want to create data that would have been written
        # to a
        #  surveyanswers files, no false submissions
    # output_filename = submit_time.strftime('%Y-%m-%d %H_%M_%S') + ".csv"

    rows = ['question id,question type,question text,question answer options,answer']
    for question in sort_and_reconstruct_questions(questions_answered,
                                                   survey_id_string,
                                                   old_surveys=old_surveys,
                                                   submit_time=submit_time):
        rows.append(",".join([question['question_id'],  # construct row
                              question['question_type'],
                              question['question_text'],
                              question['question_answer_options'],
                              question['answer'] ] ) )
    if len(rows) == 1: #drop anything that consists of only the header
        return None, None, None
    return study, submit_time, "\n".join(rows) # construct csv


def read_questions_and_submission_time(timings_csv_contents):
    #parses the timings file for questions and answers to questions
    # (calls only csv_to_list())
    questions_answered = {}
    first_displayed_time = None
    submit_time = None
    csv = csv_to_list(timings_csv_contents)
    for row in csv:
        if len(row) >= 5:
            question_id = row[1]
            questions_answered[question_id] = {
                'question_type': row[2],
                'question_text': row[3],
                'question_answer_options': row[4],
                'answer': row[5] if len(row) > 5 else "" }

        elif row[1] == "Survey first rendered and displayed to user":
            first_displayed_time = datetime.utcfromtimestamp(int(row[0])/1000.0)

        elif row[1] == "User hit submit":
            submit_time = datetime.utcfromtimestamp(int(row[0])/1000.0)

    return questions_answered, submit_time, first_displayed_time


def sort_and_reconstruct_questions(questions_answered_dict, survey_id_string,
                                   old_surveys=None, submit_time=None):
    question_answers = []
    survey_questions = get_questions_from_survey( survey_id_string,
                                               old_surveys=old_surveys,
                                               submit_time=submit_time)

    current_survey_question_ids = [content["question_id"] for content in survey_questions]
    missing_question_ids = []
    for q_id in questions_answered_dict.keys():
        if q_id not in current_survey_question_ids:
            missing_question_ids.append(q_id)
    if missing_question_ids: print missing_question_ids

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

    ===
    #TODO:we are never finding the old surveys (ever).  fix that
    ===
    if old_surveys:
        print submit_time
        old_s = old_surveys.get_closest_survey_from_datetime(submit_time)
        try: return [question for question in old_s[ survey_id_string ]["content"]
                if question['question_type'] != 'info_text_box' ]
        except KeyError:
            print "could not find %s in old surveys" % survey_id_string
        except TypeError:
            print "could not find old survey for %s" % submit_time
    try:
        # return [question for question in recursive_convert_to_unicode(Survey(survey_objid)["content"])
        return [question for question in Survey( survey_objid )["content"]
                if question['question_type'] != 'info_text_box' ]
    except NonexistentObjectError:
        return []


def reconstruct_unanswered_question(survey_question):
    question = {}
    question['question_id'] = survey_question['question_id']
    question['question_type'] = reconstruct_question_type(survey_question['question_type'])
    question['question_text'] = survey_question['question_text']
    question['question_answer_options'] = reconstruct_answer_options(survey_question)
    question['answer'] = "NO_ANSWER_SELECTED"
    return question

def reconstruct_question_type(question_type):
    if question_type == 'slider': return "Slider Question"
    elif question_type == 'radio_button': return "Radio Button Question"
    elif question_type == 'checkbox': return "Checkbox Question"
    elif question_type == 'free_response': return "Open Response Question"

def reconstruct_answer_options(question):
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

def get_data_for_raw_file_paths(all_timings_files):
    pool = ThreadPool(50)
    def batch_retrieve(parameters):
        return s3_retrieve(*parameters, raw_path=True).decode("utf8"), parameters[0]
    params = [(f, ObjectId( f.split( "/", 1)[0] )) for f in all_timings_files ]
    try: data = pool.map(batch_retrieve, params)
    except Exception: raise
    finally:
        pool.close( )
        pool.terminate( )
    return data

def csv_to_list(csv_string):
    """ turns a csv string into a list (drops the header, we don't use it)."""
    lines = [ line for line in csv_string.splitlines() ]
    return [row.split(",") for row in lines[1:]]



def recursive_convert_ascii(data):
    if isinstance(data, basestring):
        return data.decode("ascii")
    elif isinstance(data, collections.Mapping):
        return dict(map(recursive_convert_ascii, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(recursive_convert_ascii, data))
    else:
        return data


# def recursive_check_unicode( data, l=[] ):
#     if isinstance( data, basestring ):
#         l.append(u'\u201c' in data)
#     elif isinstance( data, collections.Mapping ):
#         return dict( map( recursive_check_unicode, (data.iteritems( ), l) ) )
#     elif isinstance( data, collections.Iterable ):
#         return type( data )( map( recursive_check_unicode, (data, l ) ) )
#     return data




##################################################################################
# This is the UUID generation code, it simply runs through all the provided survey
# timings and extracts ALL question IDs and question texts.
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
    try:
        recursive_convert_ascii( thing_a )
    except UnicodeEncodeError:
        correct_value = thing_b

    try:
        recursive_convert_ascii( thing_b )
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

##################################################################################


##################################################################################
# Old surveys.  This is pulled in from a pickled load of all the survey db backups,
# the get_survey_bson_data_from_pickle function
class OldSurveys():

    surveys = {}
    def __innit__(self):
        self.surveys = old_surveys.get_survey_bson_data_from_pickle()

    def get_closest_survey_from_timestamp(self, tmstmp):
        #provide a timestamp for the datetime
        return self.get_closest_survey_from_datetime[datetime.date(datetime.utcfromtimestamp(tmstmp))]

    def get_closest_survey_from_datetime(self, dt):
        # provide a datetime directly, get closest day
        keys = sorted(self.surveys.keys())
        search_d = datetime.date(dt)
        try:
            index = keys.index(search_d)
        except ValueError:
            return None
        return { s['_id']:s for s in self.surveys[keys[index]] }

    @classmethod
    def get_survey_bson_data_from_pickle(cls):
        #does the read-in and transforms the date keys.
        os.chdir( "/home/ubuntu" )
        with open( "bson_data.pickle" ) as f:
            print "getting pickle...",
            data = cPickle.load( f )
            print "settig up..."
            for key in data.keys( ):
                data[datetime.date(
                        datetime.strptime( key, "%Y-%m-%d_%H-%M" ) )] = data.pop(key)
        return data

old_surveys = OldSurveys()
old_surveys.__innit__()