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

def _check_password(password):
    """ Checks if the password meets the required criteria.
    Criteria:
        - length >= 20
        - contains at least one digit
        - contains at least one lower case character
        - contains at least one upper case character
        - contains at least one special character

    Args:
        password: The password to be checked.
    Raises:
        ValueError: If password does not meet the above mentioned criteria.
    """
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
        del password
        gc.collect()
        raise ValueError(errors)

def _get_password(validate=False, print_requirements=True):
    """ Gets a password from user input.

    Args:
        validate: Does the password need to by typed twice? This is usually
            used for encryption to prevent typos.
        print_requirements: Print the password requirements? Set to False for
            tests.
    Returns:
        The password input by the user.
    Raises:
        ValueError: If validation fails.
    """
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
            del password_2
            raise ValueError("Passwords differ.")
        else:
            del password_2

    return password

def import_key(file_name_with_path, silent=False):
    """ Imports a key from a file.

    Args:
        file_name_with_path: File name with path of the key file.
        silent: Don't print password requirements if set True.
    Returns:
        The imported key.
    Raises:
        IOError: If key import fails.
    """
    file_name = os.path.basename(file_name_with_path)
    key = False

    if "McBits" in file_name:
        if "SECRET" in file_name:
            from .mcbits import McBitsSecretKey
            try:
                key = McBitsSecretKey.import_key(file_name_with_path, silent)
            except IOError:
                print("Could not import key file: " + str(file_name))

        if "Public" in file_name:
            from .mcbits import McBitsPublicKey
            try:
                key = McBitsPublicKey.import_key(file_name_with_path, silent)
            except IOError:
                print("Could not import key file: " + str(file_name))

    if "AES_256" in file_name:
        from .aes256 import AES256Key
        try:
            key = AES256Key.import_key(file_name_with_path, silent)
        except IOError:
            print("Could not import key file: " + str(file_name))

    if "Salsa20" in file_name:
        from .salsa20 import Salsa20Key
        try:
            key = Salsa20Key.import_key(file_name_with_path, silent)
        except IOError:
            print("Could not import key file: " + str(file_name))

    if "EdDSA" in file_name:
        if "SECRET" in file_name:
            from .eddsa import EdDSASigningKey
            try:
                key = EdDSASigningKey.import_key(file_name_with_path, silent)
            except IOError:
                print("Could not import key file: " + str(file_name))

        if "Public" in file_name:
            from .eddsa import EdDSAVerifyKey
            try:
                key = EdDSAVerifyKey.import_key(file_name_with_path, silent)
            except IOError:
                print("Could not import key file: " + str(file_name))

    if "Diffie_Hellman" in file_name:
        if "SECRET" in file_name:
            from .diffiehellman import DiffieHellmanSecretKey
            try:
                key = DiffieHellmanSecretKey.import_key(
                        file_name_with_path, silent)
            except IOError:
                print("Could not import key file: " + str(file_name))

        if "Public" in file_name:
            from .diffiehellman import DiffieHellmanPublicKey
            try:
                key = DiffieHellmanPublicKey.import_key(
                        file_name_with_path, silent)
            except IOError:
                print("Could not import key file: " + str(file_name))

    if key:
        return key
    else:
        raise IOError("Could not import key.")

def sign_encrypt_sign_pubkey(signing_key, quantum_safe_public_key,
        classic_secret_key, classic_public_key, message):
    """ Sign, double public-key-encrypt and sign again a cleartext message.

    The two signing processes prevent chosen-cyphertext-attacks (the
    decryption algorithm only operates on authenticated code) and ensure the
    integrity of the data.

    The message is encrypted with the tested and trusted Diffie Hellman cypher,
    as well as the experimental McBits cypher. The latter is thought to be
    safe against quantum computer attacks.

    Args:
        signing_key: EdDSA Key object for signing.
        quantum_safe_public_key: McBits Key object for encryption.
        classic_secret_key: The sender's secret Diffie Hellman Key object for
            encryption.
        classic_public_key: The receiver's public Diffie Hellman Key object for
            encryption.
        message: Plain text string.
    Returns:
        Signed, twice encrypted and signed Base64 encoded ciphertext.
    """

    from .diffiehellman import DiffieHellman
    from .eddsa import EdDSA
    from .mcbits import McBits
    signing_cipher = EdDSA(signing_key)
    classic_cipher = DiffieHellman(classic_secret_key, classic_public_key)
    q_safe_cipher = McBits(quantum_safe_public_key)

    signed = signing_cipher.sign(message)
    signed_classicenc = classic_cipher.encrypt(signed)
    signed_classicenc_qsafeenc = q_safe_cipher.encrypt(signed_classicenc)
    signed_classicenc_qsafeenc_signed = signing_cipher.sign(
            signed_classicenc_qsafeenc)
    return signed_classicenc_qsafeenc_signed

def sign_encrypt_sign_symmetric(signing_key, symmetric_encryption_key,
        message):
    """ Sign, double symmetric-encrypt and sign again a cleartext message.

    The two signing processes prevent chosen-cyphertext-attacks (the
    decryption algorithm only operates on authenticated code) and ensure the
    integrity of the data.

    Args:
        signing_key: EdDSA Key object for signing.
        symmetric_encryption_key: Secret Salsa20 key object.
        message: Plain text string.
    Returns:
        Signed, symmetric encrypted and signed Base64 encoded ciphertext.
    """
    from .eddsa import EdDSA
    from .salsa20 import Salsa20
    signing_cipher = EdDSA(signing_key)
    symmetric_cipher = Salsa20(symmetric_encryption_key)

    signed = signing_cipher.sign(message)
    signed_symencrypted = symmetric_cipher.encrypt(signed)
    signed_symencrypted_signed = signing_cipher.sign(signed_symencrypted)
    return signed_symencrypted_signed

def verify_decrypt_verify_pubkey(verifying_key, quantum_safe_secret_key,
        classic_secret_key, classic_public_key, ciphertext):
    """ Verify, double public-key-decrypt and verify again a cleartext message.

    The two verification processes prevent chosen-cyphertext-attacks (the
    decryption algorithm only operates on authenticated code) and ensure the
    integrity of the data.

    The message is decrypted with the tested and trusted Diffie Hellman cypher,
    as well as the experimental McBits cypher. The latter is thought to be
    safe against quantum computer attacks.

    Args:
        verifying: EdDSA Key object for verifying.
        quantum_safe_secret_key: McBits Key object for decryption.
        classic_secret_key: The receiver's secret Diffie Hellman Key object for
            decryption.
        classic_public_key: The sender's public Diffie Hellman Key object for
            decryption.
        ciphertext: Base64 encoded ciphertext.
    Returns:
        Cleartext message.
    """
    from .diffiehellman import DiffieHellman
    from .eddsa import EdDSA
    from .mcbits import McBits
    verifying_cipher = EdDSA(verifying_key)
    classic_cipher = DiffieHellman(classic_secret_key, classic_public_key)
    q_safe_cipher = McBits(quantum_safe_secret_key)

    signed_classicenc_qsafeenc_signed = ciphertext

    signed_classicenc_qsafeenc = verifying_cipher.verify(
            signed_classicenc_qsafeenc_signed)
    signed_classicenc = q_safe_cipher.decrypt(signed_classicenc_qsafeenc)
    signed = classic_cipher.decrypt(signed_classicenc)
    cleartext = verifying_cipher.verify(signed)
    return cleartext

def verify_decrypt_verify_symmetric(verifying_key, symmetric_encryption_key,
        ciphertext):
    """ Verify, double symmetric-decrypt and verify again a ciphertext.

    The two verification processes prevent chosen-cyphertext-attacks (the
    decryption algorithm only operates on authenticated code) and ensure the
    integrity of the data.

    Args:
        verifying_key: EdDSA Key object for verifying.
        symmetric_encryption_key: Secret Salsa20 key object.
        ciphertext: Base64 encoded ciphertext.
    Returns:
        Cleartext message.
    """
    from .eddsa import EdDSA
    from .salsa20 import Salsa20
    verifying_cipher = EdDSA(verifying_key)
    symmetric_cipher = Salsa20(symmetric_encryption_key)

    signed_symencrypted_signed = ciphertext

    signed_symencrypted = verifying_cipher.verify(signed_symencrypted_signed)
    signed = symmetric_cipher.decrypt(signed_symencrypted)
    cleartext = verifying_cipher.verify(signed)
    return cleartext
