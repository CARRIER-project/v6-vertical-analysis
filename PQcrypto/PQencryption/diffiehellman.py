# -*- coding: utf-8 -*-
"""
Created on Mon Jul 10 16:26:41 CEST 2017

@author: BMMN

Curve25519 PyNaCl
"""

from __future__ import print_function  # make print python3 compatible

import nacl.utils
import nacl.public
import nacl.encoding
from .salsa20 import Salsa20, Salsa20Key
from .utilities import _get_password
from .sha512 import hash512
from .Key import Key

secret_key_name = "SECRET_Diffie_Hellman_Key"
secret_key_description = secret_key_name + " for DH pubkey encryption"

public_key_name = "Public_Diffie_Hellman_Key"
public_key_description = public_key_name +  " for DH pubkey encryption"


class DiffieHellman(object):
    def __init__(self, secret_key, public_key):
        self.secret_key = secret_key
        self.public_key = public_key
        self.crypto_box = nacl.public.Box(secret_key.key, public_key.key)

    @staticmethod
    def key_gen():
        """Key-pair generation for Diffie-Hellman Curve25519 public key encryption.

        Args:
            --
        Returns:
            public_key object, priveta_key object
        """
        secret_key = nacl.public.PrivateKey.generate()
        public_key = secret_key.public_key
        return DiffieHellmanSecretKey(secret_key), \
                DiffieHellmanPublicKey(public_key)

    def encrypt(self, message_unencoded):
        message = message_unencoded.encode("utf-8")
        nonce = nacl.utils.random(nacl.public.Box.NONCE_SIZE)
        encrypted = self.crypto_box.encrypt(message, nonce)
        return nacl.encoding.Base64Encoder.encode(encrypted).decode("utf-8")

    def decrypt(self, encrypted_message_base64):
        encrypted_message = nacl.encoding.Base64Encoder.decode(
                encrypted_message_base64)
        return self.crypto_box.decrypt(encrypted_message).decode("utf-8")

class DiffieHellmanKey(Key):
    def __init__(self, key, key_name, key_description):
        super(DiffieHellmanKey, self).__init__(key, key_name, key_description)
        self.key_length = len(bytes(self.key))

    def _is_valid(self):
        if not len(bytes(self.key)) == 32:
            return False
        if not (isinstance(self.key, nacl.public.PrivateKey)
                or isinstance(self.key, nacl.public.PublicKey)):
            return False
        return True

class DiffieHellmanSecretKey(DiffieHellmanKey):
    def __init__(self, key):
        super(DiffieHellmanSecretKey, self).__init__(key, secret_key_name,
                secret_key_description)
        self.security_level = "SECRET"
        self.public_key = DiffieHellmanPublicKey(self.key.public_key)

    @staticmethod
    def import_key(file_name_with_path, silent=False):
        with open(file_name_with_path) as f:
            header = f.readline().rstrip()
            encrypted_key_base64 = f.readline().rstrip()
            footer = f.readline().rstrip()
        if not secret_key_description in header:
            raise IOError("Key is not a Diffie Hellman SECRET key.")
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
        return DiffieHellmanSecretKey(nacl.public.PrivateKey(decrypted_key))

class DiffieHellmanPublicKey(DiffieHellmanKey):
    def __init__(self, key):
        super(DiffieHellmanPublicKey, self).__init__(key, public_key_name,
                public_key_description)
        self.security_level = "Public"

    @staticmethod
    def import_key(file_name_with_path, silent=False):
        with open(file_name_with_path) as f:
            header = f.readline().rstrip()
            key_base64 = f.readline().rstrip()
            footer = f.readline().rstrip()
        if not public_key_description in header:
            raise IOError("Key is not a Diffie Hellman Public key.")
        if not footer == Key.footer:
            raise IOError("Key is not a valid key.")
        key = nacl.encoding.Base64Encoder.decode(key_base64)
        return DiffieHellmanPublicKey(nacl.public.PublicKey(key))
