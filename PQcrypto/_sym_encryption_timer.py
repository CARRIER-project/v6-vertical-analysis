#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Fri Jul  7 16:44:29 CEST 2017
@author: BMMN
"""

from __future__ import print_function  # make print python3 compatible

import timeit

bytes_key = b'Thirtytwo byte key, this is long'
message = "This is a message. Hash me!"
iterations = 40000

print("Time in [s] for " + str(iterations) + " iterations.")
print("Only encryption:")

print("PyNaCl Salsa20: "
        + str(timeit.timeit(
            "my_encrypted=my_cipher.encrypt(message)",
            setup="from PQencryption import Salsa20, Salsa20Key;"
            "from __main__ import bytes_key, message;"
            "key=Salsa20Key(bytes_key);"
            "my_cipher=Salsa20(key);",
            number=iterations)))

print("Crypto AES: "
        + str(timeit.timeit(
            "my_encrypted=my_cipher.encrypt(message)",
            setup="from PQencryption import AES256, AES256Key;"
            "from __main__ import bytes_key, message;"
            "key=AES256Key(bytes_key);"
            "my_cipher=AES256(key);",
            number=iterations)))

print()
print("Encryption and decryption:")

print("PyNaCl Salsa20: "
        + str(timeit.timeit(
            "my_encrypted=my_cipher.encrypt(message);"
            "my_decrypted=my_cipher.decrypt(my_encrypted)",
            setup="from PQencryption import Salsa20, Salsa20Key;"
            "from __main__ import bytes_key, message;"
            "key=Salsa20Key(bytes_key);"
            "my_cipher=Salsa20(key);",
            number=iterations)))

print("Crypto AES: "
        + str(timeit.timeit(
            "my_encrypted=my_cipher.encrypt(message);"
            "my_decrypted=my_cipher.decrypt(my_encrypted)",
            setup="from PQencryption import AES256, AES256Key;"
            "from __main__ import bytes_key, message;"
            "key=AES256Key(bytes_key);"
            "my_cipher=AES256(key);",
            number=iterations)))

print()
print("Comments:")
print("• Generating the initialization vector from AES takes quite a while.")
print("• Salsa20 is faster.")
