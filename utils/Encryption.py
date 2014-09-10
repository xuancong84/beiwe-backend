
""" okay, so, the private key is stored serverside (on S3), and the public
    key is sent to the android device.
    decryption is line by line, current method of separating data is by
    encoding the binary data as hex
    
    Server: private
    Device: public  """


#public-private
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


# symmetric

# initialization_vector = Random.new().read(AES.block_size)
# symmetric_cipher = AES.new(aes_key, AES.MODE_CTC, initialization_vector)
#
# encrypting_string = b"Attack at dawn"
# length = 16 - (len(data) % 16)
# data += chr(length)*length
#
# msg = initialization_vector + symmetric_cipher.encrypt(data)
# and when reading data strip bytes
from Crypto.Cipher import AES
from Crypto import Random
from utils.secure import ENCRYPTION_IV, ENCRYPTION_KEY

def encrypt_aes(input_string):
    #TODO: update this comment, we are just asking for an iv in secure.py
    """ W/regards the iv: we can could store the iv along with the rest of the
        patient's data either per-patient or per-file, but this makes the "secret"
        iv totally pointless.  We can store the iv in a separate location/database,
        this is complicated (user must set up a second database), but the most secure.
        We could use the same iv for everything, require that it be provided
        at the same as the key, and prepend random noise to the beginning of all
        files we encrypt, and then ignore it later.  This is better than using no
        iv or a static iv without prepended noise. """
        #we could do a hash of the password?
    
    #TODO: test and research if we need this to be called every single time we
    # make the encrypt call, or if we can call it once as a global variable.
    symmetric_cipher = AES.new(ENCRYPTION_KEY, AES.MODE_CBC, ENCRYPTION_IV)
    
    # In order to use CBC we need to make sure the data to be encrypted is a
    # multiple of the block size.  We generate a random string that satisfies this
    # length requirement, and then insert a new line so we can separate the data
    # out it upon decryption.  We do need to make sure there are not new line
    # chars in this prepended data.
    
    random_padding = Random.new().read(AES.block_size + (len(input_string) % AES.block_size) - 1  )
    while '\n' in random_padding:
        random_padding = Random.new().read(AES.block_size + (len(input_string) % AES.block_size) - 1  )
    random_padding += '\n'
    
    output = symmetric_cipher.encrypt( random_padding + input_string )
    return output
    
    
def decrypt_aes(input_string):
    symmetric_cipher = AES.new( ENCRYPTION_KEY, AES.MODE_CBC, ENCRYPTION_IV )
    try:
        return symmetric_cipher.decrypt(input_string).split("\n", 1)[1]
    except IndexError:
        #TODO: log that an error occurred, either an error in the decryption resulting
        # in nonsense, or the data was empty.
        raise
    
    