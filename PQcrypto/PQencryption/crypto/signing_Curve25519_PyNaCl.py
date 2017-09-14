#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 10 16:26:41 CEST 2017

@author: BMMN
"""

from __future__ import print_function  # make print python3 compatible

import nacl.signing
import nacl.encoding
from .salsa20_256_PyNaCl import Salsa20, Salsa20Key
from ..utilities.utilities import _get_password
from .sha_512_hashlib import hash512
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
            return nacl.encoding.HexEncoder.encode(signed).decode("utf-8")
        else:
            raise TypeError("Key is no EdDSA SigningKey")

    def verify(self, signed_message_hex):
        if isinstance(self.key.key, nacl.signing.VerifyKey):
            signed_message = nacl.encoding.HexEncoder.decode(
                    signed_message_hex)
#            verify_key = nacl.signing.VerifyKey(self.key,
#                    encoder=nacl.encoding.HexEncoder)
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
            encrypted_key_hex = f.readline().rstrip()
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
                nacl.encoding.HexEncoder.decode(hash512(user_password))[:32]
        storage_key = Salsa20Key(storage_password)
        symmetric_cipher = Salsa20(storage_key)
        decrypted_key_hex = symmetric_cipher.decrypt(encrypted_key_hex)
        decrypted_key = nacl.encoding.HexEncoder.decode(decrypted_key_hex)
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
            key_hex = f.readline().rstrip()
            footer = f.readline().rstrip()
        if not public_key_description in header:
            raise IOError("Key is not a EdDSA Public key.")
        if not footer == Key.footer:
            raise IOError("Key is not a valid key.")
        key = nacl.encoding.HexEncoder.decode(key_hex)
        return EdDSAVerifyKey(nacl.signing.VerifyKey(key))

def sign(message, signing_key):
    signed = signing_key.sign(bytes(message.encode("utf-8")))
    return nacl.encoding.HexEncoder.encode(signed).decode("utf-8")

def verify(signed_message_hex, verify_key_hex):
    signed_message = nacl.encoding.HexEncoder.decode(signed_message_hex)
    verify_key = nacl.signing.VerifyKey(verify_key_hex,
            encoder=nacl.encoding.HexEncoder)
    return verify_key.verify(signed_message).decode("utf-8")

def key_gen():
    signing_key = nacl.signing.SigningKey.generate()
    verify_key = signing_key.verify_key
    return signing_key, verify_key


if __name__ == "__main__":
    import gc  # garbage collector
    # This in an example. In production, you would want to read the key from an
    # external file or the command line. The key must be 32 bytes long.

    # DON'T DO THIS IN PRODUCTION!
    signing_key, verify_key = key_gen()

    message = 'This is my message.'
    print("message  : " + message)

    signed_hex = sign(message, signing_key)
    verify_key_hex = verify_key.encode(encoder=nacl.encoding.HexEncoder).decode("utf-8")
    print("signed: " + signed_hex)
    print("verify_key_hex: " + verify_key_hex)

    print()
    print("verification positive:")
    print(verify(signed_hex, verify_key_hex))
    print()
    print("=====================================")
    print("THE NEXT STEP WILL FAIL, AS EXPECTED!")
    print("=====================================")
    print("verification negative:")
    spoofed_message = "0"*len(signed_hex)
    print(verify(spoofed_message, verify_key_hex))

    # make sure all memory is flushed after operations
    del signing_key
    del verify_key
    del verify_key_hex
    del signed_hex
    del message
    gc.collect()
