from os import urandom

from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from data.passwords import PASSWORD as ENCRYPTION_KEY
from data.constants import ASYMMETRIC_KEY_LENGTH
from libs.logging import log_error
from security import decode_base64

""" The private keys are stored server-side (S3), and the public key is sent to
    the android device. """
################################################################################
################################# RSA ##########################################
################################################################################


def generate_key_pairing():
    """Generates a public-private key pairing, returns tuple (public, private)"""
    private_key = RSA.generate(ASYMMETRIC_KEY_LENGTH)
    public_key = private_key.publickey()
    return public_key.exportKey(), private_key.exportKey()


def prepare_X509_key_for_java( exported_key ):
    # This may actually be a PKCS8 Key specification.
    """ Removes all extraneous data (new lines and labels from a formatted key
        string, because this is how Java likes its key files to be formatted.
        Y'know, not according to the specification.  Because Java. """
    return "".join( exported_key.split('\n')[1:-1] )


def import_RSA_key( key ):
    return RSA.importKey( key )


# This function is only for use in debugging.
# def encrypt_rsa(blob, private_key):
#     return private_key.encrypt("blob of text", "literally anything")
#     """ 'blob of text' can be either a long or a string, we will use strings.
#         The second parameter must be entered... but it is ignored.  Really."""


################################################################################
################################# AES ##########################################
################################################################################

def encrypt_for_server(input_string):
    """ encrypts data using the ENCRYPTION_KEY, prepends the generated
        initialization vector.
        Use this function on an entire file (as a string)."""
    iv = urandom(16)
    return iv + AES.new( ENCRYPTION_KEY, AES.MODE_CFB, segment_size=8, IV=iv ).encrypt( input_string )

def decrypt_server(input_string):
    """ Decrypts data encrypted by the encrypt_for_server function."""
    
    iv = input_string[:16]
    return AES.new( ENCRYPTION_KEY, AES.MODE_CFB, segment_size=8, IV=iv ).decrypt( input_string[16:] )

########################### User/Device Decryption #############################

def decrypt_device_file(patient_id, data, private_key):
    """ Runs the line-by-line decryption of a file encrypted by a device. """

    data = [line for line in data.split('\n') if line != "" ]
    return_data = ""
    
    decoded_key = decode_base64( data[0].encode( "utf-8" ) )
    decrypted_key = decode_base64(private_key.decrypt( decoded_key ) )
    #we may have an inefficiency in this encryption process, this might not need
    # to be doubly encoded in base64

#     print "length decrypted key", len(decrypted_key)
    #this is all error catching for errors we encountered (and solved).
    for line in data[1:]:
        try:
            return_data += decrypt_device_line(patient_id, decrypted_key, line) + "\n"
        except Exception as e:
            error_message = "There was an error in user decryption: "
            
            ################### skip these errors ##############################
            if "unpack" in e.message:
                error_message += "malformed line of data, dropping it and continuing."
                log_error(e, error_message)
                #the data is not colon separated correctly, this is a single
                # line error, we can just drop it.
                # implies an interrupted write operation (or read)
                continue
            
            ##################### flip out on these errors #####################
            if 'AES key' in e.message:
                error_message += "AES key has bad length."
            elif 'IV must be' in e.message:
                error_message += "iv has bad length."
            
            elif 'Incorrect padding' in e.message:
                error_message += "base64 padding error, data is getting truncated."
                # this is only seen in mp4 files. possibilities:
                #  upload during write operation.
                #  broken base64 conversion is app
                #  some unanticipated error in the file upload
            
            log_error(e, error_message)
            raise
        
    return return_data

# provide a key by running get_client_private_key(patient_id)
def decrypt_device_line(patient_id, key, data):
    """ data is expected to be 3 colon separated values.
        value 1 is the symmetric key, encrypted with the patient's public key.
        value 2 is the initialization vector for the AES CBC cipher.
        value 3 is the data, encrypted using AES CBC, with the provided key and iv. """
    iv, data = data.split(":")
    #this nonsense is because we appear to accasionally get ascii encoding errors.
    iv = decode_base64( iv.encode( "utf-8" ) )
    data = decode_base64( data.encode( "utf-8" ) )
    
    try:
        decrypted = AES.new(key, mode=AES.MODE_CBC, IV=iv).decrypt( data )
    except Exception:
        print len(iv), len(data), len(key)
        raise
    
    return remove_PKCS5_padding( decrypted )

################################################################################

def remove_PKCS5_padding(data):
    """ Unpacks encrypted data from the device that was encypted using the
        PKCS5 padding scheme (which is the ordinal value of the last byte). """
    return  data[0: -ord( data[-1] ) ]
