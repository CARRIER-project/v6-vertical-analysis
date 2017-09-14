import os
import gc
import nacl.encoding
from ..utilities.utilities import _get_password
from .sha_512_hashlib import hash512

class Key(object):
    footer = "#" * 79

    def __init__(self, key, key_name, key_description):
        self.key = key
        self.name = key_name
        self.description = key_description
        self.header = "## " + self.description + " "\
                + "#" * (79-4-len(self.description))
        self.footer = Key.footer

    def _check_length(self, key_length):
        if len(self.key) != key_length:
            raise ValueError('Invalid key length, must be '
                    + str(key_length) + ' bits.')

    def export_key(self, path, owner, force=False, silent=False):
        from .salsa20_256_PyNaCl import Salsa20, Salsa20Key
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
            storage_password = nacl.encoding.HexEncoder.decode(
                            hash512(user_password))[:32]
            storage_key = Salsa20Key(storage_password)
            symmetric_cipher = Salsa20(storage_key)
            hex_key = nacl.encoding.HexEncoder.encode(
                    bytes(self.key)).decode("utf-8")
            key_for_file = symmetric_cipher.encrypt(hex_key).decode("utf-8")
            del user_password
            del storage_password
            del symmetric_cipher
            del hex_key
            gc.collect()

        else:
            hex_key = nacl.encoding.HexEncoder.encode(bytes(self.key))
            key_for_file = hex_key.decode("utf-8")

        with open(path + file_name, 'w') as f:
            f.write(self.header + "\n")
            f.write(str(key_for_file) + "\n")
            f.write(self.footer + "\n")
