from multiprocessing.pool import ThreadPool

import collections
from bson.objectid import ObjectId
from datetime import datetime

from mongolia.errors import NonexistentObjectError

from db.study_models import Studies, Survey
from db.user_models import Users
from libs.s3 import s3_list_files, s3_retrieve


from libs.security import chunk_hash

FULL_S3_PATH = "thing?"

def print_answers_csv(timings_csv_contents, full_s3_path):
    FULL_S3_PATH = full_s3_path
    survey_id_string = full_s3_path.split("/")[3]
    file_creation_time = full_s3_path.rsplit("/", 1)[1][:-4]
    timings_csv_contents = timings_csv_contents.decode("utf8")
    questions, submit_time = read_questions_and_submission_time(timings_csv_contents)

    if submit_time is None:
        print full_s3_path + " does not have submit button"
        return
    output_filename = submit_time.strftime('%Y-%m-%d %H_%M_%S') + ".csv"

    rows = [",".join(['question id', 'question type', 'question text',
                     'question answer options', 'answer'])]

    for question in sort_and_reconstruct_questions(questions, survey_id_string):
        rows.append(",".join([question['question_id'],
                              question['question_type'],
                              question['question_text'],
                              question['question_answer_options'],
                              question['answer'] ] ) )
    csv = "\n".join(rows)
    return


def read_questions_and_submission_time(timings_csv_contents):
    questions = {}
    submit_time = None
    #might need to split contents on new lines
    # x = BytesIO()
    # x.write(timings_csv_contents)
    # x.seek(0)
    # reader = csv.reader(timings_csv_contents.splitlines(), delimiter=',')
    header, csv = csv_to_list(timings_csv_contents)
    for row in csv:
        if len(row) >= 5:
            question_id = row[1]
            question_type = row[2]
            question_text = row[3]
            question_answer_options = row[4]
            answer = ''
            if len(row) > 5: answer = row[5]
            questions[question_id] = {
                'question_type': question_type,
                'question_text': question_text,
                'question_answer_options': question_answer_options,
                'answer': answer }
        elif row[1] == "User hit submit":
            submit_time = datetime.utcfromtimestamp(int(row[0])/1000.0)
    return questions, submit_time


def sort_and_reconstruct_questions(questions, survey_id_string):
    question_answers = []
    sq = get_questions_from_survey( survey_id_string )

    current_survey_question_ids = [content["question_id"] for content in sq]
    for q_id in questions.keys():
        if q_id not in current_survey_question_ids:
            print "missing question text in %s" % FULL_S3_PATH
        # else:
        #     print "%s found in survey questions" % q_id

    for survey_question in get_questions_from_survey(survey_id_string):
        if survey_question['question_id'] in questions:
            question = questions[survey_question['question_id']]
            question['question_id'] = survey_question['question_id']
            question_answers.append(question)
        else:
            question_answers.append(reconstruct_unanswered_question(survey_question))
    return question_answers


# def sort_and_reconstruct_questions(questions, survey_id_string):
#     question_answers = []
#     for survey_question in get_questions_from_survey(survey_id_string):
#         if survey_question['question_id'] in questions:
#             question = questions[survey_question['question_id']]
#             question['question_id'] = survey_question['question_id']
#             question_answers.append(question)
#         else:
#             question_answers.append(reconstruct_unanswered_question(survey_question))
#     return question_answers


#getting the answers is easy.
def get_questions_from_survey(survey_id_string):
    survey_objid = ObjectId(survey_id_string)
    try:
        return [question for question in Survey(survey_objid)["content"]
                if question['question_type'] != 'info_text_box']
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
        answers = [str(answer['text']) for answer in question['answers']]
        answer_string = "["
        for answer in answers:
            answer_string += answer + "; "
        return answer_string[:-2] + "]"
    return ""


def get_all_timings_files():
    #get users associated with studies
    study_users = { str(s._id): Users(study_id=s._id, field='_id') for s in Studies() }
    all_user_timings = []
    for sid, users in study_users.items(): #construct prefixes
        all_user_timings.extend([sid + "/" + u + "/" + "surveyTimings" for u in users])
    #use a threadpool to efficiently get all those strings of s3 paths we will need
    pool = ThreadPool( len(all_user_timings) )
    files_lists = pool.map( s3_list_files, all_user_timings )
    pool.close( )
    pool.terminate( )

    files_list = []
    for l in files_lists: files_list.extend(l)
    #we need to purge the occasional pre-multistudy file
    return [ f for f in files_list if f.count('/') == 4 ]



def get_data_for_raw_file_paths(all_timings_files):
    pool = ThreadPool(50)
    def batch_retrieve(parameters):
        return s3_retrieve(*parameters, raw_path=True), parameters[0]
    params = [(f, ObjectId( f.split( "/", 1)[0] )) for f in all_timings_files ]
    try:
        data = pool.map(batch_retrieve, params)
    except Exception: raise
    finally:
        pool.close( )
        pool.terminate( )
    return data


def recursive_convert_to_unicode(data):
    if isinstance(data, basestring):
        return data.encode("utf8")
    elif isinstance(data, collections.Mapping):
        return dict(map(recursive_convert_to_unicode, data.iteritems()))
    elif isinstance(data, collections.Iterable):
        return type(data)(map(recursive_convert_to_unicode, data))
    else:
        return data




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
    return header + u"\n" + u"\n".join( [u",".join([x for x in row]) for row in rows_list ] )



files = get_all_timings_files()
debug_files = [f for f in files if "55d3826297013e3a1c9b8c3e" in f]
file_path_contents = get_data_for_raw_file_paths(debug_files) #tuples of (file path, contents)
for data, fp in file_path_contents:
    print fp
    print_answers_csv( data, fp )
