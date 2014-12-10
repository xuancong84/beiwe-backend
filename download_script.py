print "\n...\n"

try:
    from libs.s3 import s3_list_files as _s3_list, s3_retrieve as _s3_retrieve
    from urllib2 import urlopen as _urlopen
    from libs.encryption import decrypt_server as _decrypt
except ImportError as e:
    print "\n You need to solve this import error, I recommend using pip."
    print e.message, "\n"
    raise e

print "\n...\n"

try:
    _encrypted_user_list = _urlopen("https://beiwe.org/user_list").read()
    user_list = _decrypt(_encrypted_user_list).split(',')
    print "\na variable \"user_list\" has been created, it contains all users "
except Exception:
    print "\nunable to get user list.\n"
    exit()

def _download(prefix):
    print "this is going to return a dictionary of the form file_name:data"
    file_list = _s3_list(prefix)
    length = len(file_list)
    data = {}
    for i, file_name in enumerate(file_list):
        print i , "/" , length, ":", file_name
        data[file_name] = _s3_retrieve(file_name)
    return data
        
def download_bluetooth(user_name):
    return _download(user_name+"/bluetooth")
    
def download_wifi(user_name):
    return _download(user_name+"/wifi")
    
def download_debug(user_name):
    return _download(user_name+"/logFile")

def download_accel(user_name):
    return _download(user_name+"/accel")
    
def download_gps(user_name):
    return _download(user_name+"/gps")
    
def download_audio(user_name):
    return _download(user_name+"/voiceRecording")
    
def download_texts(user_name):
    return _download(user_name+"/texts")
    
def download_calls(user_name):
    return _download(user_name+"/call")