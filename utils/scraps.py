
def read_file(file_path):
    """reads in a file, returns a string of the entire file."""
    with open(file_path, 'r') as f:
        return f.read()


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
