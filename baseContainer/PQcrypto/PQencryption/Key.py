# -*- coding: utf-8 -*-
""" Template for crypto keys.

Not to be used on its own.
"""

import os
import gc
import nacl.encoding
from .utilities import _get_password
from .sha512 import hash512

class _Key(object):
    """ Generic key object.

    Attributes:
        key: The raw key.
        name: The key name.
        description: Verbose description of key type.
        header: Header for exporting to a file, also contains the description.
        footer: Footer for exporting to a file

    Methods:
        export_key: Export the raw key to a file.
        _check_length: Verify the length of the raw key.
    """

    footer = "#" * 79

    def __init__(self, key, key_name, key_description):
        self.key = key
        self.name = key_name
        self.description = key_description
        self.header = "## " + self.description + " "\
                + "#" * (79-4-len(self.description))
        self.footer = _Key.footer

    def _check_length(self, key_length):
        if len(self.key) != key_length:
            raise ValueError('Invalid key length, must be '
                    + str(key_length) + ' bits.')

    def export_key(self, path, owner, force=False, silent=False):
        from .salsa20 import Salsa20, Salsa20Key
        file_name = self.name + "_" + owner + ".key"
        if os.path.isfile(path + "/" + file_name) and (force==False):
            raise FileExistsError("Key file exists, use 'force=True' or "
                    "different file name.")
        if "SECRET" in self.security_level:
            if silent:
                user_password = _get_password(validate=True,
                        print_requirements=False)
            else:
                user_password = _get_password(validate=True)

            # turn user_password into 32 char storag_password for Salsa20:
            storage_password = nacl.encoding.Base64Encoder.decode(
                            hash512(user_password))[:32]
            storage_key = Salsa20Key(storage_password)
            symmetric_cipher = Salsa20(storage_key)
            base64_key = nacl.encoding.Base64Encoder.encode(
                    bytes(self.key)).decode("utf-8")
            key_for_file = symmetric_cipher.encrypt(base64_key)
            del user_password
            del storage_password
            del symmetric_cipher
            del base64_key
            gc.collect()

        else:
            base64_key = nacl.encoding.Base64Encoder.encode(bytes(self.key))
            key_for_file = base64_key.decode("utf-8")

        with open(path + file_name, 'w') as f:
            f.write(self.header + "\n")
            f.write(str(key_for_file) + "\n")
            f.write(self.footer + "\n")
