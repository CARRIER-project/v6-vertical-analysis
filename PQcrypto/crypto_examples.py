#! /usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 13 08:46:20 CEST 2017

@author: BMMN
"""

from __future__ import print_function  # make print python3 compatible
import gc  # garbage collection

def example_hashing():
    import PQencryption as cr
    print()
    print()
    print("=== example_hashing() ===")
    print()

    message = "This is a message. Hash me!"
    print("message: " + message)

    hashed = cr.hash512(message)
    print("hashed:  " + hashed)

    # make sure all memory is flushed after operations
    del message
    gc.collect()

def example_salthashing():
    import PQencryption as cr
    print()
    print()
    print("=== example_salthashing() ===")
    print()
    # In production the salt should come from a hardware random number generator
    # and will be shared between parties.

    # Salt must be 128 bytes in base64.
    salt = "a" * 128

    message = "This is a message. Hash me!"
    print("message:    " + message)

    hashed = cr.salthash(salt, message)
    print("salthashed: " + hashed)

    # make sure all memory is flushed after operations
    del salt
    del message
    gc.collect()

def example_generate_keys():
    import  PQencryption as cr
    print()
    print()
    print("=== example_generate_keys() ===")
    print()

    ciphers = [cr.AES256, cr.McBits, cr.Salsa20, cr.EdDSA, cr.DiffieHellman]
    for cipher in ciphers:
        cipher_name = str(cipher).split('.')[-1].split("'")[0]
        print(cipher_name)
        print(cipher.key_gen())
        print()

def example_symmetric_block_encryption_AES256():
    import PQencryption as cr
    print()
    print()
    print("=== example_symmetric_block_encryption_AES256() ===")
    print()
    # This in an example. In production, you would want to read the key from an
    # external file or the command line. The key must be 32 bytes long.

    # DON'T DO THIS IN PRODUCTION!
    key = cr.AES256.key_gen()

    message = 'This is my message.'
    print("message  : " + message)

    symmetric_cipher = cr.AES256(key)

    # encryption
    # In production, make sure that pythons Crypto.Random has access to
    # a hardware random number generator!
    my_encrypted_message = symmetric_cipher.encrypt(message)
    print("encrypted: " + my_encrypted_message)

    # decryption
    my_decrypted_message = symmetric_cipher.decrypt(my_encrypted_message)
    print("decrypted: " + my_decrypted_message)

    # make sure all memory is flushed after operations
    del key
    del message
    del symmetric_cipher
    del my_decrypted_message
    gc.collect()

def example_symmetric_streaming_encryption_salsa20():
    import PQencryption as cr
    print()
    print()
    print("=== example_symmetric_streaming_encryption_salsa20() ===")
    print()

    # This in an example. In production, you would want to read the key from an
    # external file or the command line. The key must be 32 bytes long.

    # DON'T DO THIS IN PRODUCTION!
    key = cr.Salsa20.key_gen()

    message = 'This is my message.'
    print("message  : " + message)

    symmetric_cipher = cr.Salsa20(key)

    # encryption
    my_encrypted_message = symmetric_cipher.encrypt(message)
    print("encrypted: " + my_encrypted_message)

    # decryption
    my_decrypted_message = symmetric_cipher.decrypt(my_encrypted_message)
    print("decrypted: " + my_decrypted_message)

    # make sure all memory is flushed after operations
    del key
    del message
    del symmetric_cipher
    del my_decrypted_message
    gc.collect()

def example_classic_pubkey_encryption():
    import PQencryption as cr
    print()
    print()
    print("=== example_classic_pubkey_encryption() ===")
    print()

    # This in an example. In production, you would want to read the key from an
    # external file or the command line. The key must be 32 bytes long.

    # DON'T DO THIS IN PRODUCTION!
    secret_key_Alice, public_key_Alice = cr.DiffieHellman.key_gen()
    secret_key_Bob, public_key_Bob = cr.DiffieHellman.key_gen()

    message = 'This is my message.'
    print("message  :    " + message)

    q_vuln_pubkey_cipher_Alice = cr.DiffieHellman(secret_key_Alice,
            public_key_Bob)
    q_vuln_pubkey_cipher_Bob = cr.DiffieHellman(secret_key_Bob,
            public_key_Alice)

    # encrypting
    encrypted = q_vuln_pubkey_cipher_Alice.encrypt(message)
    print("encrypted:    " + encrypted)

    # decrypting
    decrypted_BA = q_vuln_pubkey_cipher_Bob.decrypt(encrypted)
    print("decrypted_BA: " + decrypted_BA)

    decrypted_AB = q_vuln_pubkey_cipher_Alice.decrypt(encrypted)
    print("decrypted_AB: " + decrypted_BA)

    # make sure all memory is flushed after operations
    del secret_key_Alice
    del secret_key_Bob
    del message
    del encrypted
    del decrypted_BA
    del decrypted_AB
    gc.collect()

def example_quantum_safe_pubkey_encryption():
    import PQencryption as cr
    print()
    print()
    print("=== example_quantum_safe_pubkey_encryption() ===")
    print()

    # This in an example. In production, you would want to read the key from an
    # external file or the command line. The key must be 32 bytes long.

    # DON'T DO THIS IN PRODUCTION!
    secret_key_Alice, public_key_Alice = cr.McBits.key_gen()

    message = 'This is my message.'
    print("message  : " + message)

    q_safe_pubkey_cipher_Bob = cr.McBits(public_key_Alice)
    q_safe_pubkey_cipher_Alice = cr.McBits(secret_key_Alice)

    # encrypting
    encrypted = q_safe_pubkey_cipher_Bob.encrypt(message)
    print("encrypted: " + encrypted)

    # decrypting
    decrypted = q_safe_pubkey_cipher_Alice.decrypt(encrypted)
    print("decrypted: " + decrypted)

    # make sure all memory is flushed after operations
    del secret_key_Alice
    del message
    del decrypted
    gc.collect()

def example_export_import_keys():
    import  PQencryption as cr
    print()
    print()
    print("=== example_export_import_keys() ===")
    print()

    path = ".tmp/"
    owner = "CBS"
    key_objects = cr.EdDSA.key_gen()
    for key_object in key_objects:
        print()
        print("Exporting key " + str(key_object))
        print()
        key_object.export_key(path, owner, force=True, silent=False)

        print()
        print("Importing key")
        print()
        file_name = key_object.name + "_" + owner + ".key"
        imported_key = cr.import_key(path + file_name, silent=False)
        print()
        print("Key: " + str(imported_key))
        print()

def example_quantum_vulnerable_signing():
    import PQencryption as cr
    print()
    print()
    print("=== example_quantum_vulnerable_signing() ===")
    print()

    # This in an example. In production, you would want to read the key from an
    # external file or the command line. The key must be 32 bytes long.

    # DON'T DO THIS IN PRODUCTION!
    signing_key, verify_key = cr.EdDSA.key_gen()

    message = 'This is my message.'
    print()
    print("message           : " + message)

    # signing
    signing = cr.EdDSA(signing_key)
    signed = signing.sign(message)

    print("signed            : " + signed)

    # In production, you would simply import the verify_key from a file:
    # verify_key = cr.import(filename_with_path)
    # Here, we have to jump through some hoops to make the key printable.
    import nacl.encoding
    print("verify_key_base64 : " + nacl.encoding.Base64Encoder.encode(bytes(verify_key.key)).decode("utf-8"))

    # verification
    verifying = cr.EdDSA(verify_key)
    try:
        print("verification positive: " + verifying.verify(signed))
        print()
        print("verification negative:")
        print("="*79)
        print("THIS WILL FAIL WITH AN ERROR, AS EXPECTED.")
        print("="*79)
        print(verifying.verify("0"*len(signed)))
    except:
        raise

    finally:
        print("="*79)
        print("Yes, clean-up is still executed, even after raising errors:")
        print("begin cleanup ...")
        # make sure all memory is flushed after operations
        del message
        del signing_key
        del signing
        del signed
        del verify_key
        del verifying
        gc.collect()
        print("... end cleanup.")
        print("="*79)

if __name__ == "__main__":
    example_hashing()

    example_salthashing()

    example_symmetric_block_encryption_AES256()

    example_symmetric_streaming_encryption_salsa20()

    example_classic_pubkey_encryption()

    example_quantum_safe_pubkey_encryption()

    example_generate_keys()

    example_export_import_keys()

    example_quantum_vulnerable_signing()
