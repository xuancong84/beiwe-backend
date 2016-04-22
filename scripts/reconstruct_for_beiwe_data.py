import collections
from datetime import datetime

#FIXME: I don't think the below is very useful, logic was generally too complex to pull
# out without a major refactor.  Consider writing from older versions of the code,
# possibly production branch commit 75f630b4c30a60aacd5afcbf0c4ce7294719d835

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

#TODO: these dicts should get reduced, possibly removed totally...
good_messages = {
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


############################### Administrative functions ###############################

def get_resolvable_survey_timings(from_do_run):
    #checks for bad status messages... probably not relevant or used anymore
    ret = {}
    for k, v in from_do_run.items():
        for m in bad_messages.values():
            if m in v: break
        if m not in v:
            ret[k] = v
    return ret



################################# Data Reconstruction ##################################

#TODO: got rid of providing the s3 file path, purge things related to that.

def construct_answers_csv(timings_csv_contents, old_surveys=None):

    #setup vars
    # survey_id_string = full_s3_path.split("/")[3]
    status = []
    questions_answered, submission_time = parse_timings_file( timings_csv_contents,
                                                              status=status )

    if submission_time is None
        status.append(bad_messages["has_no_submit"])
        return None, None, None, status
        # we only really want to create answers files that would have been written
        # to a surveyanswers files, by default no false submissions
    # output_filename = submission_time.strftime('%Y-%m-%d %H_%M_%S') + ".csv"

    rows = ['question id,question type,question text,question answer options,answer']
    for question in questions_answered:
        #FIXME: This almost definitely is iterating over a dict instead of a list...
        rows.append(",".join([question['question_id'],  # construct row
                              question['question_type'],
                              question['question_text'],
                              question['question_answer_options'],
                              question['answer'] ] ) )

    if len(rows) == 1: #we do not care about anything that consists of only a header
        status.append(bad_messages["only_header"])
        return None, None, None, status

    return submission_time, "\n".join(rows), status


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
        #TODO: this data point is necessary for separating survey attempts in the
        # hourly chunked files.
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
# This is the question UUID mapping code, it simply runs through all the provided survey
# timings and extracts ALL question IDs and question texts. (code is essentially an
# abridged version of the code above)

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



#TODO: I can't tell if this is used if we take data from timings chunks
def reconstruct_unanswered_question(survey_question, status=None):
    """Does what it says"""
    question = {}
    question['question_id'] = survey_question['question_id']
    question['question_type'] = question_type_map[survey_question['question_type']]
    question['question_text'] = survey_question['question_text']
    question['question_answer_options'] = reconstruct_answer_options(survey_question)
    question['answer'] = "NO_ANSWER_SELECTED"
    return question
