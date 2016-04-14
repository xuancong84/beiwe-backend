import csv
from multiprocessing.pool import ThreadPool

from bson.objectid import ObjectId
from datetime import datetime

from db.study_models import Studies
from db.user_models import Users
from libs.s3 import s3_list_files

INPUT_FILEPATH = "/Users/admin/Desktop/working/timings.csv"
OUTPUT_DIRECTORY = "/Users/admin/Desktop/working/recreated/"
survey = {u'_id': ObjectId('570ff1ea1206f75fc2bbfdd6'),
 u'content': [{u'question_id': u'85cbb327-350b-46f6-a80f-b549e3785ee1',
   u'question_text': u'This is a text box.  Non-randomized survey.',
   u'question_type': u'info_text_box'},
  {u'max': u'7',
   u'min': u'1',
   u'question_id': u'107d67f2-118d-46d6-eabb-c2caf43a8527',
   u'question_text': u'Here is a slider question from 1 to 7.',
   u'question_type': u'slider'},
  {u'answers': [{u'text': u'Curly'}, {u'text': u'Larry'}, {u'text': u'Moe'}],
   u'question_id': u'032b5846-f79b-4606-e428-aa53f57609b4',
   u'question_text': u'Radio button with three options',
   u'question_type': u'radio_button'},
  {u'answers': [{u'text': u'Curly'},
    {u'text': u'Larry'},
    {u'text': u'Moe'},
    {u'text': u'Shemp'}],
   u'question_id': u'ac40dbe3-275e-4539-dfff-b21255603f12',
   u'question_text': u'Checkbox with four options',
   u'question_type': u'checkbox'},
  {u'question_id': u'32e2fac4-f892-4d9c-9bfe-e98fbd9e0bfc',
   u'question_text': u'Free response with a numeric answer',
   u'question_type': u'free_response',
   u'text_field_type': u'NUMERIC'},
  {u'question_id': u'2991c82c-3fab-426c-d12a-ae97e825782d',
   u'question_text': u'Free response with a single-line text answer',
   u'question_type': u'free_response',
   u'text_field_type': u'SINGLE_LINE_TEXT'},
  {u'question_id': u'16e1b47f-a86c-4b33-894a-6dec606c223d',
   u'question_text': u'Free response with a multi-line text answer',
   u'question_type': u'free_response',
   u'text_field_type': u'MULTI_LINE_TEXT'},
  {u'question_id': u'47a00a1d-99d6-4cb6-8599-f5d98bdf15f9',
   u'question_text': u'And an info text box at the end of the survey, just for good luck.',
   u'question_type': u'info_text_box'}],
 u'settings': {u'number_of_random_questions': None,
  u'randomize': False,
  u'randomize_with_memory': False,
  u'trigger_on_first_download': True},
 u'survey_type': u'tracking_survey',
 u'timings': [[], [63000], [63000], [63000], [63000], [63000], [63000]]}

def read_questions_and_submit_time(filepath):
    questions = {}
    submit_time = None
    with open(filepath, 'rb') as f:
        reader = csv.reader(f, delimiter=',')
        for i, row in enumerate(reader):
            if i > 0:
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
                        'answer': answer}
                elif row[1] == "User hit submit":
                    submit_time = datetime.utcfromtimestamp(int(row[0])/1000.0)
    return questions, submit_time

def print_answers_csv():
    questions, submit_time = read_questions_and_submit_time(INPUT_FILEPATH)
    output_filepath = OUTPUT_DIRECTORY + submit_time.strftime('%Y-%m-%d %H_%M_%S') + ".csv"
    with open(output_filepath, 'wb') as f:
        writer = csv.writer(f, delimiter=',', lineterminator='\n')
        writer.writerow(['question id', 'question type', 'question text',
                         'question answer options', 'answer'])
        for question in get_all_questions(questions):
            writer.writerow([question['question_id'],
                             question['question_type'],
                             question['question_text'],
                             question['question_answer_options'],
                             question['answer']])

def get_all_questions(questions):
    question_answers = []
    for survey_question in get_questions_from_survey():
        if survey_question['question_id'] in questions:
            question = questions[survey_question['question_id']]
            question['question_id'] = survey_question['question_id']
            question_answers.append(question)
        else:
            question_answers.append(reconstruct_question(survey_question))
    return question_answers

def reconstruct_question(survey_question):
    question = {}
    question['question_id'] = survey_question['question_id']
    question['question_type'] = reconstruct_question_type(survey_question['question_type'])
    question['question_text'] = survey_question['question_text']
    question['question_answer_options'] = reconstruct_answer_options(survey_question)
    question['answer'] = "NO_ANSWER_SELECTED"
    return question

def reconstruct_question_type(question_type):
    if question_type == 'slider':
        return "Slider Question"
    elif question_type == 'radio_button':
        return "Radio Button Question"
    elif question_type == 'checkbox':
        return "Checkbox Question"
    elif question_type == 'free_response':
        return "Open Response Question"

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

def get_questions_from_survey():
    return [question for question in survey['content']
            if question['question_type'] != 'info_text_box']



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

