#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 13 07:12:15 CEST 2017

@author: BMMN
"""

from __future__ import print_function  # make print python3 compatible
import getpass
import gc  # garbage collector
import re
import os
import nacl.hash
import nacl.utils
import nacl.signing
import nacl.encoding
import nacl.public
#from .symmetric_encryption import salsa20_256_PyNaCl
#from .pub_key.pk_signature.quantum_vulnerable import signing_Curve25519_PyNaCl

def _check_password(password):
    length = 20
    length_error = len(password) < length
    digit_error = re.search(r"\d", password) is None
    uppercase_error = re.search(r"[A-Z]", password) is None
    lowercase_error = re.search(r"[a-z]", password) is None
    # \W matches any non-word character [^a-zA-Z_0-9] . By including
    # "|_" (or _) we get effectively all special charsacters [^a-zA-Z0-9] .
    symbol_error = re.search(r"\W|_", password) is None
    password_ok = not ( length_error or digit_error or uppercase_error
            or lowercase_error or symbol_error )

    errors = ""
    if length_error:
        errors += "Password too short.\n"
    if digit_error:
        errors += "Password does not contain digits.\n"
    if lowercase_error:
        errors += "Password does not contain lowercase characters.\n"
    if uppercase_error:
        errors += "Password does not contain uppercase characters.\n"
    if symbol_error:
        errors += "Password does not contain any special characters.\n"
    if not password_ok:
        raise ValueError(errors)

def _get_password(validate=False, print_requirements=True):
    requirements = ("Password must have at least 20 characters, including:\n"
            "upper-case    ABC...\n"
            "lower-case    abc...\n"
            "digits        012...\n"
            "special chars !${...")
    if print_requirements:
        print(requirements)
    password = getpass.getpass()
    _check_password(password)
    if validate:
        password_2 = getpass.getpass("Repeat password:")
        if password != password_2:
            raise ValueError("Passwords differ.")

    return password

#def export_key(key, path, name, header, key_type):
#    if ((key_type == "PrivateKey")
#            or (key_type == "SigningKey")
#            or (key_type == "SymmetricKey")):
#        user_password = get_password(validate=True)
#
#        # turn user_password into 32 char storag_password for Salsa20:
#        storage_password = nacl.hash.sha512(user_password,
#                encoder=nacl.encoding.HexEncoder)[:32]
#        my_cipher = salsa20_256_PyNaCl.Salsa20Cipher(storage_password)
#        key_for_file = my_cipher.encrypt(key)
#        del user_password
#        del storage_password
#        del my_cipher
#    else:
#        key_for_file = key
#    with open(path + "/" + name, 'w') as file:
#        file.write(header)
#        file.write(key_for_file)
#    del key_for_file
#    gc.collect()
#
def import_key(file_name_with_path, silent=False):
    file_name = os.path.basename(file_name_with_path)
    key = False

    if "McBits" in file_name:
        if "SECRET" in file_name:
            from ..crypto.encryption_mcbits import McBitsSecretKey
            try:
                key = McBitsSecretKey.import_key(file_name_with_path, silent)
            except IOError:
                print("Could not import key file: " + str(file_name))

        if "Public" in file_name:
            from ..crypto.encryption_mcbits import McBitsPublicKey
            try:
                key = McBitsPublicKey.import_key(file_name_with_path, silent)
            except IOError:
                print("Could not import key file: " + str(file_name))

    if "AES_256" in file_name:
        from ..crypto.aes_256_Crypto import AES256Key
        try:
            key = AES256Key.import_key(file_name_with_path, silent)
        except IOError:
            print("Could not import key file: " + str(file_name))

    if "Salsa20" in file_name:
        from ..crypto.salsa20_256_PyNaCl import Salsa20Key
        try:
            key = Salsa20Key.import_key(file_name_with_path, silent)
        except IOError:
            print("Could not import key file: " + str(file_name))

    if "EdDSA" in file_name:
        if "SECRET" in file_name:
            from ..crypto.signing_Curve25519_PyNaCl import EdDSASigningKey
            try:
                key = EdDSASigningKey.import_key(file_name_with_path, silent)
            except IOError:
                print("Could not import key file: " + str(file_name))

        if "Public" in file_name:
            from ..crypto.signing_Curve25519_PyNaCl import EdDSAVerifyKey
            try:
                key = EdDSAVerifyKey.import_key(file_name_with_path, silent)
            except IOError:
                print("Could not import key file: " + str(file_name))

    if "Diffie_Hellman" in file_name:
        if "SECRET" in file_name:
            from ..crypto.encryption_Curve25519_PyNaCl import DiffieHellmanSecretKey
            try:
                key = DiffieHellmanSecretKey.import_key(
                        file_name_with_path, silent)
            except IOError:
                print("Could not import key file: " + str(file_name))

        if "Public" in file_name:
            from ..crypto.encryption_Curve25519_PyNaCl import DiffieHellmanPublicKey
            try:
                key = DiffieHellmanPublicKey.import_key(
                        file_name_with_path, silent)
            except IOError:
                print("Could not import key file: " + str(file_name))

    if key:
        return key
    else:
        raise TypeError("Importing invalid key.")

#    if ((key_type == "SigningKey")
#        or (key_type == "PrivateKey")
#        or (key_type == "SymmetricKey")):
#        user_password = get_password(validate=False)
#
#        # turn user_password into 32 char storage_password for Salsa20:
#        storage_password = nacl.hash.sha512(user_password,
#                encoder=nacl.encoding.HexEncoder)[:32]
#        my_cipher = salsa20_256_PyNaCl.Salsa20Cipher(storage_password)
#        decrypted_key = my_cipher.decrypt(raw_key)
#        if key_type == "SymmetricKey":
#            key = decrypted_key.decode("hex")
#        elif key_type == "PrivateKey":
#            key = nacl.public.PrivateKey(decrypted_key,
#                    encoder=nacl.encoding.HexEncoder)
#        else:
#            key = nacl.signing.SigningKey(decrypted_key,
#                    encoder=nacl.encoding.HexEncoder)
#    elif key_type == "PublicKey":
#        key = nacl.public.PublicKey(raw_key,
#                encoder=nacl.encoding.HexEncoder)
#    elif key_type == "VerifyKey":
#        key = nacl.signing.VerifyKey(raw_key,
#                encoder=nacl.encoding.HexEncoder)
#    else:
#        raise KeyError("Invalid key type: " + key_type)
#    return key

#def _to_hex(string):
#    #return nacl.encoding.HexEncoder.encode(string)
#    return nacl.encoding.HexEncoder.encode(bytes(string.encode("utf-8"))).decode("utf-8")
#
#def _from_hex(string):
#    return nacl.encoding.HexEncoder.decode(string).decode("utf-8")

#def sign_encrypt_sign(message, signing_key, encryption_key):
#    signed_message = signing_Curve25519_PyNaCl.sign(message, signing_key)
#    encrypted_signed_message = salsa20_256_PyNaCl.encrypt(signed_message,
#            encryption_key)
#    signed_encrypted_signed_message = signing_Curve25519_PyNaCl.sign(
#            encrypted_signed_message, signing_key)
#    return signed_encrypted_signed_message
#
#def verify_decrypt_verify(signed_encrypted_signed, verify_key, encryption_key):
#    verify_key_hex = verify_key.encode(encoder=nacl.encoding.HexEncoder).decode("utf-8")
#    verified_encrypted_signed = signing_Curve25519_PyNaCl.verify(signed_encrypted_signed, verify_key_hex)
#    signed = salsa20_256_PyNaCl.decrypt(verified_encrypted_signed,
#            encryption_key)
#    verified = signing_Curve25519_PyNaCl.verify(signed, verify_key_hex)
#    return verified
