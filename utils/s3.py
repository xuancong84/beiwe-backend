from boto import connect_s3
from boto.exception import S3ResponseError
from boto.s3.connection import Location
from utils.files import decode, encode
from boto.s3.key import Key

CONN = connect_s3()

from constants import DB

def get_bucket(name):
    """ Tries to get bucket; else returns None if bucket doesn't exist """
    try:
        bucket = CONN.get_bucket(name)
        return bucket
    except S3ResponseError:
        return None
