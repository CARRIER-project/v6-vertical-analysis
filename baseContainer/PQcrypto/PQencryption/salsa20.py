# -*- coding: utf-8 -*-
""" Salsa20 symmetric streaming encryption cipher.

Uses 256 bits key length for increased security against Grover's algorithm,
thus safe against known quantum computer attacks. Wrapper around Salsa20
encryption from the PyNaCl package.

class Salsa20 provides a cipher object for en- and decryption. Without
instantiation you can use key_gen() to generate keys.

class Salsa20Key provides key objects. The raw key can be found in KEYNAME.key.
Without instantiation, calling import_key() reads a keyfile and returns a key
object.
"""

from __future__ import print_function  # make print python3 compatible

import gc  # garbage collector
import nacl.secret
import nacl.utils
import nacl.encoding
from .Key import _Key
from .sha512 import hash512
from .utilities import _get_password


key_length = 32  # corresponds to 256 bits
key_name = "SECRET_Salsa20_Key"
key_description = key_name + " for Salsa20 256 symmetric streaming encryption"

class Salsa20(object):
    """ Cipher object for signing and verification.

    Attributes:
        key: The raw key.
        box: The box object used for en- and decryption.

    Methods:
        encrypt: Encrypt file content with a Salsa20 cipher.
        decrypt: Decrypt file content with an EdDSA cipher.
        key_gen: Generate a tuple of key objects, containing a EdDSA signing
                 key and verify key. Can be called without instantiation.
    """
    def __init__(self, key_object):
        key = bytes(key_object.key)
        self.key = key
        self.box = nacl.secret.SecretBox(key)

    def encrypt(self, message_unencoded):
        """ Encrypts cleartext with a Salsa20 symmetric cipher.

        Args:
            message_unencoded: Plain text string.

        Returns:
            Base64 encoded ciphertext.
        """
        message = message_unencoded.encode("utf-8")
        nonce = nacl.utils.random(nacl.secret.SecretBox.NONCE_SIZE)
        return self.box.encrypt(message, nonce,
                encoder=nacl.encoding.Base64Encoder).decode("utf-8")

    def decrypt(self, encrypted_message_base64):
        """ Decrypts ciphertext with a Salsa20 symmetric cipher.

        Args:
            encrypted_message_base64: Base64 encoded ciphertext.

        Returns:
            Cleartext message string.
        """
        return self.box.decrypt(encrypted_message_base64,
                encoder=nacl.encoding.Base64Encoder).decode("utf-8")

    @staticmethod
    def key_gen(size=32):
        """ Key generation for symmetric Salsa20 256 encryption.

        Args:
            size (int): size/length of the key
        Returns:
            random bytes of length(size)
        """
        return Salsa20Key(bytearray(nacl.utils.random(size)))

class Salsa20Key(_Key):
    def __init__(self, key):
        super(Salsa20Key, self).__init__(key, key_name, key_description)
        self.key = key
        self.key_length = key_length
        self._check_length(self.key_length)
        self.security_level = "SECRET"

    def _is_valid(self):
        if type(self.key) != bytearray:
            return False
        elif len(self.key) != self.key_length:
            return False
        else:
            return True

    @staticmethod
    def import_key(file_name_with_path, silent=False):
        with open(file_name_with_path) as f:
            header = f.readline().rstrip()
            encrypted_key_base64 = f.readline().rstrip()
            footer = f.readline().rstrip()
        if not key_description in header:
            raise IOError("Key is not a Salsa20 symmetric key.")
        if not footer == _Key.footer:
            raise IOError("Key is not a valid key.")
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
        return Salsa20Key(bytearray(decrypted_key))
