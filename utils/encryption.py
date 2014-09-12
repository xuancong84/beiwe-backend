""" The private key is stored server-side (on S3), and the public key is sent to
    the android device.
    Decryption is line by line, current method of separating data is by
    encoding the binary data as hex
    
    Server: private
    Device: public  """

from utils.s3 import s3_retrieve, s3_upload_handler_file, S3ResponseError

################################################################################
############################## Client Keys #####################################
################################################################################

def create_client_key_pair(user_id):
    """Generate key pairing, push to database, return sanitized key for client."""
    public, private = _generate_key_pairing()
    s3_upload_handler_file( "keys/" + user_id, private )
    return prepare_X509_key_for_java(public)


def get_client_key(user_id):
    """Grabs a user's key file from s3, if key does not exist returns None."""
    try: key = s3_retrieve( "keys/" + user_id )
    except S3ResponseError:
        return None
    return RSA.importKey( key )


################################################################################
################################# RSA ##########################################
################################################################################

from Crypto.PublicKey import RSA
from utils.constants import ASYMMETRIC_KEY_LENGTH

def _generate_key_pairing():
    """Generates a public-private key pairing, returns tuple (public, private)"""
    private_key = RSA.generate(ASYMMETRIC_KEY_LENGTH)
    public_key = private_key.publickey()
    return public_key.exportKey(), private_key.exportKey()
    
    
#TODO: Eli. deprecate
def get_private_key_from_file(file_name):
    with open("file_name", 'r') as f:
        return RSA.importKey( f.read() )
    
    
#TODO: Eli. merge with the csv reader?
def decrypt_rsa(encrypted_csv, private_key):
    """ This function takes a csv file encrypted on the client device and
        decrypts every line separately.  It then returns those concatenated
        lines?"""
    lines = encrypted_csv.splitlines()
    return "\n".join( [ private_key.decrypt( line ) for line in lines ] )
    
    
def prepare_X509_key_for_java( exported_key ):
    # This may actually be a PKCS8 Key specification.
    """ Removes all extraneous data (new lines and labels from a formatted key
        string, because this is how Java likes its key files to be formatted. """
    return "".join(exported_key.split('\n')[1:-2])
    
    
# This function is never intended to be used, it is only for debugging.
# def encrypt_rsa(blob, private_key):
#     return private_key.encrypt("blob of text", "literally anything")
#     """ 'blob of text' can be either a long or a string, we will use strings.
#         The second parameter must be entered... but it is ignored.  Really."""


################################################################################
################################# AES ##########################################
################################################################################

""" We are using AES in CFB mode because we do not have a [good-and-simple] way
    of enforcing separate storage of initialization vectors from keys or files. """

from Crypto.Cipher import AES
from utils.secure import PASSWORD as ENCRYPTION_KEY

def encrypt_aes(input_string):
    return AES.new(ENCRYPTION_KEY, AES.MODE_CFB).encrypt( input_string )
    
def decrypt_aes(input_string):
    return AES.new( ENCRYPTION_KEY, AES.MODE_CFB).decrypt( input_string )