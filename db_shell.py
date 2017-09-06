from libs.s3 import *
from db.user_models import User, Users, Admin, Admins
from db.study_models import Survey, Surveys, Study, Studies, StudyDeviceSettings, StudyDeviceSettingsCollection
from db.data_access_models import ChunkRegistry, ChunksRegistry, FileProcessLock, FileProcessLockCollection, FilesToProcess, FileToProcess
from db.profiling import EncryptionErrorMetadata, LineEncryptionError, DecryptionKeyError, UploadTracking, EncryptionErrorMetadatas, DecryptionKeyErrors, LineEncryptionErrors, Uploads
from bson import ObjectId


# import django
# from django.conf import settings
# from config.django_db_config import *
# settings.configure(
#     SECRET_KEY=SECRET_KEY,
#     DATABASES=DATABASES,
#     TIME_ZONE=TIME_ZONE,
#     INSTALLED_APPS=INSTALLED_APPS
# )
#
# django.setup()
#
# from db2.models import Study
