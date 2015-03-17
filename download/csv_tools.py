import csv, datetime
from os import listdir


def create_csv_of_all_data_between(start_timestamp, end_timestamp):
    data = []
    for name in get_files_created_between(start_timestamp, end_timestamp):
        with open(name, 'r') as f:
            data.append(f.read())
    finaldata = []
    for x in data:
        for line in x.splitlines()[1:]:
            finaldata.append(line)
    with open('output.csv', 'w') as f:
        for line in finaldata:
            f.write(line)
            f.write('\n')


def get_files_created_between(start_timestamp, end_timestamp):
    relevant_file_list = []
    for name in listdir('.'):
        try:
            file_timestamp = int(name.split('_')[1].split('.')[0])
            if (file_timestamp > start_timestamp) and (file_timestamp < end_timestamp):
                relevant_file_list.append(name)
        except (IndexError, ValueError):
            print "error on filename ", name
    return relevant_file_list


def get_local_time_from_unix_timestamp_string(timestamp_string):
    timestamp = int(timestamp_string)
    if len(timestamp_string) == 13:
        timestamp = timestamp / 1000
    return datetime.datetime.fromtimestamp(
        int(timestamp)
    ).strftime('%m/%d/%Y %H:%M:%S')


def get_length_of_csv_file(filename):
    return sum([1 for _row in csv.reader(open(filename))])


def return_file(filename):
    lines = []
    for line in csv.reader(open(filename)):
        lines.append(line)
    return lines


def get_timestamps(filename):
    data = []
    lines = return_file(filename)[1:]
    for line in lines:
        data.append(int(line[0]))
    return data

def get_time_diffs(timestamps):
    time_diffs = []
    for i in range(len(timestamps))[1:]:
        time_diffs.append(timestamps[i] - timestamps[i-1])
    return time_diffs

def get_timeline(timestamps, resolution):
    time_diffs = []
    for i in range(len(timestamps))[1:]:
        time_diff = timestamps[i] - timestamps[i-1]
        if time_diff > resolution:
            human_time = get_local_time_from_unix_timestamp_string(str(timestamps[i-1]))
            time_diffs.append((human_time, time_diff / float(resolution)))
    return time_diffs
