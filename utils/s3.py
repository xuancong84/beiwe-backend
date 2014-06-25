from boto import connect_s3
from boto.exception import S3ResponseError
from boto.s3.connection import Location
from boto.s3.key import Key
from utils.files import decode, encode

import mimetypes


CONN = connect_s3()

from constants import DB

def get_bucket(name):
    """ Tries to get bucket; else returns None if bucket doesn't exist """
    try:
        bucket = CONN.get_bucket(name)
        return bucket
    except S3ResponseError:
        return None

def s3_upload_handler(key_name, file_obj):
    bucket = get_bucket(DB)
    key = bucket.new_key(key_name)
    key.set_metadata('Content-Type', mimetypes.guess_type(self.filename)[0])
    # seek to the beginning of the file and read it into the key
    file_obj.seek(0)
    key.set_contents_from_file(file_obj)
