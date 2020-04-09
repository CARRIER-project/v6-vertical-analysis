# -*- coding: utf-8 -*-
""" Diffie Hellman pubkey encryption cipher.

Will be vulnerable against quantum computing attacks. Wrapper around Curve25519
encryption from the PyNaCl package.

class DiffieHellman provides a cipher object for en- and decryption. Without
instantiation you can use key_gen() to generate keys.

classes DiffieHellmanSecretKey and DiffieHellmanPublicKey provide key objects.
The raw keys can be found in KEYNAME.key. Without instantiation,
calling import_key() reads a keyfile and returns a key object.
"""

from __future__ import print_function  # make print python3 compatible

import nacl.utils
import nacl.public
import nacl.encoding
from .salsa20 import Salsa20, Salsa20Key
from .utilities import _get_password, repeat_import_export
from .sha512 import hash512
from .Key import _Key

secret_key_name = "SECRET_Diffie_Hellman_Classic_Asymmetric_Decryption_Key"
secret_key_description = secret_key_name + " for DH pubkey encryption"

public_key_name = "Public_Diffie_Hellman_Classic_Asymmetric_Encryption_Key"
public_key_description = public_key_name +  " for DH pubkey encryption"


class DiffieHellman(object):
    """ Cipher object for en- and decryption.

    Attributes:
        secret_key: The raw secret key for encryption.
        public_key: The raw public key for decryption.

    Methods:
        encrypt: Encrypt plaintext with a Diffie Hellman pubkey cipher.
        decrypt: Encrypt ciphertext with a Diffie Hellman pubkey cipher.
        key_gen: Generate a tuple of key objects, containing a Diffie Hellman
                 secret key and public key. Can be called without
                 instantiation.
    """
    def __init__(self, secret_key, public_key):
        self.secret_key = secret_key
        self.public_key = public_key
        self.crypto_box = nacl.public.Box(secret_key.key, public_key.key)

    @staticmethod
    def key_gen():
        """Key-pair generation for Diffie-Hellman Curve25519 public key
           encryption.

        Args:
            --
        Returns:
            private_key object, public_key object
        """
        secret_key = nacl.public.PrivateKey.generate()
        public_key = secret_key.public_key
        return DiffieHellmanSecretKey(secret_key), \
                DiffieHellmanPublicKey(public_key)

    def encrypt(self, message_unencoded):
        """ Encrypts cleartext with a Diffie Hellman cipher.

        Args:
            message_unencoded: Plain text string.

        Returns:
            Base64 encoded ciphertext.
        """
        message = message_unencoded.encode("utf-8")
        nonce = nacl.utils.random(nacl.public.Box.NONCE_SIZE)
        encrypted = self.crypto_box.encrypt(message, nonce)
        return nacl.encoding.Base64Encoder.encode(encrypted).decode("utf-8")

    def decrypt(self, encrypted_message_base64):
        """ Decrypts ciphertext with a Diffie Hellman cipher.

        Args:
            encrypted_message_base64: Base64 encoded ciphertext.

        Returns:
            Cleartext message string.

        Raises:
            nacl.exceptions.CryptoError if decryption fails.
        """
        encrypted_message = nacl.encoding.Base64Encoder.decode(
                encrypted_message_base64)
        return self.crypto_box.decrypt(encrypted_message).decode("utf-8")

class _DiffieHellmanKey(_Key):
    def __init__(self, key, key_name, key_description):
        super(_DiffieHellmanKey, self).__init__(key, key_name, key_description)
        self.key_length = len(bytes(self.key))

    def _is_valid(self):
        if not len(bytes(self.key)) == 32:
            return False
        if not (isinstance(self.key, nacl.public.PrivateKey)
                or isinstance(self.key, nacl.public.PublicKey)):
            return False
        return True

class DiffieHellmanSecretKey(_DiffieHellmanKey):
    """ Secret key object for decryption.

    Attributes:
        key: The raw secret key.
        name: The key name.
        description: Verbose description of key type.
        header: Header for exporting to a file, also contains the description.
        footer: Footer for exporting to a file.
        security_level: String, "SECRET" if encrypted storage is needed,
                        "Private" if not.
        public_key: The public key that belongs to the secret key.

    Methods:
        export_key: Export the raw key to a key file.
        import _key: Creates a key object from the content of a key file. Can
                     be called without instantiation.
        _check_length: Verify the length of the raw key.
        _is_valid: Self check for validity.
    """
    def __init__(self, key):
        super(DiffieHellmanSecretKey, self).__init__(key, secret_key_name,
                secret_key_description)
        self.security_level = "SECRET"
        self.public_key = DiffieHellmanPublicKey(self.key.public_key)

    @staticmethod
    @repeat_import_export
    def import_key(file_name_with_path, silent=False):
        """ Creates a secret key object from a key file.

        Attributes:
            file_name_with_path: Key_file.
            silent: Don't print password requirements if set True.

        Returns:
            DiffieHellmanSecretKey object.

        Raises:
            IOError: When opening a wrong file.
            TypeError: When key in file is invalid.
            ValueError: When decryption passwords do not match requirements.
            nacl.exceptions.CryptoError: When key decryption fails.
        """
        with open(file_name_with_path) as f:
            header = f.readline().rstrip()
            encrypted_key_base64 = f.readline().rstrip()
            footer = f.readline().rstrip()
        if not secret_key_description in header:
            raise TypeError("Key is not a Diffie Hellman SECRET key.")
        if not footer == _Key.footer:
            raise TypeError("Key is not a valid key.")
        if silent:
            user_password = _get_password(validate=False,
                    print_requirements=False)
        else:
            user_password = _get_password(validate=False)
        storage_password = \
                nacl.encoding.Base64Encoder.decode(hash512(user_password))[:32]
        storage_key = Salsa20Key(storage_password)
        symmetric_cipher = Salsa20(storage_key)
        decrypted_key_base64 = symmetric_cipher.decrypt(encrypted_key_base64)
        decrypted_key = nacl.encoding.Base64Encoder.decode(decrypted_key_base64)
        return DiffieHellmanSecretKey(nacl.public.PrivateKey(decrypted_key))

class DiffieHellmanPublicKey(_DiffieHellmanKey):
    """ Public key object for decryption.

    Attributes:
        key: The raw public key.
        name: The key name.
        description: Verbose description of key type.
        header: Header for exporting to a file, also contains the description.
        footer: Footer for exporting to a file.
        security_level: String, "SECRET" if encrypted storage is needed,
                        "Private" if not.

    Methods:
        export_key: Export the raw key to a key file.
        import _key: Creates a key object from the content of a key file. Can
                     be called without instantiation.
        _check_length: Verify the length of the raw key.
        _is_valid: Self check for validity.
    """
    def __init__(self, key):
        super(DiffieHellmanPublicKey, self).__init__(key, public_key_name,
                public_key_description)
        self.security_level = "Public"

    @staticmethod
    def import_key(file_name_with_path, silent=False):
        """ Creates a public key object from a key file.

        Attributes:
            file_name_with_path: Key_file.
            silent: Don't print password requirements if set True.

        Returns:
            DiffieHellmanSecretKey object.

        Raises:
            IOError: When opening a wrong file.
            TypeError: When key in file is invalid.
        """
        with open(file_name_with_path) as f:
            header = f.readline().rstrip()
            key_base64 = f.readline().rstrip()
            footer = f.readline().rstrip()
        if not public_key_description in header:
            raise IOError("Key is not a Diffie Hellman Public key.")
        if not footer == _Key.footer:
            raise IOError("Key is not a valid key.")
        key = nacl.encoding.Base64Encoder.decode(key_base64)
        return DiffieHellmanPublicKey(nacl.public.PublicKey(key))
