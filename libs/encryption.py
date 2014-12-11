""" The private keys are stored server-side (S3), and the public key is sent to
    the android device. """


################################################################################
################################# RSA ##########################################
################################################################################
from Crypto.PublicKey import RSA
from data.constants import ASYMMETRIC_KEY_LENGTH

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
from Crypto.Cipher import AES
from data.passwords import ENCRYPTION_KEY
from security import decode_base64
from os import urandom

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

###############################################################################

def decrypt_device_file(patient_id, data, private_key):
    """ Runs the line-by-line decryption of a file encrypted by a device. """
    #we are relying on a quirk? in the split function, which only strips empty
    # entries if no argument is supplied.
    return "\n".join( [ decrypt_device_line(patient_id, line, private_key) for line in data.split() ] )


# provide a key by running get_client_private_key(patient_id)
def decrypt_device_line(patient_id, data, private_key):
    """ data is expected to be 3 colon separated values.
        value 1 is the symmetric key, encrypted with the patient's public key.
        value 2 is the initialization vector for the AES CBC cipher.
        value 3 is the data, encrypted using AES CBC, with the provided key and iv. """
        
    try:
        try:
            symmetric_key, iv, data = data.split(":")
        except Exception as e1:
            print "malformed line, could not split, this dump could be big..."
            print data
            raise e1
        
        iv = decode_base64( iv.encode( "utf-8" ) )
        data = decode_base64( data.encode( "utf-8" ) )
        symmetric_key = private_key.decrypt( decode_base64( symmetric_key.encode( "utf-8" ) ) )
        decrypted = AES.new(symmetric_key, mode=AES.MODE_CBC, IV=iv).decrypt( data )
    except Exception as e2:
        if "unpack" in e2.message: raise e2
        print "an error occurred in decryption"
        print "iv length", len(iv)
        print 'iv', iv
        print "symmetric_key length", len(symmetric_key)
        print "symmetric key", symmetric_key
        print "data length:", len(data)
        print "start of data:", data[:4096]
        print "end of data:", data[-256:]
        raise e2
    
    return remove_PKCS5_padding( decrypted )


def remove_PKCS5_padding(data):
    """ Unpacks encrypted data from the device that was encypted using the
        PKCS5 padding scheme (which is the ordinal value of the last byte). """
    return  data[0: -ord( data[-1] ) ]
