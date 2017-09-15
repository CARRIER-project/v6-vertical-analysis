# -*- coding: utf-8 -*-
"""
Created on 4 jul 2017 12:31:39 CEST

@author: BMMN

Salsa20 256 PyNaCl
"""

from __future__ import print_function  # make print python3 compatible

import gc  # garbage collector
import nacl.secret
import nacl.utils
import nacl.encoding
from .Key import Key
from .sha512 import hash512
from .utilities import _get_password


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
                encoder=nacl.encoding.Base64Encoder).decode("utf-8")

    def decrypt(self, encrypted):
        return self.box.decrypt(encrypted,
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
            encrypted_key_base64 = f.readline().rstrip()
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
                nacl.encoding.Base64Encoder.decode(hash512(user_password))[:32]
        storage_key = Salsa20Key(storage_password)
        symmetric_cipher = Salsa20(storage_key)
        decrypted_key_base64 = symmetric_cipher.decrypt(encrypted_key_base64)
        decrypted_key = nacl.encoding.Base64Encoder.decode(decrypted_key_base64)
        return Salsa20Key(bytearray(decrypted_key))
