# -*- coding: utf-8 -*-
""" EdDSA pubkey signing cipher.

Will be vulnerable against quantum computing attacks. Wrapper around Curve25519
signing from the PyNaCl package.

class EdDSA provides a cipher object for signing and verifying. Without
instantiation you can use key_gen() to generate keys.

classes EdDSASigningKey and EdDSAVerifyingKey provide key objects.
The raws key can be found in KEYNAME.key. Without instantiation,
calling import_key() reads a keyfile and returns a key object.
"""

from __future__ import print_function  # make print python3 compatible

import nacl.signing
import nacl.encoding
from .salsa20 import Salsa20, Salsa20Key
from .utilities import _get_password, repeat_import_export
from .sha512 import hash512
from .Key import _Key

secret_key_name = "SECRET_EdDSA_Key"
secret_key_description = secret_key_name + " for EdDSA asymmetric signing"

public_key_name = "Public_EdDSA_Key"
public_key_description = public_key_name + " for EdDSA asymmetric signing"


class EdDSA(object):
    """ Cipher object for signing and verification.

    Attributes:
        key: The raw key.

    Methods:
        sign: Sign file content with an EdDSA cipher.
        verify: Verify signed file content with an EdDSA cipher.
        key_gen: Generate a tuple of key objects, containing a EdDSA signing
                 key and verify key. Can be called without instantiation.
    """
    def __init__(self, key):
        self.key = key

    def sign(self, message):
        """ Signs file content with an EdDSA cipher.

        Args:
            message: File content.

        Returns:
            Base64 encoded signed file content.
        """
        if isinstance(self.key.key, nacl.signing.SigningKey):
            signed = self.key.key.sign(bytes(message.encode("utf-8")))
            return nacl.encoding.Base64Encoder.encode(signed).decode("utf-8")
        else:
            raise TypeError("Key is no EdDSA SigningKey")

    def verify(self, signed_message_base64):
        """ Verifies signed file content with an EdDSA cipher.

        Args:
            signed_message_base64: Base64 encoded file content.

        Returns:
            Original file content.

        Raises:
            nacl.exceptions.BadSignatureError if verification fails.
        """
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
        """Key-pair generation for EdDSA signing and verification.

        Args:
            --
        Returns:
            signing_key object, verifying_key object
        """
        signing_key = nacl.signing.SigningKey.generate()
        verify_key = signing_key.verify_key
        return EdDSASigningKey(signing_key), EdDSAVerifyKey(verify_key)

class _EdDSAKey(_Key):
    def __init__(self, key, key_name, key_description):
        super(_EdDSAKey, self).__init__(key, key_name, key_description)
        self.key_length = len(bytes(self.key))

    def _is_valid(self):
        if not len(bytes(self.key)) == 32:
            return False
        if not (isinstance(self.key, nacl.signing.SigningKey)
                or isinstance(self.key, nacl.signing.VerifyKey)):
            return False
        return True

class EdDSASigningKey(_EdDSAKey):
    """ Private key object for signing.

    Attributes:
        key: The raw secret key.
        verify_key: The public key that belongs to the secret key.
        name: The key name.
        description: Verbose description of key type.
        header: Header for exporting to a file, also contains the description.
        footer: Footer for exporting to a file.
        security_level: String, "SECRET" if encrypted storage is needed,
                        "Private" if not.

    Methods:
        export_key: Export the raw key to a key file.
        import _key: Creates a key object from the content of a key file. Can
                     be called without instantiation.
        _check_length: Verify the length of the raw key.
        _is_valid: Self check for validity.
    """
    def __init__(self, key):
        super(EdDSASigningKey, self).__init__(key, secret_key_name,
                secret_key_description)
        self.security_level = "SECRET"
        self.verify_key = EdDSAVerifyKey(self.key.verify_key)

    @staticmethod
    @repeat_import_export
    def import_key(file_name_with_path, silent=False):
        """ Creates a signing key object from a key file.

        Attributes:
            file_name_with_path: Key_file.
            silent: Don't print password requirements if set True.

        Returns:
            EdDSASigningKey object.

        Raises:
            IOError: When opening a wrong file.
            TypeError: When key in file is invalid.
            ValueError: When decryption passwords do not match requirements.
            nacl.exceptions.CryptoError: When key decryption fails.
        """
        with open(file_name_with_path) as f:
            header = f.readline().rstrip()
            encrypted_key_base64 = f.readline().rstrip()
            footer = f.readline().rstrip()
        if not secret_key_description in header:
            raise TypeError("Key is not a EdDSA SECRET key.")
        if not footer == _Key.footer:
            raise TypeError("Key is not a valid key.")
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

class EdDSAVerifyKey(_EdDSAKey):
    """ Public key object for verification.

    Attributes:
        key: The raw public key.
        name: The key name.
        description: Verbose description of key type.
        header: Header for exporting to a file, also contains the description.
        footer: Footer for exporting to a file.
        security_level: String, "SECRET" if encrypted storage is needed,
                        "Private" if not.

    Methods:
        export_key: Export the raw key to a key file.
        import _key: Creates a key object from the content of a key file. Can
                     be called without instantiation.
        _check_length: Verify the length of the raw key.
        _is_valid: Self check for validity.
    """
    def __init__(self, key):
        super(EdDSAVerifyKey, self).__init__(key, public_key_name,
                public_key_description)
        self.security_level = "Public"

    @staticmethod
    def import_key(file_name_with_path, silent=False):
        """ Creates a verify key object from a key file.

        Attributes:
            file_name_with_path: Key_file.
            silent: Don't print password requirements if set True.

        Returns:
            EdDSAVerifyKey object.

        Raises:
            IOError: When opening a wrong file.
            TypeError: When key in file is invalid.
        """
        with open(file_name_with_path) as f:
            header = f.readline().rstrip()
            key_base64 = f.readline().rstrip()
            footer = f.readline().rstrip()
        if not public_key_description in header:
            raise TypeError("Key is not a EdDSA Public key.")
        if not footer == _Key.footer:
            raise TypeError("Key is not a valid key.")
        key = nacl.encoding.Base64Encoder.decode(key_base64)
        return EdDSAVerifyKey(nacl.signing.VerifyKey(key))
