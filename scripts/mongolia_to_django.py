# Add the parent directory to the path in order to enable
# imports from sister directories
from os.path import abspath as _abspath
from sys import path as _path

_one_folder_up = _abspath(__file__).rsplit('/', 2)[0]
_path.insert(1, _one_folder_up)

# Load the Django settings
from config import load_django

# Import Mongolia models
from db.study_models import Studies as MStudies, Survey as MSurvey
from db.user_models import Admin as MAdmin

# Import Django models
from study.models import Researcher as DAdmin, Study as DStudy, Survey as DSurvey


# Actual code begins here
# AJK TODO write a script to convert the Mongolia database to Django
# AJK TODO maximize for efficiency
# AJK TODO chunk bulk_creation, especially for the green models (ChunkRegistry, FileToProcess)
# AJK TODO annotate everything
def migrate_studies():
    m_study_list = MStudies()
    d_study_list = []
    study_referents = {}
    for m_study in m_study_list:
        study_name = m_study['name']
        d_study = DStudy(
            name=study_name,
            encryption_key=m_study['encryption_key'],
            deleted=m_study['deleted'],
        )
        # AJK TODO should I catch this exception?
        d_study.full_clean()
        d_study_list.append(d_study)

        m_survey_list = m_study['surveys']
        m_admin_list = m_study['admins']
        m_device_settings = m_study['device_settings']
        study_referents[study_name] = {
            'survey_list': m_survey_list,
            'admin_list': m_admin_list,
            'device_settings': m_device_settings,
        }

    DStudy.objects.bulk_create(d_study_list)
    return study_referents


def migrate_surveys_admins_and_settings(study_referents):

    m_admin_duplicate_set = set()
    d_study_admin_list = []
    d_admin_list = []
    d_survey_list = []

    for study_name, object_ids in study_referents.iteritems():
        m_survey_id_list = object_ids['survey_list']
        m_admin_id_list = object_ids['admin_list']
        d_study = DStudy.objects.get(name=study_name)
        d_study_admin_list.append([d_study, []])

        for m_survey_id in m_survey_id_list:
            m_survey = MSurvey(m_survey_id)
            d_survey = DSurvey(
                content=m_survey['content'],
                survey_type=m_survey['survey_type'],
                settings=m_survey['settings'],
                timings=m_survey['timings'],
                study_id=d_study.pk,
                deleted=d_study.deleted,
            )

            d_survey.full_clean()
            d_survey_list.append(d_survey)

        for m_admin_id in m_admin_id_list:
            d_study_admin_list[-1][1].append(m_admin_id)
            if m_admin_id not in m_admin_duplicate_set:
                m_admin = MAdmin(m_admin_id)
                d_admin = DAdmin(
                    username=m_admin_id,
                    admin=m_admin['system_admin'],
                    access_key_id=m_admin['access_key_id'],
                    access_key_secret=m_admin['access_key_secret'],
                    access_key_secret_salt=m_admin['access_key_secret_salt'],
                    password=m_admin['password'],
                    salt=m_admin['salt'],
                    deleted=d_study.deleted,
                )
                m_admin_duplicate_set.add(m_admin_id)

                d_admin.full_clean()
                d_admin_list.append(d_admin)

    DSurvey.objects.bulk_create(d_survey_list)
    DAdmin.objects.bulk_create(d_admin_list)

    for study, admin_username_list in d_study_admin_list:
        admin_id_set = DAdmin.objects.filter(username__in=admin_username_list).values_list('pk', flat=True)
        study.researchers.add(*admin_id_set)


if __name__ == '__main__':
    print(DStudy.objects.count(), DSurvey.objects.count(), DAdmin.objects.count())

    study_referent_dict = migrate_studies()
    migrate_surveys_admins_and_settings(study_referent_dict)

    print(DStudy.objects.count(), DSurvey.objects.count(), DAdmin.objects.count())
