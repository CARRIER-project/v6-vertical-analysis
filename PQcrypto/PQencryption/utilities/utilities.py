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
