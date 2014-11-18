""" The private key is stored server-side (on S3), and the public key is sent to
    the android device.
    Decryption is line by line, current method of separating data is by
    encoding the binary data as hex

    Server: private
    Device: public  """

from libs.s3 import s3_retrieve, s3_upload_handler_string

################################################################################
############################## Client Keys #####################################
################################################################################

def create_client_key_pair(patient_id):
    """Generate key pairing, push to database, return sanitized key for client."""
    public, private = _generate_key_pairing()
    s3_upload_handler_string( "keys/" + patient_id + "_private", private )
    s3_upload_handler_string( "keys/" + patient_id + "_public", public )


def get_client_public_key_string(patient_id):
    """Grabs a user's public key string from s3."""
    key_string = s3_retrieve( "keys/" + patient_id +"_public" )
    return prepare_X509_key_for_java( key_string )


def get_client_public_key(patient_id):
    """Grabs a user's public key file from s3."""
    key = s3_retrieve( "keys/" + patient_id +"_public" )
    return RSA.importKey( key )


def get_client_private_key(patient_id):
    """Grabs a user's private key file from s3."""
    key = s3_retrieve( "keys/" + patient_id +"_private" )
    return RSA.importKey( key )


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


def decrypt_rsa_lines(encrypted_lines, patient_id):
    """ This function takes a list of encrypted lines (from a client device) and
        decrypts every line separately, and returns a list of decrypted lines."""
    private_key = get_client_private_key(patient_id)
    return "\n".join([ private_key.decrypt( line.decode("hex") ) for line in encrypted_lines ])


def prepare_X509_key_for_java( exported_key ):
    # This may actually be a PKCS8 Key specification.
    """ Removes all extraneous data (new lines and labels from a formatted key
        string, because this is how Java likes its key files to be formatted.
        Y'know, not according to the specification.  Because Java. """
    return "".join( exported_key.split('\n')[1:-1] )


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
from security import decode_base64
from os import urandom

def encrypt_server(input_string):
    iv = urandom(16)
    return iv + AES.new( ENCRYPTION_KEY, AES.MODE_CFB, segment_size=8, IV=iv ).encrypt( input_string )

def decrypt_server(input_string):
    """ encrypts data using the ENCRYPTION_KEY, prepends the generated
        initialization vector.
        Use this function with the entire file (in string form) you wish to encrypt."""
    iv = input_string[:16]
    return AES.new( ENCRYPTION_KEY, AES.MODE_CFB, segment_size=8, IV=iv ).decrypt( input_string[16:] )


def decrypt_device_line(patient_id, data):
    """ data is expected to be 3 colon separated values.
        value 1 is the symmetric key, encrypted with the patient's public key.
        value 2 is the initialization vector for the AES cipher.
        value 3 is the data, encrypted using AES in cipher feedback mode, using
            the provided symmetric key and iv. """
    
    private_key = get_client_private_key(patient_id)
    symmetric_key, iv, data = data.split(":")
    
    iv = decode_base64(iv)
    data = decode_base64(data)
    symmetric_key = private_key.decrypt( symmetric_key )
    
    return remove_PKCS5_padding( AES.new(
                   symmetric_key, mode=AES.MODE_CBC, IV=iv).decrypt(data) )


def remove_PKCS5_padding(data):
    """ Unpacks encrypted data from the device that was encypted using the
        PKCS5 padding scheme (which is the ordinal value of the last byte). """
    return  data[0: -ord( data[-1] ) ]
