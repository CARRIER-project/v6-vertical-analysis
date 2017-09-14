#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 4 jul 2017 12:31:39 CEST

@author: BMMN
"""

from __future__ import print_function  # make print python3 compatible

import gc  # garbage collector
import nacl.secret
import nacl.utils
import nacl.encoding
from .Key import Key
from .sha_512_hashlib import hash512
from ..utilities.utilities import _get_password


key_length = 32
key_name = "SECRET_Salsa20_Key"
key_description = key_name + " for Salsa20 256 symmetric streaming encryption"

class Salsa20(object):
    def __init__(self, key_object):
        key = bytes(key_object.key)
        self.key = key
        self.box = nacl.secret.SecretBox(key)

    def encrypt(self, message_unencoded):
        message = message_unencoded.encode("utf-8")
        nonce = nacl.utils.random(nacl.secret.SecretBox.NONCE_SIZE)
        return self.box.encrypt(message, nonce,
                encoder=nacl.encoding.HexEncoder)

    def decrypt(self, encrypted):
        return self.box.decrypt(encrypted,
                encoder=nacl.encoding.HexEncoder).decode("utf-8")

    @staticmethod
    def key_gen(size=32):
        """ Key generation for symmetric Salsa20 256 encryption.

        Args:
            size (int): size/length of the key
        Returns:
            random bytes of length(size)
        """
        return Salsa20Key(bytearray(nacl.utils.random(size)))

class Salsa20Key(Key):
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
            encrypted_key_hex = f.readline().rstrip()
            footer = f.readline().rstrip()
        if not key_description in header:
            raise IOError("Key is not a Salsa20 symmetric key.")
        if not footer == Key.footer:
            raise IOError("Key is not a valid key.")
        if silent:
            user_password = _get_password(validate=False,
                    print_requirements=False)
        else:
            user_password = _get_password(validate=False)
        storage_password = \
                nacl.encoding.HexEncoder.decode(hash512(user_password))[:32]
        storage_key = Salsa20Key(storage_password)
        symmetric_cipher = Salsa20(storage_key)
        decrypted_key_hex = symmetric_cipher.decrypt(encrypted_key_hex)
        decrypted_key = nacl.encoding.HexEncoder.decode(decrypted_key_hex)
        return Salsa20Key(bytearray(decrypted_key))


#def key_gen(size=32):
#    """ Key generation for symmetric Salsa20 256 encryption.
#
#    Args:
#        size (int): size/length of the key
#    Returns:
#        random bytes of length(size)
#    """
#    return nacl.utils.random(size)

#def encrypt(message_str, key):
#    """ Symmetric Salsa20 256 encryption.
#
#    Args:
#        message (string): message to be encrypted
#        key (string): symmetric key
#    Returns:
#        hex-encoded cypher in unicode
#    """
#    message_bytes = bytes(message_str.encode("utf-8"))
#    my_cipher = Salsa20Cipher(key)
#    return my_cipher.encrypt(message_bytes).decode("utf-8")

#def decrypt(message, key):
#    """ Symmetric Salsa20 256 decryption.
#
#    Args:
#        encrypted_message (string): hex-encoded cypher text
#        key (bytes): symmetric key
#    Returns:
#        hex-encoded clear text message
#    """
#    my_cipher = Salsa20Cipher(key)
#    return my_cipher.decrypt(message).decode("utf-8")

if __name__ == "__main__":
    # This in an example. In production, you would want to read the key from an
    # external file or the command line. The key must be 32 bytes long.

    # DON'T DO THIS IN PRODUCTION!
    key = key_gen()

    message = 'This is my message.'
    print("message:  " + message)

    my_encrypted_message = encrypt(message, key)
    print("encrypted: " + my_encrypted_message)

    my_decrypted_message = decrypt(my_encrypted_message, key)
    print("decrypted: " + my_decrypted_message)

    # make sure all memory is flushed after operations
    del key
    #del message
    del my_decrypted_message
    gc.collect()
