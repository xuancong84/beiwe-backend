from libs.s3 import s3_list_files, s3_retrieve
from libs.encryption import get_client_private_key, decrypt_rsa_lines

################################################################################
########################### CSV HANDLERS #######################################
################################################################################

def s3_csv_to_dict(s3_file_path):
    return read_csv_string( s3_retrieve( s3_file_path ) )


def read_csv_string(csv_string):
    """ Converts a string formatted as a csv into a dictionary with the format
        {Column Name: [list of data points] }. Data are in their original order,
        any empty entries are dropped.  """
    #grab a list of every line in the file, strips off trailing whitespace.
    lines = [ line for line in csv_string.splitlines() ]

    header_list = lines[0].split(',')
    list_of_entries = []

    for line in lines[1:]:
        data = line.split(',')
        #creates a dict of {column name: data point, ...}
        list_of_entries.append( { header_list[i]: entry for i, entry in enumerate(data) if entry != ''} )
    return list_of_entries


################################################################################
########################### GRAPH DATA HANDLERS ################################
################################################################################

# This is a method to get the last seven names saved in a folder
def grab_weekly_file_names(all_files):
    # Returns a sorted list of all files
    if (len(all_files) <= 7):
        return sorted(all_files)
    else:
        return sorted(all_files[len(all_files) - 7:])


def get_most_recent_id(file_path):
    all_files = s3_list_files(file_path)
    id_set = set()
    for filename in all_files:
        # This assumes that the 3rd entry is always an integer
        organizing_list = filename.split('/')
        survey_id = int(organizing_list[2])
        id_set.add(survey_id)
    result_list = sorted(id_set)
    return result_list[len(result_list) - 1]


def get_weekly_results(username="sur", methods=['GET', 'POST']):
    file_path = username + '/surveyAnswers/'
    survey_id = get_most_recent_id(file_path)
    weekly_files = grab_weekly_file_names(s3_list_files(file_path + str(survey_id) + '/'))
    # Convert each csv_file to a readable data list
    weekly_surveys = [s3_csv_to_dict(file_name) for file_name in weekly_files]

    # Adds all question ids to a set, then turns that set into an ordered list
    # Also, creates the final list of answers to be sent to the graph
    ordered_question_ids = set()
    all_answers = {}
    for question in weekly_surveys[0]:
        ordered_question_ids.add(question['question id'])
        all_answers[question['question id']] = { question['question text'] : []}
    list_ordered_question_ids = sorted(ordered_question_ids)

    # Adds all answers to it in a formatted way
    for survey in weekly_surveys:
        for question in survey:
            current_id = question['question id']
            answer = question['answer']
            question_text = question['question text']
            try:
                all_answers[current_id][question_text].append(int(answer))
            except ValueError:
                all_answers[current_id][question_text].append(None)

    tuple_values = sorted(all_answers.values())
    result = []
    for value in tuple_values:
        for question_num, corresponding_answers in value.items():
            result.append([question_num, corresponding_answers])
    return result