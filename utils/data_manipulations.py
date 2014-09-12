from utils.s3 import list_s3_files, s3_retrieve


def csv_to_dict(s3_file_path):
    return read_csv_string( s3_retrieve( s3_file_path ) )


def read_csv_string(csv_string):
    #TODO: Dori, test for empty entry handling in graphing, we can change behavior of empty entries.
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


#TODO: Dori. add a user id parameter?
def grab_weekly_file_names(all_files):
    # Returns a sorted list of all files
    if (len(all_files) <= 7):
        return sorted(all_files)
    else:
        return sorted(all_files[-7:])


def get_most_recent_id(file_path):
    all_files = list_s3_files(file_path)
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
    weekly_files = grab_weekly_file_names(list_s3_files(file_path + str(survey_id) + '/'))
    # Convert each csv_file to a readable data list
    weekly_surveys = [csv_to_dict(file_name) for file_name in weekly_files]

    # Adds all question ids to a set, then turns that set into an ordered list
    # Also, creates the final list of answers to be sent to the graph
    ordered_question_ids = set()
    all_answers = []
    for question in weekly_surveys[0]:
        ordered_question_ids.add(question['question id'])
        all_answers.append([])
    list_ordered_question_ids = sorted(ordered_question_ids)

    # Adds all answers to it in a formatted way
    for survey in weekly_surveys:
            for question in survey:
                current_id = question['question id']
                answer = question['answer']

                # TODO: Dori. This will change. For now, the graph can't deal with string answers..
                try:
                    all_answers[list_ordered_question_ids.index(current_id)].append(int(answer))
                except ValueError:
                    all_answers[list_ordered_question_ids.index(current_id)].append(None)
    return all_answers