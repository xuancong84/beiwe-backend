from os import urandom

from werkzeug.datastructures import FileStorage
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from config.security import ASYMMETRIC_KEY_LENGTH
from libs.logging import log_error
from security import decode_base64
from db.study_models import Study

class DecryptionKeyError(Exception): pass
class HandledError(Exception): pass
class InvalidIV(Exception): pass
class InvalidData(Exception): pass

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
    """ Removes all extraneous config (new lines and labels from a formatted key
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

def encrypt_for_server(input_string, study_id):
    """ encrypts config using the ENCRYPTION_KEY, prepends the generated
        initialization vector.
        Use this function on an entire file (as a string)."""
    encryption_key = Study(study_id)['encryption_key']
    iv = urandom(16)
    return iv + AES.new( encryption_key, AES.MODE_CFB, segment_size=8, IV=iv ).encrypt( input_string )

def decrypt_server(data, study_id):
    """ Decrypts config encrypted by the encrypt_for_server function."""
    encryption_key = Study(study_id)['encryption_key']
    iv = data[:16]
    data = data[16:]
    return AES.new( encryption_key, AES.MODE_CFB, segment_size=8, IV=iv ).decrypt( data )

########################### User/Device Decryption #############################

def decrypt_device_file(patient_id, data, private_key):
    """ Runs the line-by-line decryption of a file encrypted by a device. """
    #This is a special handler for iOS file uploads.
    if type(data) is FileStorage:
        data = data.read()
    data = [line for line in data.split('\n') if line != "" ]
    return_data = ""
    
    try: #get the decryption key from the file.
        decoded_key = decode_base64( data[0].encode( "utf-8" ) )
        #TODO: data is sometimes an empty list, we get an index error.  Fix, don't catch.
        decrypted_key = decode_base64(private_key.decrypt( decoded_key ) )
    except (TypeError, IndexError) as e:
        raise DecryptionKeyError("invalid decryption key. %s" % e.message)

    #(we have an inefficiency in this encryption process, this might not need
    # to be doubly encoded in base64.  It works, not fixing it.)
    #The following is all error catching code for bugs we encountered (and solved)
    # in development.
    # print "length decrypted key", len(decrypted_key)
    for line in data[1:]:
        if line is None:
            print "encountered empty line of data, ignoring."
            continue
        try:
            return_data += decrypt_device_line(patient_id, decrypted_key, line) + "\n"
        except Exception as e:
            error_message = "There was an error in user decryption: "
            if isinstance(e, IndexError):
                error_message += "Something is wrong with data padding:\n\tline: %s" % line
                log_error(e, error_message)
                continue

            if isinstance(e, TypeError) and decrypted_key is None:
                error_message += "The key was empty:\n\tline: %s" % line
                log_error(e, error_message)
                continue

            ################### skip these errors ##############################
            if "unpack" in e.message:
                error_message += "malformed line of config, dropping it and continuing."
                log_error(e, error_message)
                #the config is not colon separated correctly, this is a single
                # line error, we can just drop it.
                # implies an interrupted write operation (or read)
                continue
            if "Input strings must be a multiple of 16 in length" in e.message:
                error_message += "Line was of incorrect length, dropping it and continuing."
                log_error(e, error_message)
                continue
            if isinstance(e, InvalidData):
                error_message += "Line contained no data, skipping: " + str(line)
                log_error(e, error_message)
                continue
            if isinstance(e, InvalidIV):
                error_message += "Line contained no iv, skipping: " + str(line)
                log_error(e, error_message)
                continue
            ##################### flip out on these errors #####################
            if 'AES key' in e.message: error_message += "AES key has bad length."
            elif 'IV must be' in e.message: error_message += "iv has bad length."
            elif 'Incorrect padding' in e.message:
                error_message += "base64 padding error, config is truncated."
                # this is only seen in mp4 files. possibilities:
                #  upload during write operation.
                #  broken base64 conversion in the app
                #  some unanticipated error in the file upload
            else:
                raise #If none of the above errors happened, raise the error.
            raise HandledError(error_message) #if any of them did happen, raise a HandledError to cease execution.
    return return_data

def decrypt_device_line(patient_id, key, data):
    """ config is expected to be 3 colon separated values.
        value 1 is the symmetric key, encrypted with the patient's public key.
        value 2 is the initialization vector for the AES CBC cipher.
        value 3 is the config, encrypted using AES CBC, with the provided key and iv. """
    iv, data = data.split(":")
    iv = decode_base64( iv.encode( "utf-8" ) ) #handle non-ascii encoding garbage...
    data = decode_base64( data.encode( "utf-8" ) )
    if not data:
        raise InvalidData()
    if not iv:
        raise InvalidIV
    try:
        decrypted = AES.new(key, mode=AES.MODE_CBC, IV=iv).decrypt( data )
    except Exception:
        if iv is None: len_iv = "None"
        else: len_iv = len(iv)
        if data is None: len_data = "None"
        else: len_data = len(data)
        if key is None: len_key = "None"
        else: len_key = len(key)
        print "length iv: %s, length data: %s, length key: %s" % (len_iv, len_data, len_key)
        print patient_id, key, data
        raise
    return remove_PKCS5_padding( decrypted )

################################################################################

def remove_PKCS5_padding(data):
    """ Unpacks encrypted config from the device that was encypted using the
        PKCS5 padding scheme (which is the ordinal value of the last byte). """
    #This can raise an indexerror when data is empty, but that is not expected behavior.
    return  data[0: -ord( data[-1] ) ]
