""" The private key is stored server-side (on S3), and the public key is sent to
    the android device.
    Decryption is line by line, current method of separating data is by
    encoding the binary data as hex
    
    Server: private
    Device: public  """
    
from libs.s3 import (s3_retrieve, s3_upload_handler_file, S3ResponseError,
    s3_list_files, s3_upload_handler_string)

################################################################################
############################## Client Keys #####################################
################################################################################

def create_client_key_pair(user_id):
    """Generate key pairing, push to database, return sanitized key for client."""
    public, private = _generate_key_pairing()
    s3_upload_handler_string( "keys/" + user_id + "_private", private )
    s3_upload_handler_string( "keys/" + user_id + "_public", public )
    
    
def get_client_public_key_string(user_id):
    """Grabs a user's public key string from s3."""
    key_string = s3_retrieve( "keys/" + user_id +"_public" )
    return prepare_X509_key_for_java( key_string )
    
    
def get_client_public_key(user_id):
    """Grabs a user's public key file from s3."""
    key = s3_retrieve( "keys/" + user_id +"_public" )
    return RSA.importKey( key )
    
    
def get_client_private_key(user_id):
    """Grabs a user's private key file from s3."""
    key = s3_retrieve( "keys/" + user_id +"_private" )
    return RSA.importKey( key )
    
    
def check_client_key(user_id):
    if len(s3_list_files( "keys/" + user_id )) == 1:
        return True
    return False

################################################################################
################################# RSA ##########################################
################################################################################
from Crypto.PublicKey import RSA
from data.constants import ASYMMETRIC_KEY_LENGTH

def _generate_key_pairing():
    """Generates a public-private key pairing, returns tuple (public, private)"""
    private_key = RSA.generate(ASYMMETRIC_KEY_LENGTH)
    public_key = private_key.publickey()
    return public_key.exportKey(), private_key.exportKey()
    
    
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
    return "".join( exported_key.split('\n')[1:-2] )
    
    
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
from data.passwords import PASSWORD as ENCRYPTION_KEY

def encrypt_aes(input_string):
    return AES.new( ENCRYPTION_KEY, AES.MODE_CFB ).encrypt( input_string )
    
def decrypt_aes(input_string):
    return AES.new( ENCRYPTION_KEY, AES.MODE_CFB ).decrypt( input_string )
