#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 4 jul 2017 12:31:39 CEST

@author: BMMN
"""

from __future__ import print_function  # make print python3 compatible

#import base64
import nacl.encoding
import gc  # garbage collector
from Crypto import Random
from Crypto.Cipher import AES
from .Key import Key
from .sha512 import hash512
from .salsa20 import Salsa20, Salsa20Key
from .utilities import _get_password

key_length = 32
key_name = "SECRET_AES_256_Key"
key_description = key_name + " for AES 256 symmetric block encryption"

class AES256(object):
    def __init__(self, key_object):
        key = bytes(key_object.key)
        self.block_size = AES.block_size
        self.key = key

    def encrypt(self, raw):
        initialization_vector = Random.new().read(AES.block_size)
        raw = self.pad(raw, self.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, initialization_vector)
        return nacl.encoding.Base64Encoder.encode(
                initialization_vector + cipher.encrypt(raw)).decode("utf-8")

    def decrypt(self, enc):
        enc = nacl.encoding.Base64Encoder.decode(enc)
        initialization_vector = enc[:self.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, initialization_vector)
        return self.unpad(cipher.decrypt(enc[self.block_size:])).decode('utf-8')

    @staticmethod
    def pad(s, block_size):  # using PKCS#7 style padding
        return s + (block_size - len(s) % block_size) \
                * chr(block_size - len(s) % block_size)

    @staticmethod
    def unpad(s):  # using PKCS#7 style padding
        return s[:-ord(s[len(s)-1:])]

    @staticmethod
    def key_gen(size=32):
        """ Key generation for symmetric AES 256 encryption.

        Args:
            size (int): size/length of the key
        Returns:
            symmetric key object
        """
        key = Random.new().read(size)
        return AES256Key(bytearray(key))

class AES256Key(Key):
    def __init__(self, key):
        super(AES256Key, self).__init__(key, key_name, key_description)
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
            raise IOError("Key is not a AES 256 symmetric key.")
        if not footer == Key.footer:
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
        decrypted_key = nacl.encoding.Base64Encoder.decode(
                decrypted_key_base64)
        return AES256Key(bytearray(decrypted_key))


#def encrypt(message, key):
#    """ Symmetric AES 256 encryption.
#
#    Args:
#        message (string): message to be encrypted
#        key (string): symmetric key
#    Returns:
#        base64-encoded cipher in unicode
#    """
#    # In production, you would want to have a hardware random number generator
#    # for initialization_vector-generation.
#    initialization_vector = Random.new().read(AES.block_size)
#    my_cipher = AES256Cipher(key)
#    return my_cipher.encrypt(message, initialization_vector).decode("utf-8")
#
#def decrypt(encrypted_message, key):
#    """ Symmetric AES 256 decryption.
#
#    Args:
#        encrypted_message (string): base64-encoded cypher text
#        key (bytes): symmetric key
#    Returns:
#        base64-encoded clear text message
#    """
#    my_cipher = AES256Cipher(key)
#    return my_cipher.decrypt(encrypted_message)

if __name__ == "__main__":
    # This in an example. In production, you would want to read the key from an
    # external file or the command line. The key must be 32 bytes long.

    # DON'T DO THIS IN PRODUCTION!
    key = key_gen()

    message = 'This is my message.'
    print("message  : " + message)

    my_encrypted_message = encrypt(message, key)
    print("encrypted: " + my_encrypted_message)

    mydec = decrypt(my_encrypted_message, key)
    print("decrypted: " + mydec)

    # make sure all memory is flushed after operations
    del key
    del message
    del mydec
    gc.collect()
