
""" okay, so, the private key is stored serverside (on S3), and the public
    key is sent to the android device.
    decryption is line by line, current method of separating data is by
    encoding the binary data as hex
    
    Server: private
    Device: public  """



################################################################################
################################# RSA ##########################################
################################################################################

from Crypto.PublicKey import RSA

def generate_key_pairing():
    private = RSA.generate(2048)
    """ Value is the bit-length of the keys to be generated, must be a multiple of 256"""
    
    public = private.publickey()
#     private_key_string = private.exportKey()
#     public_key_string = public.exportKey()
    return public.exportKey(), private.exportKey()
    
    
#TODO: change this to something that grabs the key from an s3 user bucket
def get_private_key(file_name):
    with open("file_name", 'r') as f:
        return RSA.importKey( f.read() )
        
    
def encrypt_rsa(blob, private_key):
    """ This function is never intended to be used. """
    return private_key.encrypt("blob of text", "literally anything")
    """ 'blob of text' can be either a long or a string, we will use strings.
        The second parameter must be entered... but it is ignored.  Really.  """
    
def decrypt_rsa(blob, public_key):
    return public_key.decrypt( blob )
    
    

def prepare_X509_key_for_java( exported_key ):
    # it may be a PKCS8 Key specification?  not entirely sure.
    """ Removes all extraneous data (new lines and labels from a formatted key
        string, because this is how Java likes its key files to be formatted. """
    return "".join(exported_key.split('\n')[1:-2])



################################################################################
################################# AES ##########################################
################################################################################

""" We are using AES in CFB mode because we do not have a [good-and-simple] way
    of enforcing separate storage of initialization vectors from keys or files. """

from Crypto.Cipher import AES
from utils.secure import ENCRYPTION_KEY

def encrypt_aes(input_string):
    return AES.new(ENCRYPTION_KEY, AES.MODE_CFB).encrypt( input_string )
    
def decrypt_aes(input_string):
    return AES.new( ENCRYPTION_KEY, AES.MODE_CFB).decrypt( input_string )