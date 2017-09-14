#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Fri Jul  7 16:44:29 CEST 2017
@author: BMMN
"""

from __future__ import print_function  # make print python3 compatible

import timeit

key = b'Thirtytwo byte key, this is long'
message = "This is a message. Hash me!"
iterations = 40000

print("Time in [s] for " + str(iterations) + " iterations.")
print("Only encryption:")

print("PyNaCl Salsa20 wrapped: "
        + str(timeit.timeit(
            "my_encrypted=encrypt(message, key)",
            setup="from salsa20_256_PyNaCl import encrypt;"
            "from __main__ import key, message",
            number=iterations)))

print("PyNaCl Salsa20 bare: "
        + str(timeit.timeit(
            "my_encrypted=my_cipher.encrypt(message)",
            setup="from salsa20_256_PyNaCl import Salsa20Cipher;"
            "from __main__ import key, message;"
            "my_cipher=Salsa20Cipher(key);",
            number=iterations)))

print("Crypto AES wrapped: "
        + str(timeit.timeit(
            "initialization_vector = Random.new().read(AES.block_size);"
            "my_cipher=AES256Cipher(key);"
            "my_encrypted=my_cipher.encrypt(message, initialization_vector)",
            setup="from aes_256_Crypto import AES256Cipher;"
            "from Crypto import Random;"
            "from Crypto.Cipher import AES;"
            "from __main__ import key, message",
            number=iterations)))

print("Crypto AES bare: "
        + str(timeit.timeit(
            "initialization_vector = Random.new().read(AES.block_size);"
            "my_encrypted=my_cipher.encrypt(message, initialization_vector)",
            setup="from aes_256_Crypto import AES256Cipher;"
            "from Crypto import Random;"
            "from Crypto.Cipher import AES;"
            "from __main__ import key, message;"
            "my_cipher=AES256Cipher(key);",
            number=iterations)))

print()
print("Encryption and decryption:")

print("PyNaCl Salsa20 wrapped: "
        + str(timeit.timeit(
            "my_encrypted=encrypt(message, key);"
            "my_decrypted=decrypt(my_encrypted, key)",
            setup="from salsa20_256_PyNaCl import encrypt, decrypt;"
            "from __main__ import key, message",
            number=iterations)))

print("PyNaCl Salsa20 bare: "
        + str(timeit.timeit(
            "my_encrypted=my_cipher.encrypt(message);"
            "my_decrypted=my_cipher.decrypt(my_encrypted)",
            setup="from salsa20_256_PyNaCl import Salsa20Cipher;"
            "from __main__ import key, message;"
            "my_cipher=Salsa20Cipher(key);",
            number=iterations)))

print("Crypto AES wrapped: "
        + str(timeit.timeit(
            "initialization_vector = Random.new().read(AES.block_size);"
            "my_cipher=AES256Cipher(key);"
            "my_encrypted=my_cipher.encrypt(message, initialization_vector);"
            "my_decrypted=my_cipher.decrypt(my_encrypted)",
            setup="from aes_256_Crypto import AES256Cipher;"
            "from Crypto import Random;"
            "from Crypto.Cipher import AES;"
            "from __main__ import key, message",
            number=iterations)))

print("Crypto AES bare: "
        + str(timeit.timeit(
            "initialization_vector = Random.new().read(AES.block_size);"
            "my_encrypted=my_cipher.encrypt(message, initialization_vector);"
            "my_decrypted=my_cipher.decrypt(my_encrypted)",
            setup="from aes_256_Crypto import AES256Cipher;"
            "from Crypto import Random;"
            "from Crypto.Cipher import AES;"
            "from __main__ import key, message;"
            "my_cipher=AES256Cipher(key);",
            number=iterations)))

print()
print("Comments:")
print("• Salsa20 is faster.")
print("• Generating the initialization vector from AES takes quite a while.")
print("• Re-using nacl.secret.SecretBox gives a big speed boost (Salsa20 "
    "wrapped vs bare).")
