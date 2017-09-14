#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on vr 25 aug 2017 17:44:50 CEST

@author: BMMN
"""

from __future__ import print_function  # make print python3 compatible
import os
import ctypes
import nacl.encoding
#import nacl.hash
from .salsa20_256_PyNaCl import Salsa20, Salsa20Key
from ..utilities.utilities import _get_password
from .sha_512_hashlib import hash512
from .Key import Key


secret_key_name = "SECRET_McBits_Key"
secret_key_description = secret_key_name + " for McBits asymmetric quantum-" \
        "computer-safe encryption"

public_key_name = "Public_McBits_Key"
public_key_description = public_key_name + " for McBits asymmetric quantum-" \
        "computer-safe encryption"

library_name = "libmcbits.so"
library_absolute_path = os.path.dirname(os.path.abspath(__file__)) \
        + os.path.sep + library_name
mcbits = ctypes.CDLL(library_absolute_path)

# general vars
synd_bytes = 208
len_pk = 1357824
len_sk = 13008

class McBits(object):
    def __init__(self, key):
        self.key = key

    def encrypt(self, message_unencoded):
        """McBits public key encryption.

        Args:
            message_unencoded (str): message to be encrypted
        Returns:
            hex-encoded cipher in unicode
        """
        if not self.key.key_length == len_pk:
            raise ValueError("Can't encrypt with a secret key.")
        message = message_unencoded.encode("utf-8")
        public_key = (ctypes.c_ubyte * len_pk)(*self.key.key)
        message_length = len(message)
        cipher_length = synd_bytes + message_length + 16
        cipher = (ctypes.c_ubyte * cipher_length)()
        clen = ctypes.c_longlong()

        mcbits.crypto_encrypt(cipher, ctypes.byref(clen), message, message_length,
                public_key)
        return nacl.encoding.HexEncoder.encode(cipher).decode("utf-8")

    def decrypt(self, encrypted_message_hex):
        """McBits public key decryption.

        Args:
            encrypted_message_hex (string): hex-encoded cipher text
        Returns:
            Clear text message as unicode string
        Raises:
            ValueError: if decryption fails
        """
        if not self.key.key_length == len_sk:
            raise ValueError("Can't decrypt with a private key.")
        encrypted_message = \
                nacl.encoding.HexEncoder.decode(encrypted_message_hex)
        secret_key = (ctypes.c_ubyte * len_sk)(*self.key.key)
        cipher_length = len(encrypted_message)
        message_length = cipher_length - synd_bytes - 16
        decrypted = (ctypes.c_ubyte * message_length)()
        mlen = ctypes.c_longlong()

        status = mcbits.crypto_encrypt_open(decrypted, ctypes.byref(mlen),
                encrypted_message, cipher_length, secret_key)

        if status == 0:
            return bytearray(decrypted).decode("utf-8")
        else:
            raise ValueError("Decryption failed, 'mcbits.crypto_encrypt_open "
            "return value' is not zero")

    @staticmethod
    def key_gen():
        """Key-pair generation for McBits encrytion.

        Args:
            --
        Returns:
            secret_key, public_key objects
        """
        secret_key = (ctypes.c_ubyte * len_sk)()
        public_key = (ctypes.c_ubyte * len_pk)()
        mcbits.crypto_encrypt_keypair(public_key, secret_key)
        return McBitsSecretKey(bytearray(secret_key)), \
                McBitsPublicKey(bytearray(public_key))

class McBitsKey(Key):
    def __init__(self, key, key_name, key_description):
        super(McBitsKey, self).__init__(key, key_name, key_description)

#    def encrypt(self, message_unencoded):
#        """McBits public key encryption.
#
#        Args:
#            message_unencoded (str): message to be encrypted
#        Returns:
#            hex-encoded cipher in unicode
#        """
#        if not self.key_length == len_pk:
#            raise ValueError("Can't encrypt with a secret key.")
#        message = message_unencoded.encode("utf-8")
#        public_key = (ctypes.c_ubyte * len_pk)(*self.key)
#        message_length = len(message)
#        cipher_length = synd_bytes + message_length + 16
#        cipher = (ctypes.c_ubyte * cipher_length)()
#        clen = ctypes.c_longlong()
#
#        mcbits.crypto_encrypt(cipher, ctypes.byref(clen), message, message_length,
#                public_key)
#        return nacl.encoding.HexEncoder.encode(cipher).decode("utf-8")
#
#    def decrypt(self, encrypted_message_hex):
#        """McBits public key decryption.
#
#        Args:
#            encrypted_message_hex (string): hex-encoded cipher text
#        Returns:
#            Clear text message as unicode string
#        Raises:
#            ValueError: if decryption fails
#        """
#        if not self.key_length == len_sk:
#            raise ValueError("Can't decrypt with a private key.")
#        encrypted_message = nacl.encoding.HexEncoder.decode(encrypted_message_hex)
#        secret_key = (ctypes.c_ubyte * len_sk)(*self.key)
#        cipher_length = len(encrypted_message)
#        message_length = cipher_length - synd_bytes - 16
#        decrypted = (ctypes.c_ubyte * message_length)()
#        mlen = ctypes.c_longlong()
#
#        status = mcbits.crypto_encrypt_open(decrypted, ctypes.byref(mlen),
#                encrypted_message, cipher_length, secret_key)
#
#        if status == 0:
#            return bytearray(decrypted).decode("utf-8")
#        else:
#            raise ValueError("Decryption failed, 'mcbits.crypto_encrypt_open "
#            "return value' is not zero")

    def _is_valid(self):
        if type(self.key) != bytearray:
            return False
        elif len(self.key) != self.key_length:
            return False
        else:
            return True

class McBitsSecretKey(McBitsKey):
    def __init__(self, key):
        super(McBitsSecretKey, self).__init__(key, secret_key_name,
                secret_key_description)
        self.key_length = len_sk
        self._check_length(self.key_length)
        self.security_level = "SECRET"

    @staticmethod
    def import_key(file_name_with_path, silent=False):
        with open(file_name_with_path) as f:
            header = f.readline().rstrip()
            encrypted_key_hex = f.readline().rstrip()
            footer = f.readline().rstrip()
        if not secret_key_description in header:
            raise IOError("Key is not a McBits SECRET key.")
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
        return McBitsSecretKey(bytearray(decrypted_key))

class McBitsPublicKey(McBitsKey):
    def __init__(self, key):
        super(McBitsPublicKey, self).__init__(key, public_key_name,
                public_key_description)
        self.key_length = len_pk
        self._check_length(self.key_length)
        self.security_level = "Public"

    @staticmethod
    def import_key(file_name_with_path, silent=False):
        with open(file_name_with_path) as f:
            header = f.readline().rstrip()
            key_hex = f.readline().rstrip()
            footer = f.readline().rstrip()
        if not public_key_description in header:
            raise IOError("Key is not a McBits Public key.")
        if not footer == Key.footer:
            raise IOError("Key is not a valid key.")
        key = nacl.encoding.HexEncoder.decode(key_hex)
        return McBitsPublicKey(bytearray(key))


if __name__ == "__main__":
    import gc  #garbage collector
    # This in an example. In production, you would want to read the key from an
    # external file or the command line. The key must be 32 bytes long.

    # DON'T DO THIS IN PRODUCTION!

    s, p = McBits.key_gen()
    p.export_key(".", "mine")

    sender = McBits(p)
    receiver = McBits(s)

    message = "This is my message."
    print("message  : " + message)

    enc = sender.encrypt(message)
    print("encrypted: " + enc)

    dec = receiver.decrypt(enc)
    print("decrypted: " + dec)
    exit()

    # make sure all memory is flushed after operations
    del s
    del p
    del sender
    del receiver
    del enc
    del dec
    gc.collect()
