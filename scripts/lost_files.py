from boto import connect_s3
from multiprocessing.pool import ThreadPool
# from datetime import datetime

#digits of precision of millisecond time
FUZZY_SEARCH = 9

bucket_name = "beiwe"
connection = connect_s3(aws_access_key_id="AKIAI63QZHDTE3VMMC7A",
                  aws_secret_access_key="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")
bucket = connection.get_bucket(bucket_name)

relevant_data_types = {'survey_answers', 'audio_recordings'}
study_to_audio_survey_map = {"55d231c197013e3a1c9b8c31":"55d2350d97013e3a1c9b8c36","55d231c197013e3a1c9b8c31":"55db4c0597013e3fb50376a7","55d2332397013e3a1c9b8c33":"55d2353797013e3a1c9b8c37","55d330b897013e3a1c9b8c3c":"57165ea71206f75d7712adb5","55d3826297013e3a1c9b8c3e":"55f9fc8397013e62c885e72a","55dccfde97013e3fb50376ae":"55f1b79997013e32cd8adf3b","55dcd1cc97013e3fb50376b2":"55e0ab6497013e3fb50376be","560027a997013e4579f98d21":"560037a897013e4579f98d23","56019e2697013e66de3d0223":"5601a07e97013e66de3d0224","5601a5eb97013e66de3d0226":"5612d6ba97013e703b725e5f","5613ceaa97013e703b725e61":"5613cff697013e703b725e63","56180d9f97013e3a48101dfe":"56180f9997013e3a48101e03","56180e9e97013e3a48101e00":"56180faf97013e3a48101e04","5629525297013e1c75dce084":"5629533497013e1c75dce086","5629525297013e1c75dce084":"56fe88691206f744b40cf561","56325d8297013e33a2e57736":"5633779797013e33a2e57739","564dfcba97013e69346ddd95":"564e28e597013e69346ddd99","567426271206f74055c34951":"568aec6b1206f73e93c87124","567426811206f74055c34953":"569034001206f75106178464","567426ce1206f74055c34955":"56798a3e1206f7677df87197","5674271c1206f74055c34957":"5695774b1206f76a7e2e505a","56796f9f1206f7677df87086":"56be51ef1206f720205feaa2","56a0f93a1206f7615f9ce096":"56a0fb781206f7615f9ce0c6","56a795a31206f75bfce275ec":"56a797481206f75bfce27696","56c73edd1206f7160de71394":"56c74c1a1206f7160de71628","56c73edd1206f7160de71394":"56c764d91206f7160de71b48","56cf16231206f7536acbaf58":"56cf18271206f7536acbafbe","56d0b84e1206f706e258de83":"5707acc11206f77d6167a946","56d5eab21206f7036f891390":"56d5f7951206f7036f89166c","56d999151206f73defac57e7":"56d9b03e1206f73defac609e","56fc00221206f75acc14e395":"56fc019a1206f75acc14e48e","5703f0e61206f740445ec1a7":"5704063b1206f743c50c1e4d"}
study_id_to_name = {'55d231c197013e3a1c9b8c31': 'Test study ','55d2332397013e3a1c9b8c33': 'Test study ','55d235d397013e3a1c9b8c39': 'Test study ','55d330b897013e3a1c9b8c3c': 'PHQ-9 study with passive data','55d3826297013e3a1c9b8c3e': 'Debugging Study','55dccfde97013e3fb50376ae': 'McLean Webb','55dcd19097013e3fb50376b0': 'McLean Kaiser','55dcd1cc97013e3fb50376b2': 'MGH Perlis','55f1b37b97013e32cd8adf38': 'Test Study ','560027a997013e4579f98d21': 'HSPH Onnela Lab ','56019e2697013e66de3d0223': 'FAS Buckner','5601a5eb97013e66de3d0226': 'FAS Nock','5613ceaa97013e703b725e61': 'HSPH Onnela Lab_GPS Testing','561426aa97013e703b725e65': 'HSPH Onnela Lab_GPS Testing_2_Short Parameters','56180d9f97013e3a48101dfe': 'McLean Baker_Neurogenetic Analysis in Unipolar and Bipolar Depression','56180e9e97013e3a48101e00': 'McLean Baker and Buckner_Circuit Dynamics in Bipolar Disorder','56294df397013e1c75dce082': 'McLean Webb_Examining Reward-Related Predictors and Mechanisms of Change in BA Treatment for Anhedonic Adolescents','5629525297013e1c75dce084': 'BIDMC Keshavan and Torous_Feasibility and Sensitivity of a SMART for Schizophrenia','56325d8297013e33a2e57736': 'HSPH Onnela Lab_GitHub','5637d6a097013e43b65acfe9': 'Catalyst Rich-Edwards_Stress and Health Disparities','564dfcba97013e69346ddd95': 'FAS Buckner_Coombs_Seven Month In Depth Study of Real World Behaviors','564dfd8697013e69346ddd97': 'FAS Buckner_Coombs_In Depth Study of Behavioral States','567425971206f74055c3494f': 'FAS_Buckner_Coombs_Seven Month Real World Behaviors_Games','567426271206f74055c34951': 'FAS_Buckner_Coombs_Seven Month Real World Behaviors_Social Media / Internet','567426811206f74055c34953': 'FAS_Buckner_Coombs_Seven Month Real World Behaviors_TV / Movies','567426ce1206f74055c34955': 'FAS_Buckner_Coombs_Seven Month Real World Behaviors_Eating','5674271c1206f74055c34957': 'FAS_Buckner_Coombs_Seven Month Real World Behaviors_Exercise','56796f9f1206f7677df87086': 'FAS_Buckner_Coombs_Seven Month Real World Behaviors_Other 1','567970111206f7677df87088': 'FAS_Buckner_Coombs_Seven Month Real World Behaviors_Other 2','567970ae1206f7677df8708a': 'FAS_Buckner_Coombs_Seven Month Real World Behaviors_Other 3','569544c61206f76a7e2e443b': 'UW_McLaughlin_Adolescent Stress ','56a0f93a1206f7615f9ce096': 'Test study ','56a67b9d1206f70a8f76d77d': 'UW_McLaughlin_Adolescent Stress_Passive Data Only ','56a795a31206f75bfce275ec': 'Demo Study ','56ac04491206f75bfce30030': 'RAND_Rudin_Asthma Symptom Monitoring','56ac04e91206f75bfce30032': 'BWH_Lee_Rheumatoid Arthritis Flares ','56c73edd1206f7160de71394': 'Sonde Test Study ','56cb3cb71206f73ec4f506c6': 'Catalyst Test Study ','56cf16231206f7536acbaf58': 'HSPH_Onnela Lab_JP Test Data','56d0b84e1206f706e258de83': 'BWH_Smith_Digital Phenotyping of the Neurosurgical Patient','56d5eab21206f7036f891390': 'Rocket Farm Test Study ','56d999151206f73defac57e7': 'McLean_Stewart_NCIS','56fc00221206f75acc14e395': 'MGH Berry Feasibility and Sensitivity of a SMART for Amyotrophic Lateral Sclerosis','5703f0e61206f740445ec1a7': 'Google Test Study ','571a5c6d1206f722f557e84a': 'HSPH Onnela Lab_Passive Data High Sampling','5721136c1206f76ce19e0b56': 'HSPH Onnela Lab_beta testing','5729238c1206f72d18c80985': 'McLean_Bjorgvinsson_Using EMA to Assess Outcomes Following Discharge from Partial Hospitalization','5731566f1206f73a6b6dcd16': 'BWH_Oser and Torous_Feasibility of Smartphone Active and Passive Monitoring in CBT ','573f25971206f72054f6daa2': 'HSPH_Test study_Maria','57474b061206f70a74f19b62': 'hsph_onnela lab_maria test 2','5751c9fd1206f715072b96c4': 'HSPH Onnela Lab_iOS Test Study 1','5755a70f1206f747fdc5bfdf': 'FAS_Buckner_Coombs_SCS_SocialMedia_Internet','5755a9ff1206f747fdc5c078': 'FAS_Buckner_Coombs_SCS_TV_Movies','5755ab561206f747fdc5c07a': 'FAS_Buckner_Coombs_SCS_Eating','5755ac431206f747fdc5c0b6': 'FAS_Buckner_Coombs_SCS_Exercise','5756e5721206f73b274d4e53': 'HSPH Onnela Lab_iOS Test Study 2','575aeb251206f76f032979e7': 'FAS_Buckner_Coombs_SCS_Test study '}


from bson import decode_all
f7 = open("the_7th.bson", 'r')
f8 = open("the_8th.bson", 'r')
f9 = open("the_9th.bson", 'r')
f10 = open("the_10th.bson", 'r')
f11 = open("the_11th.bson", 'r')
f_ans = open("answers", 'r')
f_aud = open("audios", 'r')

#getting data from the 7th and the 11th does not improve anything
the_7th = [ z for z in decode_all(f7.read()) if z['data_type'] in relevant_data_types ]
the_8th = [ z for z in decode_all(f8.read()) if z['data_type'] in relevant_data_types ]
the_9th = [ z for z in decode_all(f9.read()) if z['data_type'] in relevant_data_types ]
the_10th = [ z for z in decode_all(f10.read()) if z['data_type'] in relevant_data_types ]
current_audio_files = set(f_aud.read().splitlines())
current_survey_files = set(f_ans.read().splitlines())
f7.close(); f8.close(); f9.close(); f10.close(); f11.close(); f_ans.close(); f_aud.close()

ds = [the_8th, the_9th, the_10th ]
for d in ds:
    for z in d:
        z['_id'] = str(z['_id'])
        z['study_id'] = str(z['study_id'])
        z.pop("chunk_hash")
        z.pop('time_bin')
        z.pop('is_chunkable')
del ds, d

data = {str(d['_id']): d for d in the_7th}
d_8 = {d['_id']: d for d in the_8th}
d_9 = {d['_id']: d for d in the_9th}
d_10 = {d['_id']: d for d in the_10th}

data.update(d_8)
data.update(d_9)
#confirmed: all files in d_10 exist on s3
for x in d_10:
    if x in data:
        data.pop(x)


#####################################################################################

def check_exists(fp):
    raw = [_ for _ in bucket.list(prefix=fp)]
    #to check for non_raw files we chop off the file name such that we get
    #  within 10000 milliseconds (before)
    non_raw = [_ for _ in bucket.list(prefix=fp[:-8])]
    # we also grab within 100000 milliseconds to search for weirdo cases
    really_non_raw = [ _ for _ in bucket.list(prefix=fp[:-FUZZY_SEARCH])]
    return len(raw), len(non_raw), len(really_non_raw)

survey_answers = [x for x in data.values() if x['data_type'] == 'survey_answers']

pool = ThreadPool(50)
# res = pool.map(check_exists, [x['chunk_path'] for x in the_10th])
s_exists = pool.map(check_exists, [x['chunk_path'] for x in survey_answers])
pool.close()
pool.terminate()

survey_data = []
for d, (raw, not_raw, super_not) in zip(survey_answers, s_exists):
    d['raw_exists'] = raw
    d['replacement_exists'] = not_raw
    d['very_fuzzy_exists'] = super_not
    survey_data.append(d)


restored_survey_answers = [f for f in survey_data if f['replacement_exists'] and f['data_type'] == 'survey_answers']

s_w_replacements = [ x for x in survey_data if x['replacement_exists'] ]
s_wo_replacements = [ x for x in survey_data if not x['replacement_exists'] ]
s_w_maybe_replacements = [ x for x in survey_data if not x['replacement_exists'] and x['very_fuzzy_exists'] ]


def get_time_variance(fp):
    a = fp.rsplit("/",1)[1][:-4]
    b = [_.name[:-4] for _ in bucket.list(prefix=fp[:-FUZZY_SEARCH])][0]
    number_value = b.rsplit("/",1)[1]
    return int(a) - int(number_value), b

for x in s_w_maybe_replacements:
    variance, path = get_time_variance(x['chunk_path'])
    if variance > 10000:
        print "the following has a possible problem, time varience was %s seconds:" % (int(variance) / 1000.)
        print study_id_to_name[x['chunk_path'].split('/',1)[0]]
        print "current:", (path + ".csv").split('/',1)[1]
        print "original:", x['chunk_path'].split('/',1)[1]

#####################################################################################

def oldenify(x):
    # in:  '567426811206f74055c34953/dxbaldfj/voiceRecording/569034001206f75106178464/1457834115000.mp4'
    # out: '567426811206f74055c34953/dxbaldfj/voiceRecording/1457834115.mp4'
    x = x[:-7] + x[-4:]
    split = x.split("/")
    return "/".join(split[:3]) + "/" + "/".join(split[-1:])

# reverse_map = {oldenify(x):x for x in current_audio_files if x.count("/") == 4}

audio_files_uploaded = set(oldenify(x) for x in current_audio_files if x.count("/") == 4)
audio_files_then = set(x['chunk_path'] for x in data.values() if x['data_type'] == 'audio_recordings')

then_not_up = audio_files_then.difference(audio_files_uploaded)
# up_not_then = audio_files_uploaded.difference(audio_files_then)

print len(then_not_up)

for x in sorted(list(then_not_up)):
    print study_id_to_name[x[:24]],"||", x[25:]
    # print datetime.fromtimestamp(int(x[-14:-4]))


#TODO:
#are any files from MGH Perlis restored? yes.
#get list of files mat uploaded, check that it contains
#get list of files tim uploaded
#