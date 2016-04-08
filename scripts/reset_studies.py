# Test study 1: 55d231c197013e3a1c9b8c31
# Test study 2: 55d2332397013e3a1c9b8c33
# Test study 3: 55d235d397013e3a1c9b8c39
# Debugging Study: 55d3826297013e3a1c9b8c3e
# UW_McLaughlin_Adolescent Stress : 569544c61206f76a7e2e443b
# Test study 4: 56a0f93a1206f7615f9ce096
# UW_McLaughlin_Adolescent Stress_Passive Data Only : 56a67b9d1206f70a8f76d77d
# Demo Study : 56a795a31206f75bfce275ec
# RAND_Rudin_Asthma Symptom Monitoring: 56ac04491206f75bfce30030
# BWH_Lee_Rheumatoid Arthritis Flares : 56ac04e91206f75bfce30032
from bson import ObjectId

from db.data_access_models import FilesToProcess
from db.study_models import Study
from libs.file_processing_utils import reindex_study
from libs.logging import email_system_administrators

studies = []

if not studies:
    raise Exception("you need to provide some studies")


def do_email( study ):
    email_system_administrators( study.name + " blew up while reindexing",
                                 "Go check on reindex operation.",
                                 source_email="reindexing_error@studies.beiwe.org" )


for study_id in studies:
    if isinstance( study_id, (str, unicode) ):
        study_id = ObjectId( study_id )
    study = Study(study_id)

    print "============================================================="
    print "============================================================="
    print "============================================================="
    print "starting on %s, study id: %s\n" % (study.name, str(study_id))
    print "============================================================="
    print "============================================================="
    print "============================================================="

    if FilesToProcess.count() != 0:
        do_email(study)
        print "stopped on " + str( study_id )
        break

    study_id = ObjectId( study_id )

    try:
        reindex_study(study)
    except Exception as e:
        do_email( study )
        print "stopped on " + str( study_id )
        break
