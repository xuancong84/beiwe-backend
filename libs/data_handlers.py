from data.constants import DAILY_SURVEY_NAME
from libs.s3 import s3_list_files, s3_retrieve
from libs.logging import log_error

################################################################################
########################### CSV HANDLERS #######################################
################################################################################

def s3_csv_to_dict(s3_file_path):
    return csv_to_dict( s3_retrieve( s3_file_path ) )

def csv_to_dict(csv_string):
    """ Converts a string formatted as a csv into a dictionary with the format
        {Column Name: [list of data points] }. Data are in their original order,
        any empty entries are dropped."""
    #grab a list of every line in the file, strips off trailing whitespace.
    lines = [ line for line in csv_string.splitlines() ]

    header_list = lines[0].split(',')
    list_of_entries = []

    for line in lines[1:]:
        data = line.split(',')
        #creates a dict of {column name: data point, ...}, strips empty strings
        list_of_entries.append( { header_list[i]: entry for i, entry in enumerate(data) if entry != ''} )
    return list_of_entries


################################################################################
############################### GRAPH DATA #####################################
################################################################################

def grab_file_names(file_path, survey_id, number_points):
    """ Takes a list, returns a list of the most recent 7 files."""
    all_files = s3_list_files(file_path + survey_id + '/')
    return sorted( all_files[ len(all_files) - number_points: ] )


def get_most_recent_id(user_file_path):
    """ Grabs the most recent survey id for a path of the form
        username_/surveyAnswers/survey_type/ """
    all_files = s3_list_files(user_file_path)
    id_set = set()
    for filename in all_files:
        # (based on file name spec)
        # assumes 3rd entry is always an integer, grab the survey_id.
        survey_id = int( filename.split('/')[3] )
        id_set.add( survey_id )
    result_list = sorted( id_set )
    # return the last entry, which is the most recent survey id.
    return result_list[ -1 ]



def compile_question_data(surveys):
    """ Grabs all question ids, grabs all answers. """
    ordered_question_ids = set()
    all_answers = {}
    for question in surveys[0]:
        ordered_question_ids.add( question['question id'] )
        all_answers[ question['question id'] ] = { question['question text'] : [] }
    return ordered_question_ids, all_answers



def get_survey_results( username="", survey_type=DAILY_SURVEY_NAME , number_points=7 ):
    """ Compiles 2 weeks (14 points) of data from s3 for a given patient into
        data points for displaying on the device.
        result is a list of lists, inner list[0] is the title/question text,
        inner list[1] is a list of y coordinates."""
    
    if not username:
        log_error (Exception("failed to provide username"),
                   "while compiling graph data.")
    
    # path pointing to the correct survey type
    file_path = username + '/surveyAnswers/' + survey_type + '/'
    survey_id = str( get_most_recent_id( file_path ) )
    weekly_files = grab_file_names( file_path, survey_id, number_points)
    
    # Convert each csv_file to a useful list of data
    surveys = [ s3_csv_to_dict(file_name) for file_name in weekly_files ]
    # grab the questions that answers correspond to
    ordered_question_ids, all_answers = compile_question_data(surveys)
    #welp, that variable is not used!

    # add responses that correspond to the given questions
    for survey in surveys:
        for question in survey:
            current_id = question['question id']
            answer = question['answer']
            question_text = question['question text']
            try:
                all_answers[current_id][question_text].append( int(answer) )
            except ValueError:
                all_answers[current_id][question_text].append(None)

    # turns the data into a list of lists that javascript can actually handle.
    tuple_values = sorted( all_answers.values() )
    result = []
    for value in tuple_values:
        for question_num, corresponding_answers in value.items():
            result.append( [question_num, corresponding_answers] )
    return result
