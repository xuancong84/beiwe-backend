from datetime import datetime, timedelta

from django.db import models
from django.utils import timezone

from config.constants import UPLOAD_FILE_TYPE_MAPPING
from libs.security import decode_base64
from database.base_models import AbstractModel, JSONTextField


class EncryptionErrorMetadata(AbstractModel):
    
    file_name = models.CharField(max_length=256)
    total_lines = models.PositiveIntegerField()
    number_errors = models.PositiveIntegerField()
    errors_lines = JSONTextField()
    error_types = JSONTextField()


class LineEncryptionError(AbstractModel):

    AES_KEY_BAD_LENGTH = "AES_KEY_BAD_LENGTH"
    EMPTY_KEY = "EMPTY_KEY"
    INVALID_LENGTH = "INVALID_LENGTH"
    IV_BAD_LENGTH = "IV_BAD_LENGTH"
    IV_MISSING = "IV_MISSING"
    LINE_EMPTY = "LINE_EMPTY"
    LINE_IS_NONE = "LINE_EMPTY"
    MALFORMED_CONFIG = "MALFORMED_CONFIG"
    MP4_PADDING = "MP4_PADDING"
    PADDING_ERROR = "PADDING_ERROR"
    
    ERROR_TYPE_CHOICES = (
        (AES_KEY_BAD_LENGTH, AES_KEY_BAD_LENGTH),
        (EMPTY_KEY, EMPTY_KEY),
        (INVALID_LENGTH, INVALID_LENGTH),
        (IV_BAD_LENGTH, IV_BAD_LENGTH),
        (IV_MISSING, IV_MISSING),
        (LINE_EMPTY, LINE_EMPTY),
        (LINE_IS_NONE, LINE_IS_NONE),
        (MP4_PADDING, MP4_PADDING),
        (MALFORMED_CONFIG, MALFORMED_CONFIG),
        (PADDING_ERROR, PADDING_ERROR),
    )
    
    type = models.CharField(max_length=32, choices=ERROR_TYPE_CHOICES)
    line = models.TextField(blank=True)
    base64_decryption_key = models.CharField(max_length=256)
    prev_line = models.TextField(blank=True)
    next_line = models.TextField(blank=True)


class DecryptionKeyError(AbstractModel):
    
    file_path = models.CharField(max_length=256)
    contents = models.TextField()
    
    participant = models.ForeignKey('Participant', on_delete=models.PROTECT, related_name='decryption_key_errors')
    
    def decode(self):
        return decode_base64(self.contents)


class UploadTracking(AbstractModel):
    
    file_path = models.CharField(max_length=256)
    file_size = models.PositiveIntegerField()
    timestamp = models.DateTimeField()

    participant = models.ForeignKey('Participant', on_delete=models.PROTECT, related_name='upload_trackers')
    
    @classmethod
    def get_trailing(cls, time_delta):
        return cls.objects.filter(timestamp__gte=timezone.now() - time_delta)
    
    @classmethod
    def get_trailing_count(cls, time_delta):
        cls.objects.filter(timestamp__gte=timezone.now() - time_delta).count()
    
    @classmethod
    def weekly_stats(cls, days=7, get_usernames=False):
        ALL_FILETYPES = UPLOAD_FILE_TYPE_MAPPING.values()
        if get_usernames:
            data = {filetype: {"megabytes": 0., "count": 0, "users": set()} for filetype in ALL_FILETYPES}
        else:
            data = {filetype: {"megabytes": 0., "count": 0} for filetype in ALL_FILETYPES}
        
        data["totals"] = {}
        data["totals"]["total_megabytes"] = 0
        data["totals"]["total_count"] = 0
        data["totals"]["users"] = set()
        
        for i, upload in enumerate(cls.get_trailing(timedelta(days=days))):
            # global stats
            data["totals"]["total_count"] += 1
            data["totals"]["total_megabytes"] += upload['file_size'] / 1024. / 1024.
            data["totals"]["users"].add(upload['user_id'])
            
            # get data stream type from file_path
            file_type = UPLOAD_FILE_TYPE_MAPPING[upload['file_path'].split("/", 2)[1]]
            # update per-data-stream information
            data[file_type]["megabytes"] += upload['file_size'] / 1024. / 1024.
            data[file_type]["count"] += 1
            
            if get_usernames:
                data[file_type]["users"].add(upload["user_id"])
            if i % 10000 == 0:
                print("processed %s uploads..." % i)
        
        data["totals"]["user_count"] = len(data["totals"]["users"])
        
        if not get_usernames:  # purge usernames if we don't need them.
            del data["totals"]["users"]
        
        return data
