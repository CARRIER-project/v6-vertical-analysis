#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 4 jul 2017 12:31:39 CEST

@author: BMMN
"""

from __future__ import print_function  # make print python3 compatible

import base64
import gc  # garbage collector
from Crypto import Random
from Crypto.Cipher import AES


class AES256Cipher(object):

    def __init__(self, key):
        if len(key) != 32:  # allow only the most secure key length
            raise ValueError('AES Key must be 32 bytes long.')
        self.block_size = AES.block_size
        self.key = key

    def encrypt(self, raw, iv):
        raw = self.pad(raw, self.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:self.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self.unpad(cipher.decrypt(enc[self.block_size:])).decode('utf-8')

    @staticmethod
    def pad(s, block_size):  # using PKCS#7 style padding
        return s + (block_size - len(s) % block_size) \
                * chr(block_size - len(s) % block_size)

    @staticmethod
    def unpad(s):  # using PKCS#7 style padding
        return s[:-ord(s[len(s)-1:])]

if __name__ == "__main__":
# This in an example. In production, you would want to read the key from an
# external file or the command line. The key must be 32 bytes long.

# DON'T DO THIS IN PRODUCTION!
    key = b'Thirtytwo byte key, this is long'

# In production, you would want to have a hardware random number generator
# for this.
    initialization_vector = Random.new().read(AES.block_size)

    message = 'This is my message.'
    print("message  : " + message)
    my_cipher = AES256Cipher(key)

# encryption
    my_encrypted_message = my_cipher.encrypt(message, initialization_vector)
    print("encrypted: " + my_encrypted_message)

# decryption
    mydec = my_cipher.decrypt(my_encrypted_message)
    print("decrypted: " + mydec)

# make sure all memory is flushed after operations
    del key
    del message
    del mydec
    gc.collect()
