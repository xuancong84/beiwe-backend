from boto import connect_s3
from boto.exception import S3ResponseError
from boto.s3.connection import Location
from boto.s3.key import Key

import mimetypes


CONN = connect_s3()

from constants import DB


def get_bucket(name):
    """ Method tries to get bucket; else returns None if bucket doesn't exist """
    try:
        bucket = CONN.get_bucket(name)
        return bucket
    except S3ResponseError:
        return None


def s3_upload_handler(key_name, file_obj):
    """ Method uploads file object to bucket with key_name"""
    bucket = get_bucket(DB)
    key = bucket.new_key(key_name)
    key.set_metadata('Content-Type', mimetypes.guess_type(key_name))
    # seek to the beginning of the file and read it into the key
    file_obj.seek(0)
    key.set_contents_from_file(file_obj)


def list_s3_files(prefix):
    """ Method fetches a list of filenames with prefix"""
    b = get_bucket(DB)
    results = b.list(prefix=prefix)
    return [i.name.strip("/") for i in results]


def s3_retrieve(key_name):
    """ Method returns file contents with specified S3 key path"""
    key = Key(get_bucket(DB), key_name)
    return key.read()


def s3_retreive_two_weeks(prefix):
    #TODO: using a user ID retrieve two weeks (14 points??) of data
    