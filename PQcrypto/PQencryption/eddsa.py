# -*- coding: utf-8 -*-
"""
Created on Mon Jul 10 16:26:41 CEST 2017

@author: BMMN

signing Curve 25519 PyNaCl
"""

from __future__ import print_function  # make print python3 compatible

import nacl.signing
import nacl.encoding
from .salsa20 import Salsa20, Salsa20Key
from .utilities import _get_password
from .sha512 import hash512
from .Key import Key

secret_key_name = "SECRET_EdDSA_Key"
secret_key_description = secret_key_name + " for EdDSA asymmetric signing"

public_key_name = "Public_EdDSA_Key"
public_key_description = public_key_name + " for EdDSA asymmetric signing"


class EdDSA(object):
    def __init__(self, key):
        self.key = key

    def sign(self, message):
        if isinstance(self.key.key, nacl.signing.SigningKey):
            signed = self.key.key.sign(bytes(message.encode("utf-8")))
            return nacl.encoding.Base64Encoder.encode(signed).decode("utf-8")
        else:
            raise TypeError("Key is no EdDSA SigningKey")

    def verify(self, signed_message_base64):
        if isinstance(self.key.key, nacl.signing.VerifyKey):
            signed_message = nacl.encoding.Base64Encoder.decode(
                    signed_message_base64)
#            verify_key = nacl.signing.VerifyKey(self.key,
#                    encoder=nacl.encoding.Base64Encoder)
            return self.key.key.verify(signed_message).decode("utf-8")
        else:
            raise TypeError("Key is no EdDSA VerifyKey")

    @staticmethod
    def key_gen():
        signing_key = nacl.signing.SigningKey.generate()
        verify_key = signing_key.verify_key
        return EdDSASigningKey(signing_key), EdDSAVerifyKey(verify_key)

class EdDSAKey(Key):
    def __init__(self, key, key_name, key_description):
        super(EdDSAKey, self).__init__(key, key_name, key_description)
        self.key_length = len(bytes(self.key))

    def _is_valid(self):
        if not len(bytes(self.key)) == 32:
            return False
        if not (isinstance(self.key, nacl.signing.SigningKey)
                or isinstance(self.key, nacl.signing.VerifyKey)):
            return False
        return True

class EdDSASigningKey(EdDSAKey):
    def __init__(self, key):
        super(EdDSASigningKey, self).__init__(key, secret_key_name,
                secret_key_description)
        self.security_level = "SECRET"
        self.verify_key = EdDSAVerifyKey(self.key.verify_key)

    @staticmethod
    def import_key(file_name_with_path, silent=False):
        with open(file_name_with_path) as f:
            header = f.readline().rstrip()
            encrypted_key_base64 = f.readline().rstrip()
            footer = f.readline().rstrip()
        if not secret_key_description in header:
            raise IOError("Key is not a EdDSA SECRET key.")
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
        return EdDSASigningKey(nacl.signing.SigningKey(decrypted_key))

class EdDSAVerifyKey(EdDSAKey):
    def __init__(self, key):
        super(EdDSAVerifyKey, self).__init__(key, public_key_name,
                public_key_description)
        self.security_level = "Public"

    @staticmethod
    def import_key(file_name_with_path, silent=False):
        with open(file_name_with_path) as f:
            header = f.readline().rstrip()
            key_base64 = f.readline().rstrip()
            footer = f.readline().rstrip()
        if not public_key_description in header:
            raise IOError("Key is not a EdDSA Public key.")
        if not footer == Key.footer:
            raise IOError("Key is not a valid key.")
        key = nacl.encoding.Base64Encoder.decode(key_base64)
        return EdDSAVerifyKey(nacl.signing.VerifyKey(key))
