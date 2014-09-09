from utils.s3 import list_s3_files, s3_retrieve

# TODO: DEPRECATE!!
#
# def read_file(file_path):
#     """reads in a file, returns a string of the entire file."""
#     with open(file_path, 'r') as f:
#         return f.read()


def read_csv_other(csv_string):
    #grab a list of every line in the file, strips off trailing whitespace.
    #
    lines = [ line for line in csv_string.splitlines() ]

    header_list = lines[0].split(',')
    list_of_entries = []

    for line in lines[1:]:
        data = line.split(',')
        #creates a dict of {column name: data point, ...}
        list_of_entries.append( { header_list[i]: entry for i, entry in enumerate(data) if entry != ''} )
    return list_of_entries


# Dori's working code
def manipulate_csv(readed_file):
    modified_list = [line for line in readed_file.splitlines()]
    headers = modified_list[0].split(',')
    result = []
    for element in modified_list[1:]:
        listed_values = element.split(',')
        dictionary = {header : listed_values[header_index] for (header_index, header) in enumerate(headers)}
        result.append(dictionary)
    return result

def csv_to_dict(file_path):
    return read_csv_other( s3_retrieve( file_path ) )

def grab_weekly_file_names(all_files):

    # Added an if statement to avoid index out of bounds
    # Returns a sorted list of all files
    if (len(all_files) <= 7):
        return sorted(all_files)
    else:
        return sorted(all_files[len(all_files) - 7:])

def get_weekly_results(username="sur"):
    weekly_files = grab_weekly_file_names(list_s3_files(username + '/surveyAnswers42/'))
    # Convert each csv_file to a readable data list
    weekly_surveys = [csv_to_dict(file_name) for file_name in weekly_files]

    # Adds all question ids to a set, then turns that set into an ordered list
    # Also, creates the final list of answers to be sent to the graph
    ordered_question_ids = set()
    all_answers = []
    for question in weekly_surveys[0]:
        ordered_question_ids.add(question['question id'])
        all_answers.append([])
    list_ordered_question_ids = [question_id for question_id in ordered_question_ids]

    # Adds all answers to it in a formatted way
    for survey in weekly_surveys:
            for question in survey:
                current_id = question['question id']
                answer = question['answer']
                try:
                    all_answers[list_ordered_question_ids.index(current_id)].append(int(answer))
                except ValueError:
                    all_answers[list_ordered_question_ids.index(current_id)].append(None)
    return all_answers