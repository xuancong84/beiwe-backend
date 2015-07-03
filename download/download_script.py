import os
from os import chdir

try:
    from libs.s3 import s3_list_files as _s3_list, s3_retrieve as _s3_retrieve
    from urllib2 import urlopen as _urlopen
    from libs.encryption import decrypt_server as _decrypt
except ImportError as e:
    print "\n You need to solve this import error, I recommend using pip."
    print e.message, "\n\n\n"
    raise e

#TODO: Eli. the download script needs to be either rewritten to grab only relevant user ids,
# or it needs to not grab user ids at all. 

print "\n\n...\n"
try:
    _encrypted_user_list = _urlopen("https://beiwe.org/user_list").read()
    user_list = _decrypt(_encrypted_user_list).split(',')
    print "\na variable \"user_list\" has been created, it contains all user ids"
except Exception:
    print "\nunable to get user list.\n"
    exit()

print "\nyou are currently in", os.path.abspath(".")
print 'To change your current directory type chdir("/some/folderpath/here/")'

def _get_user_folder_path(patient_id):
    return patient_id + '/'

def _sanitize_file_name(name):
    return name.split('/', 1)[-1].replace("/", "_")
    
def _download(prefix, patient_id):
    print "this is going to download files to a folder in the current directory with named the patient id"
    folder_path = _get_user_folder_path(patient_id)
    if not os.path.exists(folder_path):
        os.mkdir(folder_path)
    extant_files = os.listdir(folder_path)
    download_list = _s3_list(prefix)
    length = len(download_list)
    
    for i, server_file_name in enumerate(download_list):
        local_file_name = _sanitize_file_name(server_file_name)
        
        #print statement of current status
        print str(i+1) + "/" + str(length) + ":", local_file_name,
        if local_file_name in extant_files:
            print " ... file already exists, skipping"
            continue
        print "downloading."
        with open(patient_id + '/' + local_file_name, 'w+') as f:
            f.write( _s3_retrieve(server_file_name) )


def download_all(patient_id):
    _download(patient_id+"/", patient_id)

def download_bluetooth(patient_id):
    _download(patient_id+"/bluetooth", patient_id)

def download_wifi(patient_id):
    _download(patient_id+"/wifi", patient_id)

def download_debug(patient_id):
    _download(patient_id+"/logFile", patient_id)

def download_accel(patient_id):
    _download(patient_id+"/accel", patient_id)

def download_gps(patient_id):
    _download(patient_id+"/gps", patient_id)

def download_audio(patient_id):
    _download(patient_id+"/voiceRecording", patient_id)

def download_texts(patient_id):
    _download(patient_id+"/texts", patient_id)

def download_calls(patient_id):
    _download(patient_id+"/call", patient_id)

def download_daily_survey_results_data(patient_id):
    _download(patient_id +'/'+"surveyAnswers/Daily", patient_id)

def download_weekly_survey_results_data(patient_id):
    _download(patient_id +'/'+"surveyAnswers/Weekly", patient_id)

def download_weekliy_survey_timings_data(patient_id):
    _download(patient_id +'/'+"surveyTimings/Weekly", patient_id)

def download_daily_survey_timings_data(patient_id):
    _download(patient_id +'/'+"surveytimings/Weekly", patient_id)

def download_power_state_timings_data(patient_id):
    _download(patient_id +'/'+"powerState/", patient_id)
