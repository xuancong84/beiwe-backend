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

def grab_weekly_files(all_files):

    # Added to avoid index out of bounds
    if (len(all_files) <= 7):
        return all_files
    else:
        return all_files[len(all_files) - 7:]

def get_weekly_results(username="ABCDEF12", question_id='A113'):
    answer_list = []
    weekly_files = grab_weekly_files(list_s3_files(username + '/surveyAnswers/'))

    # Convert each item to a readable data list
    for item in weekly_files:
        data = csv_to_dict(item)

        # If the dictionary is empty, append a string
        if (len(data) == 0):
            answer_list.append('None')

        # Grab the right question, and its right answer
        else:
            for question in data:
                if (question['question id'] == question_id):
                    answer_list.append(question['answer'])
                else:
                    continue
    result_list = []

    # If the answer is a string, it's not graphable, so place is as None
    # Otherwise, place it as a floating point number
    for answer in answer_list:
        try:
            temp = float(answer)
            result_list.append(temp)
        except ValueError:
            temp = None
            result_list.append(temp)
    return result_list