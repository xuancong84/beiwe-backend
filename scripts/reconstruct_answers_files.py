import csv
from datetime import datetime

def get_questions_and_submit_time(filepath):
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
    input_filepath = "/Users/admin/Desktop/working/timings.csv"
    output_directory = "/Users/admin/Desktop/working/recreated/"
    questions, submit_time = get_questions_and_submit_time(input_filepath)
    output_filepath = output_directory + submit_time.strftime('%Y-%m-%d %H_%M_%S') + ".csv"
    with open(output_filepath, 'wb') as f:
        writer = csv.writer(f, delimiter=',', lineterminator='\n')
        writer.writerow(['question id', 'question type', 'question text',
                         'question answer options', 'answer'])
        for question_id in questions:
            question = questions[question_id]
            print question
            writer.writerow([question_id,
                             question['question_type'],
                             question['question_text'],
                             question['question_answer_options'],
                             question['answer']])
