import json
from os import urandom
from security import decode_base64

from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from flask import request
from werkzeug.datastructures import FileStorage

from config.settings import ASYMMETRIC_KEY_LENGTH, IS_STAGING
from libs.logging import log_error
from database.models import Study, DecryptionKeyError, EncryptionErrorMetadata, LineEncryptionError


class DecryptionKeyInvalidError(Exception): pass
class HandledError(Exception): pass
class InvalidIV(Exception): pass
class InvalidData(Exception): pass
class DefinitelyInvalidFile(Exception):pass

# The private keys are stored server-side (S3), and the public key is sent to the android device.

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
    """ Removes all extraneous config (new lines and labels from a formatted key string,
    because this is how Java likes its key files to be formatted.
    (Y'know, not in accordance with the specification.  Because Java. """
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

def encrypt_for_server(input_string, study_object_id):
    """
    Encrypts config using the ENCRYPTION_KEY, prepends the generated initialization vector.
    Use this function on an entire file (as a string).
    """

    encryption_key = Study.objects.get(object_id=study_object_id).encryption_key
    iv = urandom(16)
    return iv + AES.new( encryption_key, AES.MODE_CFB, segment_size=8, IV=iv ).encrypt( input_string )


def decrypt_server(data, study_object_id):
    """ Decrypts config encrypted by the encrypt_for_server function."""
    encryption_key = Study.objects.filter(object_id=study_object_id).values_list('encryption_key', flat=True).get()
    iv = data[:16]
    data = data[16:]
    return AES.new( encryption_key, AES.MODE_CFB, segment_size=8, IV=iv ).decrypt( data )


########################### User/Device Decryption #############################


def decrypt_device_file(patient_id, original_data, private_key, user):
    """ Runs the line-by-line decryption of a file encrypted by a device.
    This function is a special handler for iOS file uploads. """
    
    def create_line_error_db_entry(error_type):
        # declaring this inside decrypt device file to access its function-global variables
        # TODO @Eli consider enabling this on prod as well
        if IS_STAGING:
            LineEncryptionError.objects.create(
                type=error_type,
                base64_decryption_key=private_key.decrypt(decoded_key),
                line=line,
                prev_line=file_data[i - 1] if i > 0 else '',
                next_line=file_data[i + 1] if i < len(file_data) - 1 else '',
            )
    
    if isinstance(original_data, FileStorage):
        file_data = original_data.read()
    elif isinstance(original_data, (unicode, str)):
        #namespace is immediately overwritten, this is fine.
        file_data = original_data
    else:
        raise TypeError("expected string or werkzeug.datastructures.FileStorage")
    
    bad_lines = []
    error_types = []
    error_count = 0
    return_data = ""
    file_data = [line for line in file_data.split('\n') if line != ""]
    
    try: #get the decryption key from the file.
        decoded_key = decode_base64(file_data[0].encode("utf-8"))
        decrypted_key = decode_base64(private_key.decrypt( decoded_key ) )
    except (TypeError, IndexError) as e:
        DecryptionKeyError.objects.create(
            file_path=request.values['file_name'],
            contents='\n'.join(file_data),
            participant=user,
        )
        raise DecryptionKeyInvalidError("invalid decryption key. %s" % e.message)
    
    # (we have an inefficiency in this encryption process, this might not need to be doubly
    # encoded in base64.  This is probably never going to be changed.)
    # The following is all error catching code for bugs we encountered (and solved) in development.
    # print "length decrypted key", len(decrypted_key)
    
    for i, line in enumerate(file_data):
        #we need to skip the first line (the decryption key), but need real index values in i
        if i==0: continue
        
        if line is None:
            #this case causes weird behavior inside decrypt_device_line, so we test for it instead.
            error_count += 1
            create_line_error_db_entry(LineEncryptionError.LINE_IS_NONE)
            error_types.append(LineEncryptionError.LINE_IS_NONE)
            bad_lines.append(line)
            print("encountered empty line of data, ignoring.")
            continue
            
        try:
            return_data += decrypt_device_line(patient_id, decrypted_key, line) + "\n"
        except Exception as e:
            error_count += 1
            
            error_message = "There was an error in user decryption: "
            if isinstance(e, IndexError):
                error_message += "Something is wrong with data padding:\n\tline: %s" % line
                log_error(e, error_message)
                create_line_error_db_entry(LineEncryptionError.PADDING_ERROR)
                error_types.append(LineEncryptionError.PADDING_ERROR)
                bad_lines.append(line)
                continue

            if isinstance(e, TypeError) and decrypted_key is None:
                error_message += "The key was empty:\n\tline: %s" % line
                log_error(e, error_message)
                create_line_error_db_entry(LineEncryptionError.EMPTY_KEY)
                error_types.append(LineEncryptionError.EMPTY_KEY)
                bad_lines.append(line)
                continue

            ################### skip these errors ##############################
            if "unpack" in e.message:
                error_message += "malformed line of config, dropping it and continuing."
                log_error(e, error_message)
                create_line_error_db_entry(LineEncryptionError.MALFORMED_CONFIG)
                error_types.append(LineEncryptionError.MALFORMED_CONFIG)
                bad_lines.append(line)
                #the config is not colon separated correctly, this is a single
                # line error, we can just drop it.
                # implies an interrupted write operation (or read)
                continue
                
            if "Input strings must be a multiple of 16 in length" in e.message:
                error_message += "Line was of incorrect length, dropping it and continuing."
                log_error(e, error_message)
                create_line_error_db_entry(LineEncryptionError.INVALID_LENGTH)
                error_types.append(LineEncryptionError.INVALID_LENGTH)
                bad_lines.append(line)
                continue
                
            if isinstance(e, InvalidData):
                error_message += "Line contained no data, skipping: " + str(line)
                log_error(e, error_message)
                create_line_error_db_entry(LineEncryptionError.LINE_EMPTY)
                error_types.append(LineEncryptionError.LINE_EMPTY)
                bad_lines.append(line)
                continue
                
            if isinstance(e, InvalidIV):
                error_message += "Line contained no iv, skipping: " + str(line)
                log_error(e, error_message)
                create_line_error_db_entry(LineEncryptionError.IV_MISSING)
                error_types.append(LineEncryptionError.IV_MISSING)
                bad_lines.append(line)
                continue
                
            ##################### flip out on these errors #####################
            if 'AES key' in e.message:
                error_message += "AES key has bad length."
                create_line_error_db_entry(LineEncryptionError.AES_KEY_BAD_LENGTH)
                error_types.append(LineEncryptionError.AES_KEY_BAD_LENGTH)
                bad_lines.append(line)
            elif 'IV must be' in e.message:
                error_message += "iv has bad length."
                create_line_error_db_entry(LineEncryptionError.IV_BAD_LENGTH)
                error_types.append(LineEncryptionError.IV_BAD_LENGTH)
                bad_lines.append(line)
            elif 'Incorrect padding' in e.message:
                error_message += "base64 padding error, config is truncated."
                create_line_error_db_entry(LineEncryptionError.MP4_PADDING)
                error_types.append(LineEncryptionError.MP4_PADDING)
                bad_lines.append(line)
                # this is only seen in mp4 files. possibilities:
                #  upload during write operation.
                #  broken base64 conversion in the app
                #  some unanticipated error in the file upload
            else:
                raise #If none of the above errors happened, raise the error.
            raise HandledError(error_message)
            # if any of them did happen, raise a HandledError to cease execution.
    
    if error_count:
        EncryptionErrorMetadata.objects.create(
            file_name=request.values['file_name'],
            total_lines=len(file_data),
            number_errors=error_count,
            errors_lines=json.dumps(bad_lines),
            error_types=json.dumps(error_types),
        )
        
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
        print("length iv: %s, length data: %s, length key: %s" % (len_iv, len_data, len_key))
        print('%s %s %s' % (patient_id, key, data))
        raise
    return remove_PKCS5_padding( decrypted )

################################################################################

def remove_PKCS5_padding(data):
    """ Unpacks encrypted config from the device that was encypted using the
        PKCS5 padding scheme (which is the ordinal value of the last byte). """
    #This can raise an indexerror when data is empty, but that is not expected behavior.
    return  data[0: -ord( data[-1] ) ]
