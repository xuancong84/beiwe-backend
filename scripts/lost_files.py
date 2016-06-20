from datetime import datetime, timedelta
from boto import connect_s3
from multiprocessing.pool import ThreadPool



relevant_data_types = {'survey_answers', 'audio_recordings'}

bucket_name = "beiwe"
connection = connect_s3(aws_access_key_id="AKIAI63QZHDTE3VMMC7A",
                  aws_secret_access_key="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")
bucket = connection.get_bucket(bucket_name)

import cPickle
f = open("MAT_AUDIO_FILENAMES_UPLOADED.pickle", 'r')
mat_audio_filenames_uploaded = cPickle.load(f); f.close() #mat_audio_filenames_uploaded
# f = open("MAT_AUDIO_FILENAMES_ORIGINAL.pickle", 'r')
# mat_audio_filenames_original = cPickle.load(f); f.close() #mat_audio_filenames_original
f = open("MAT_UPLOADED_SURVEYS.pickle", 'r')
mat_uploaded_surveys = cPickle.load(f); f.close() #mat_uploaded_surveys
f = open("TIM_SURVEY_FILENAMES_UPLOADED.pickle", 'r')
tim_survey_filenames_uploaded = cPickle.load(f); f.close() #tim_survey_filenames_uploaded
f = open("TIM_AUDIO_FILENAMES_UPLOADED.pickle", 'r')
tim_audio_filenames_uploaded = cPickle.load(f); f.close() #tim_audio_filenames_uploaded
f = open("ELI_FILES_RECONSTRUCTED.pickle", 'r')
eli_files_reconstructed = cPickle.load(f); f.close()

f = open("STUDY_ID_TO_AUDIO_SURVEY_ID.pickle", 'r')
study_id_to_audio_survey_id = cPickle.load(f); f.close() #study_id_to_audio_survey_id
f = open("STUDY_ID_TO_NAME.pickle", 'r')
study_id_to_name = cPickle.load(f); f.close() #study_id_to_name
f = open("USER_TO_STUDY_ID.pickle", 'r')
user_to_study_id = cPickle.load(f); f.close() #user_to_study_id

f = open("THE_7TH.pickle", 'r')
the_7th = cPickle.load(f); f.close()
f = open("THE_8TH.pickle", 'r')
the_8th = cPickle.load(f); f.close()
f = open("THE_9TH.pickle", 'r')
the_9th = cPickle.load(f); f.close()
f = open("THE_10TH.pickle", 'r')
the_10th = cPickle.load(f); f.close()

f = open("ALL_MISSING_FILES.pickle", 'r')
all_missing_files = cPickle.load(f); f.close()

f = open("CURRENT_AUDIO_FILES.pickle", 'r')
s3_audio_files = cPickle.load(f); f.close()
f = open("CURRENT_SURVEY_FILES.pickle", 'r')
s3_survey_files = cPickle.load(f); f.close()

all_uploaded_surveys = []
all_uploaded_surveys.extend(eli_files_reconstructed)
all_uploaded_surveys.extend(tim_survey_filenames_uploaded)
# all_uploaded_files.extend(tim_audio_filenames_uploaded)
all_uploaded_surveys.extend(mat_uploaded_surveys)
# all_uploaded_files.extend(mat_audio_filenames_uploaded)

#####################################################################################
#This commented out code generates some of the vars above, but it is slow and that data set is rather huge
# from bson import decode_all
# f7 = open("the_7th.bson", 'r')
# f8 = open("the_8th.bson", 'r')
# f9 = open("the_9th.bson", 'r')
# f10 = open("the_10th.bson", 'r')
# f11 = open("the_11th.bson", 'r')
# f_ans = open("answers", 'r')
# f_aud = open("audios", 'r')
#
# #getting data from the 7th and the 11th does not improve anything
# the_7th = [ z for z in decode_all(f7.read()) if z['data_type'] in relevant_data_types ]
# the_8th = [ z for z in decode_all(f8.read()) if z['data_type'] in relevant_data_types ]
# the_9th = [ z for z in decode_all(f9.read()) if z['data_type'] in relevant_data_types ]
# the_10th = [ z for z in decode_all(f10.read()) if z['data_type'] in relevant_data_types ]
# current_audio_files = set(f_aud.read().splitlines())
# current_survey_files = set(f_ans.read().splitlines())
# survey_files_current = current_survey_files
# f7.close(); f8.close(); f9.close(); f10.close(); f11.close(); f_ans.close(); f_aud.close()

# ds = [the_7th, the_8th, the_9th, the_10th ]
# for d in ds:
#     for z in d:
#         z['_id'] = str(z['_id'])
#         z['study_id'] = str(z['study_id'])
#         z.pop("chunk_hash")
#         z.pop('time_bin')
#         z.pop('is_chunkable')
# del ds, d

# all_missing_files = {str(d['_id']): d for d in the_7th}
# d_8 = {d['_id']: d for d in the_8th}
# d_9 = {d['_id']: d for d in the_9th}
# d_10 = {d['_id']: d for d in the_10th}

# all_missing_files.update(d_8)
# all_missing_files.update(d_9)
# #confirmed: all files in d_10 exist on s3
# for x in d_10:
#     if x in all_missing_files:
#         all_missing_files.pop(x)
#####################################################################################

def unix_millisecond_time_to_datetime(fp):
    return datetime.fromtimestamp(int(fp[-17:-7])) + timedelta(milliseconds=int(fp[-7:-4]))

def check_within_n_milliseconds(dt1, dt2, t):
    td = abs((dt1 - dt2).total_seconds())
    if td < t and td != 0:
        return True, td
    return False, td

def survey_times_by_user(files_by_time):
    #returns the files and dt assigned to each user
    #sort order is preserved
    files_by_user = {}
    for dt, fp in files_by_time:
        key = fp.split("/")[1]
        try:
            files_by_user[key].append((dt, fp))
        except KeyError:
            files_by_user[key] = [(dt, fp)]
    return files_by_user

def construct_user_time_mapping(time_by_user, n_seconds):
    data = {}
    for _, currents in time_by_user.items(): #for each user...
        for dt1, outer_fp in currents: # for each file...
            data[outer_fp] = []  # (this iterates once over every file)
            for dt2, inner_fp in currents: # for every Other file associated with the user... (n^2, ew)
                within_n, delta = check_within_n_milliseconds(dt1, dt2, n_seconds)
                if within_n: #if with n seconds...
                    data[outer_fp].append((delta, inner_fp)) #add to our data
                    # print int(inner_fp.split("/")[-1][:-4]) - int(outer_fp.split("/")[-1][:-4])
    return {k:d for k,d in data.items() if d}

# survey_files_old = [str(x['chunk_path']) for x in data.values() if x['data_type'] == 'survey_answers']

#get the dts
# survey_time_old = [ (unix_millisecond_time_to_datetime(x), x) for x in survey_files_old]
# survey_time_old.sort(key=lambda x:x[0])
# survey_time_current = [ (unix_millisecond_time_to_datetime(x), x) for x in survey_files_current]
# survey_time_current.sort(key=lambda x:x[0])

# survey_time_by_user_old = survey_times_by_user(survey_time_old)
# survey_time_by_user_current = survey_times_by_user(survey_time_current)

# current_data = construct_user_time_mapping(survey_time_by_user_current, 30)

def do_n_squared_comparison(fp_list):
    by_time = [(unix_millisecond_time_to_datetime(x), x) for x in fp_list]
    by_user = survey_times_by_user(by_time)

    datums = {0:[]}
    for x in range(10):
        datums[x + 1] = construct_user_time_mapping(by_user, x + 1)
        print str(x + 1) + ":", 'totes:', len(datums[x + 1]),
        if x != 0:
            print "diff:", len(datums[x + 1]) - len(datums[x])
        else: print ""
    return datums


print "\nall"
a = do_n_squared_comparison(all_uploaded_surveys)
print "\nmat"
b = do_n_squared_comparison(mat_uploaded_surveys)
print "\ntim:"
c = do_n_squared_comparison(tim_survey_filenames_uploaded)
print "\neli:"
d = do_n_squared_comparison(eli_files_reconstructed)
print ""

#
# potential_dupes = {}
# for x,data in d[5].items():
#     y = study_id_to_name[x.split("/",1)[0]]
#     if y in potential_dupes:
#         potential_dupes[y].append(x)
#
#         potential_dupes[y].extend([_[1] for _ in data])
#         potential_dupes[y] = list(set(potential_dupes[y]))
#         potential_dupes[y].sort()
#     else:
#         potential_dupes[y] = [x]
#         potential_dupes[y].extend([_[1] for _ in data])
# pprint(potential_dupes)
#
# #
# for s in eli_study_names:
#     print s
#     do_n_squared_comparison( {x for x in eli_files_reconstructed if study_id_to_name[x.split("/")[0]] == s } )
#     print ""

#####################################################################################
#there are actually duplicates in the missing files, we need a list of unique file hashes.
# I don't know how this happened, as the survey answer files should simply have been deleted
# and the file path should not show up again later.  This is not really a problem.
missing_surveys = list(set([x['chunk_path'] for x in all_missing_files.values() if x['data_type'] == "survey_answers"]))
fixed_missing_surveys = [x[0:-7] + '000' + ".csv" for x in missing_surveys]

#stick in fixed file_path, get out original file path
fixed_v_missing_map = dict(zip(fixed_missing_surveys, missing_surveys))

#identify files that already had 000 for milliseconds just in case...
fixed_v_missing_collisions = [x for x in fixed_missing_surveys if x in missing_surveys]

restored_surveys = [x for x in fixed_missing_surveys if x in s3_survey_files]
# length: 2158
unrestored_surveys = [x for x in fixed_missing_surveys if x not in s3_survey_files]
# length: 181

# probable_missing_surveys = [fixed_v_missing_map[x] for x in unrestored_surveys ]

missing_study_counts = {}
for x in unrestored_surveys:
    y = study_id_to_name[x.split("/")[0]]
    dt = unix_millisecond_time_to_datetime(x)
    if y in missing_study_counts:
        missing_study_counts[y].append((x, fixed_v_missing_map[x]))
        missing_study_counts[y] = list(set(missing_study_counts[y]))
        missing_study_counts[y].sort()
    else:
        missing_study_counts[y] = [(x, fixed_v_missing_map[x])]


restored_study_counts = {}
for x in restored_surveys:
    y = study_id_to_name[x.split("/")[0]]
    dt = unix_millisecond_time_to_datetime(x)
    if y in restored_study_counts:
        restored_study_counts[y].append((x, fixed_v_missing_map[x]))
        restored_study_counts[y] = list(set(restored_study_counts[y]))
        restored_study_counts[y].sort()
    else:
        restored_study_counts[y] = [(x, fixed_v_missing_map[x])]



wtf = [x for x in all_missing_files.values() if 'survey_id' not in x or not x['survey_id']]


#####################################################################################
#This is the first attempt at getting info, it was useful but meh.

#digits of precision of millisecond time
# FUZZY_SEARCH = 9

# def check_exists(fp):
#     raw = [_ for _ in bucket.list(prefix=fp)]
#     #to check for non_raw files we chop off the file name such that we get
#     #  within 10000 milliseconds (before)
#     non_raw = [_ for _ in bucket.list(prefix=fp[:-8])]
#     # we also grab within 100000 milliseconds to search for weirdo cases
#     really_non_raw = [ _ for _ in bucket.list(prefix=fp[:-FUZZY_SEARCH])]
#     return len(raw), len(non_raw), len(really_non_raw)
#
# survey_answers = [x for x in data.values() if x['data_type'] == 'survey_answers']
#
# pool = ThreadPool(50)
# # res = pool.map(check_exists, [x['chunk_path'] for x in the_10th])
# s_exists = pool.map(check_exists, [x['chunk_path'] for x in survey_answers])
# pool.close()
# pool.terminate()
#
# survey_data = []
# for d, (raw, not_raw, super_not) in zip(survey_answers, s_exists):
#     d['raw_exists'] = raw
#     d['replacement_exists'] = not_raw
#     d['very_fuzzy_exists'] = super_not
#     survey_data.append(d)
#
#
# restored_survey_answers = [f for f in survey_data if f['replacement_exists'] and f['data_type'] == 'survey_answers']
#
# s_w_replacements = [ x for x in survey_data if x['replacement_exists'] ]
# s_wo_replacements = [ x for x in survey_data if not x['replacement_exists'] ]
# s_w_maybe_replacements = [ x for x in survey_data if not x['replacement_exists'] and x['very_fuzzy_exists'] ]
#
#
# def get_time_variance(fp):
#     # FIXME: confirm file names are correct on uploaded csv restores unlike with audio files
#     a = fp.rsplit("/",1)[1][:-4]
#     b = [_.name[:-4] for _ in bucket.list(prefix=fp[:-FUZZY_SEARCH])][0]
#     number_value = b.rsplit("/",1)[1]
#     return int(a) - int(number_value), b
#
# for x in s_w_maybe_replacements:
#     variance, path = get_time_variance(x['chunk_path'])
#     if variance > 10000:
#         print "the following has a possible problem, time varience was %s seconds:" % (int(variance) / 1000.)
#         print study_id_to_name[x['chunk_path'].split('/',1)[0]]
#         print "current:", (path + ".csv").split('/',1)[1]
#         print "original:", x['chunk_path'].split('/',1)[1]

#####################################################################################

def oldenify(x):
    # in:  '567426811206f74055c34953/dxbaldfj/voiceRecording/569034001206f75106178464/1457834115000.mp4'
    # out: '567426811206f74055c34953/dxbaldfj/voiceRecording/1457834115.mp4'
    x = x[:-7] + x[-4:]
    split = x.split("/")
    return "/".join(split[:3]) + "/" + "/".join(split[-1:])

# reverse_map = {oldenify(x):x for x in current_audio_files if x.count("/") == 4}

audio_files_uploaded = set(oldenify(x) for x in s3_audio_files if x.count("/") == 4)
audio_files_then = set(x['chunk_path'] for x in all_missing_files.values() if x['data_type'] == 'audio_recordings')

audio_files_lost = [x for x in audio_files_then if x not in audio_files_uploaded]

audio_lost_count = {}
for x in audio_files_lost:
    y = study_id_to_name[x.split("/")[0]]
    if y in audio_lost_count:
        audio_lost_count[y].append(x)
        audio_lost_count[y].sort()
    else:
        audio_lost_count[y] = [x]

audio_restored_count = {}
for x in audio_files_uploaded:
    y = study_id_to_name[x.split("/")[0]]
    if y in audio_restored_count:
        audio_restored_count[y].append(x)
        audio_restored_count[y].sort()
    else:
        audio_restored_count[y] = [x]

#TODO:
#get list of files mat uploaded, check that it contains
#get list of files tim uploaded
#note about the 1 csv file that potentially deviated

#Determine

#list of files that originally went missing,
# files we have managed to restore,
# files we have not managed to restore (still missing)
# list of potential duplicates
# for all restored or uploaded files the source of that file.
#organized by study

#Also, get study and survey mapping info(?) for the conflicts I encountered in my restoration.