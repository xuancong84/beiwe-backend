from boto import connect_s3
from boto.exception import S3ResponseError
from boto.s3.key import Key
import mimetypes
from constants import DB

CONN = connect_s3()


def _get_bucket(name):
    """ Method tries to get a bucket; returns None if bucket doesn't exist """
    try:
        bucket = CONN.get_bucket(name)
        return bucket
    except S3ResponseError:
        return None


def s3_upload_handler_file( key_name, file_obj ):
    """ Method uploads file object to bucket with key_name"""
    bucket = _get_bucket(DB)
    key = bucket.new_key(key_name)
    key.set_metadata('Content-Type', mimetypes.guess_type(key_name))
    # seek to the beginning of the file and read it into the key
    file_obj.seek(0)
    key.set_contents_from_file(file_obj)


def s3_upload_handler_string( key_name, some_string ):
    """ Method uploads string to bucket with key_name"""
    bucket = _get_bucket(DB)
    key = bucket.new_key(key_name)
    key.set_contents_from_string(some_string)
    
    

def list_s3_files( prefix ):
    """ Method fetches a list of filenames with prefix.
        note: entering the empty string into this search without later calling
        the object results in a truncated/paginated view."""
    bucket = _get_bucket(DB)
    results = bucket.list(prefix=prefix)
    return [i.name.strip("/") for i in results]


def s3_retrieve( key_name ):
    """ Method returns file contents with specified S3 key path"""
    key = Key(_get_bucket(DB), key_name)
    return key.read()


def s3_retrieve_raw( key_name ):
    """ Method returns the Key associated specified S3 key path"""
    return Key(_get_bucket(DB), key_name)


def s3_retrieve_two_weeks( prefix ): pass
    #TODO: Dori. Using a user ID retrieve two weeks (14 points?) of data


def s3_copy_with_new_name(old_name, new_name):
    """makes a copy of a file under a new name."""
    bucket = _get_bucket(DB)
    bucket.copy_key(new_name, DB, old_name)
    bucket.delete(old_name)
