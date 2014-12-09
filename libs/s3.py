from boto import connect_s3
from boto.exception import S3ResponseError
from boto.s3.key import Key
from data.constants import S3_BUCKET
from libs import encryption
# import mimetypes

CONN = connect_s3()


def _get_bucket(name):
    """ Method tries to get a bucket; returns None if bucket doesn't exist """
    try:
        bucket = CONN.get_bucket(name)
        return bucket
    except S3ResponseError:
        return None


# def s3_upload_handler_file( key_name, file_obj ):
#     """ Method uploads file object to bucket with key_name"""
#     bucket = _get_bucket(S3_BUCKET)
#     key = bucket.new_key(key_name)
#     key.set_metadata('Content-Type', mimetypes.guess_type(key_name))
#     # seek to the beginning of the file and read it into the key
#     file_obj.seek(0)
#     key.set_contents_from_file(file_obj)


def s3_upload( key_name, some_string ):
    """ Method uploads string to bucket with key_name"""
    bucket = _get_bucket(S3_BUCKET)
    key = bucket.new_key(key_name)
    key.set_contents_from_string(some_string)


def s3_upload_encrypted( key_name, some_string ):
    bucket = _get_bucket(S3_BUCKET)
    key = bucket.new_key(key_name)
    data = encryption.encrypt_for_server(some_string)
    key.set_contents_from_string(data)


def s3_retrieve_decrypt(key_name):
    key = Key(_get_bucket(S3_BUCKET), key_name)
    return encryption.decrypt_server( key.read() )


def s3_list_files( prefix ):
    """ Method fetches a list of filenames with prefix.
        note: entering the empty string into this search without later calling
        the object results in a truncated/paginated view."""
    bucket = _get_bucket(S3_BUCKET)
    results = bucket.list(prefix=prefix)
    return [i.name.strip("/") for i in results]


def s3_retrieve( key_name ):
    """ Method returns file contents with specified S3 key path"""
    key = Key(_get_bucket(S3_BUCKET), key_name)
    return key.read()


def s3_retrieve_raw( key_name ):
    """ Method returns the Key associated specified S3 key path"""
    return Key(_get_bucket(S3_BUCKET), key_name)


# def s3_copy_with_new_name(old_name, new_name):
#     """makes a copy of a file under a new name."""
#     bucket = _get_bucket(S3_BUCKET)
#     bucket.copy_key(new_name, S3_BUCKET, old_name)
#     s3_upload(new_name, s3_retrieve(old_name))
#     bucket.delete_key(old_name)


################################################################################
######################### Client Key Management ################################
################################################################################

def create_client_key_pair(patient_id):
    """Generate key pairing, push to database, return sanitized key for client."""
    public, private = encryption.generate_key_pairing()
    s3_upload( "keys/" + patient_id + "_private", private )
    s3_upload( "keys/" + patient_id + "_public", public )


def get_client_public_key_string(patient_id):
    """Grabs a user's public key string from s3."""
    key_string = s3_retrieve( "keys/" + patient_id +"_public" )
    return encryption.prepare_X509_key_for_java( key_string )


def get_client_public_key(patient_id):
    """Grabs a user's public key file from s3."""
    key = s3_retrieve( "keys/" + patient_id +"_public" )
    return encryption.import_RSA_key( key )


def get_client_private_key(patient_id):
    """Grabs a user's private key file from s3."""
    key = s3_retrieve( "keys/" + patient_id +"_private" )
    return encryption.import_RSA_key( key )
