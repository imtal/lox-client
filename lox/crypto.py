'''
Description:

    Module containing helper class for encryption of files

Please note:

    (1) The files are AES encrypted
    (2) For that reason, the file is aligned (padded) to a block size of 16
    (3) The original file length is not stored, so decryption leaves a padded file (!)
    (4) The initialization vector is stored with the key (!) and not in the file
    (5) The key and initialization vector are PGP encrypted
    (6) PGP public and private (!) key are stored ascii armoured (but not PEM) on the server
    (7) PGP keys are not signed
    (8) PGP keys and AES keys are stored base64 on the server, module base64 is used
    (9) The ~/.lox directory is used for the keyring, named after the session
    (A) There is one keyring per session (account) so there is also one private key per account
    (B) The iOS and Android apps (with BouncyCastle libraries) use  a special padding technique, read comments

'''

import os
import base64
from Crypto.Cipher import AES
from Crypto import Random
import gnupg
import lox.config as config
from lox.api import LoxApi
import lox.gui


class LoxKey:
    '''
    The other Localbox apps see the key and iv together s a key
    '''
    def __init__(self, key=None, iv=None):
        self.key = key
        self.iv = iv


class LoxKeyring:
    '''
    The LoxKeyring uses GPG to store its keys. On initializing
    the object only the GPG object is created. Loading of
    keys is deferred to the moment when really needed.

    Use a LoxKeyring per account, so a different private key is
    generated for each session in order to not mix up session
    security.
    '''

    def __init__(self, session):
        '''
        This class uses a GPG object
        '''
        keyring = ".{}.pub".format(session)
        secret_keyring = ".{}.sec".format(session)
        self.session = session
        self._passphrase = None
        self._conf_dir = os.environ['HOME']+'/.lox'
        # always force restricted access to config dir
        os.chmod(self._conf_dir, 0700)
        # open a GPG keyring
        self._gpg = gnupg.GPG(
                            gnupghome=self._conf_dir,
                            keyring=keyring,
                            secret_keyring=secret_keyring,
                            verbose=False,
                            options=['--allow-non-selfsigned-uid']
                        )
        self._gpg.encoding = 'utf-8'
        self._id = config.settings[session]['username']
        self._open = False

    def open(self):
        '''
        Opening the keyring is done apart from creating the instance
        because when using unencrypted folders only it is not nescessary
        to open the keyring.

        When the keyring is opened there is a check if there is already
        a remote (private) key available. If so and there is not yet a local key the
        remote key is copied. If not a local key is generated and uploaded. If there
        are keys in both places the keys are compared, when different an error is
        raised because this situation needs special attention. When there is no
        network connection, no keys are generated and encryption cannot be done.

        '''
        if not self._open:
            api = LoxApi(self.session)
            user_info = api.get_user_info()
            # check if private key exists
            if not user_info[u'private_key']:
                print "LoxKeyring: no remote private key"
                # remote private key not set
                if not self._gpg.list_keys():
                    print "LoxKeyring: generating new private key"
                    input_data = self._gpg.gen_key_input(
                                        key_type='RSA',
                                        key_length=2048,
                                        passphrase=config.passphrase(),
                                        name_email=self._id,
                                        name_comment='Localbox user',
                                        name_real='Anonymous'
                                    )
                    self._gpg.gen_key(input_data)
                else:
                    print "LoxKeyring: remote private key dropped while local one not?"
                private_key = self._gpg.export_keys(self._id, True)
                public_key = self._gpg.export_keys(self._id)
                print "LoxKeyring: uploading my keys"
                self.api.set_user_info(binascii.b2a_base64(public_key), binascii.b2a_base64(private_key))
                self._privkey = private_key
            else:
                if not self._gpg.list_keys(True):
                    print "LoxKeyring: downloading remote private key"
                    public_key = base64.b64decode(user_info[u'public_key'])
                    import_result = self._gpg.import_keys(public_key)
                    #assert (import_result.count==1)
                    print import_result.count
                    private_key = base64.b64decode(user_info[u'private_key'])
                    import_result = self._gpg.import_keys(private_key)
                    #assert (import_result.count==1)
                    print import_result.count
                    self._privkey = private_key
                else:
                    print "LoxKeyring: checking local and remote private keys,",
                    # extreme workaround to compare keys, due to not using PEM format in other apps
                    my_key = self._gpg.export_keys(self._id, True, armor=True, minimal=True)
                    server_key = user_info[u'private_key']
                    my_flattened_key = ''
                    lines = my_key.splitlines()
                    n = len(lines) - 2
                    for i in range(3, n):
                        my_flattened_key += lines[i]
                    if not my_flattened_key == server_key:
                        print "they are different"
                    else:
                        print "they are the same"
                    self._privkey = my_flattened_key
            self._open = True

    def set_private(self, key):
        '''
        Import a localbox key in the keyring
        '''
        self._gpg.import_keys(key)

    def gpg_decrypt(self, string):
        '''
        Base64 decode
        PGP decrypt a string (usually the AES key)
        '''
        assert(self._open)
        ciphertext = base64.b64decode(string)
        plaintext = self._gpg.decrypt(ciphertext, passphrase=config.passphrase())
        return plaintext

    def gpg_encrypt(self, string, recipients=None):
        '''
        PGP encrypt a string (usually the AES key)
        then base64 encode
        '''
        assert(self._open)
        ciphertext = self._gpg.encrypt(string, recipients=self._id,
                                        passphrase=config.passphrase(),
                                        armor=False, always_trust=True)
        encoded = base64.b64encode(str(ciphertext))
        return encoded

    def gpg_list(self):
        '''
        List (private) keys in keyring
        '''
        assert(self._open)
        self._gpg.list_keys(True)

    def _aes_pad(self, filename):
        '''
        Pad file a to a 16 byte block length,
        needed for an omission at this moment:
        the original file length is not stored
        '''
        size = os.path.getsize(filename)
        if (size % 16) > 0:
            with open(filename, 'a') as outfile:
                # The iOS and Android apps upad with a character that
                # is the same as the amount of padding characters.
                # Using only a space or NULL character gives as problem
                # that documents do not show in apps.
                n = (16 - (size % 16))
                chunk = chr(n) * n
                outfile.write(chunk)

    def _aes_encrypt(self, key, iv, filename_in, filename_out, chunksize=64*1024):
        '''
        Encrypt a file with AES to another file,
        use function to decrypt from original file to temp file
        Note: initialization vector and original size are not stored
        '''
        cipher = AES.new(key, AES.MODE_CBC, iv)
        with open(filename_in, 'rb') as infile:
            with open(filename_out, 'wb') as outfile:
                #outfile.write(struct.pack('<Q', filesize))
                #outfile.write(iv)
                while True:
                    chunk = infile.read(chunksize)
                    if len(chunk) == 0:
                        break
                    elif len(chunk) % 16 != 0:
                        # The iOS and Android apps upad with a character that
                        # is the same as the amount of padding characters.
                        # Using only a space or NULL character gives as problem
                        # that documents do not show in apps.
                        n = (16 - len(chunk) % 16)
                        chunk += chr(n) * n
                    outfile.write(cipher.encrypt(chunk))

    def _aes_decrypt(self, key, iv, filename_in, filename_out, chunksize=64*1024):
        '''
        Decrypt a file with AES to another file,
        Note: initialization vector and original size are not stored
        '''
        with open(filename_in, 'rb') as infile:
            #origsize = struct.unpack('<Q', infile.read(struct.calcsize('Q')))[0]
            #iv = infile.read(16)
            cipher = AES.new(key, AES.MODE_CBC, iv)
            with open(filename_out, 'wb') as outfile:
                while True:
                    chunk = infile.read(chunksize)
                    if len(chunk) == 0:
                        break
                    outfile.write(cipher.decrypt(chunk))
                #outfile.truncate(origsize)

    def new_key(self):
        '''
        Get a new AES key and iv, localbox uses a self generated iv
        '''
        key = Random.new().read(AES.key_size[2])
        iv = Random.new().read(AES.block_size)
        return LoxKey(key, iv)

    def get_key(self, path):
        '''
        Get the AES key from the server and decrypt it using PGP
        '''
        self.open()
        assert(self._open)
        api = LoxApi(self.session)
        aes = api.get_key(path)
        encrypted_iv = aes[u'iv']
        encrypted_key = aes[u'key']
        key = str(self.gpg_decrypt(encrypted_key))
        iv = str(self.gpg_decrypt(encrypted_iv))
        return LoxKey(key, iv)

    def decrypt(self, lox_key, filename_in, filename_out):
        '''
        Use this function to decrypt from temp file to final file,
        it does all checks, i.e if the KeyRing is open.
        '''
        assert(isinstance(lox_key, LoxKey))
        self._aes_decrypt(lox_key.key, lox_key.iv, filename_in, filename_out)

    def encrypt(self, lox_key, filename_in, filename_out):
        '''
        Use this function to decrypt from temp file to final file,
        it does all checks, i.e if the KeyRing is open.
        '''
        assert(isinstance(lox_key, LoxKey))
        self._aes_pad(filename_in)
        self._aes_encrypt(lox_key.key, lox_key.iv, filename_in, filename_out)

def zerome(string):
    '''
    Helper function to erase string from memory,
    use in case i.e. a password string needs to be cleared.
    Please note that after multiple assignments multiple copies
    are stored in memory due to the non mutable state of
    objects ...
    '''
    # find the header size with a dummy string
    temp = "finding offset"
    header = ctypes.string_at(id(temp), sys.getsizeof(temp).find(temp))
    location = id(string) + header
    size = sys.getsizeof(string) - header
    memset = ctypes.CDLL("libc.so.6").memset
    # Windows: memset = ctypes.cdll.msvcrt.memset
    memset(location, 0, size)


