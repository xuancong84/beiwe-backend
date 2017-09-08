# Add the parent directory to the path in order to enable
# imports from sister directories
from os.path import abspath as _abspath
from sys import path as _path

_one_folder_up = _abspath(__file__).rsplit('/', 2)[0]
_path.insert(1, _one_folder_up)

# Load the Django settings
from config import load_django

# Import Mongolia models
from db.study_models import Studies as MStudies

# Import Django models
from study.models import Study as DStudy


# Actual code begins here
# AJK TODO write a script to convert the Mongolia database to Django
# Do chunked bulk_creates for speed, because there are a lot of files

print(DStudy.objects.count())

# AJK TODO annotate everything
# AJK TODO refactor: probably one function per model
m_study_list = MStudies()
d_study_list = []
for m_study in m_study_list:
    # AJK TODO keep a list of the admins, surveys etc.
    d_study = DStudy(
        name=m_study['name'],
        encryption_key=m_study['encryption_key'],
        deleted=m_study['deleted'],
    )
    # AJK TODO should I catch this exception?
    d_study.full_clean()
    d_study_list.append(d_study)

# AJK TODO chunk this, especially for the green models (ChunkRegistry, FileToProcess)
DStudy.objects.bulk_create(d_study_list)

print(DStudy.objects.count())
