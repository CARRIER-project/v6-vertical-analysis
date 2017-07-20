#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 13 08:46:20 CEST 2017

@author: BMMN
"""

from __future__ import print_function  # make print python3 compatible
import gc  # garbage collection

def test_hashing_hashlib():
    from PQencryption.hashing import sha_512_hashlib
    # In production the salt should come from a hardware random number generator
    # and will be shared between parties.

    # Salt must be 128 bytes in hex.
    salt = "a" * 128

    message = "This is a message. Hash me!"
    print(message)

    hashed = sha_512_hashlib.sha512_hash(salt, message)
    print(hashed)

    # make sure all memory is flushed after operations
    del salt
    del message
    gc.collect()

def test_hashing_PyNaCl():
    from PQencryption.hashing import sha_512_PyNaCl
    # In production the salt should come from a hardware random number generator
    # and will be shared between parties.

    # Salt must be 128 bytes in hex.
    salt = "a" * 128

    message = "This is a message. Hash me!"
    print(message)

    hashed = sha_512_PyNaCl.sha512_hash(salt, message)
    print(hashed)

    # make sure all memory is flushed after operations
    del salt
    del message
    gc.collect()

def test_AES256():
    from PQencryption.symmetric_encryption import aes_256_Crypto
    from Crypto import Random
    from Crypto.Cipher import AES
    # This in an example. In production, you would want to read the key from an
    # external file or the command line. The key must be 32 bytes long.

    # DON'T DO THIS IN PRODUCTION!
    key = b'Thirtytwo byte key, this is long'

    # In production, you would want to have a hardware random number generator
    # for this.
    initialization_vector = Random.new().read(AES.block_size)

    message = 'This is my message.'
    print("message  : " + message)
    my_cipher = aes_256_Crypto.AES256Cipher(key)

    # encryption
    my_encrypted_message = my_cipher.encrypt(message, initialization_vector)
    print("encrypted: " + my_encrypted_message)

    # decryption
    mydec = my_cipher.decrypt(my_encrypted_message)
    print("decrypted: " + mydec)

    # make sure all memory is flushed after operations
    del key
    del message
    del mydec
    gc.collect()

def test_salsa20_256_PyNaCl():
    from PQencryption.symmetric_encryption import salsa20_256_PyNaCl

    # This in an example. In production, you would want to read the key from an
    # external file or the command line. The key must be 32 bytes long.

    # DON'T DO THIS IN PRODUCTION!
    key = b'Thirtytwo byte key, this is long'

    message = 'This is my message.'
    print("message  : " + message)
    my_cipher = salsa20_256_PyNaCl.Salsa20Cipher(key)

    # encryption
    my_encrypted_message = my_cipher.encrypt(message)
    print("encrypted: " + my_encrypted_message)

    # decryption
    my_decrypted_message = my_cipher.decrypt(my_encrypted_message)
    print("decrypted: " + my_decrypted_message)

    # make sure all memory is flushed after operations
    del key
    del message
    del my_decrypted_message
    gc.collect()

def test_quantum_vulnerable_encryption():
    from PQencryption.pub_key.pk_encryption.quantum_vulnerable import encryption_Curve25519_PyNaCl
    import nacl.public

    # This in an example. In production, you would want to read the key from an
    # external file or the command line. The key must be 32 bytes long.

    # DON'T DO THIS IN PRODUCTION!
    secret_key_Bob = nacl.public.PrivateKey.generate()
    public_key_Bob = secret_key_Bob.public_key

    secret_key_Alice = nacl.public.PrivateKey.generate()
    public_key_Alice = secret_key_Alice.public_key

    message = 'This is my message.'
    print("message  : " + message)

    # encrypting
    encrypted = encryption_Curve25519_PyNaCl.encrypt(
            secret_key_Alice, public_key_Bob, message)
    print("encrypted: "
            + nacl.encoding.HexEncoder.encode(encrypted))

    # decrypting
    decrypted_BA = encryption_Curve25519_PyNaCl.decrypt(
            secret_key_Bob, public_key_Alice, encrypted)
    print("decrypted_BA: " + decrypted_BA)

    decrypted_AB = encryption_Curve25519_PyNaCl.decrypt(
            secret_key_Alice, public_key_Bob, encrypted)
    print("decrypted_AB: " + decrypted_BA)

    # make sure all memory is flushed after operations
    del secret_key_Alice
    del secret_key_Bob
    del message
    del encrypted
    del decrypted_BA
    del decrypted_AB
    gc.collect()


def test_quantum_vulnerable_signing():
    from PQencryption.pub_key.pk_signature.quantum_vulnerable import signing_Curve25519_PyNaCl
    import nacl.signing
    # This in an example. In production, you would want to read the key from an
    # external file or the command line. The key must be 32 bytes long.

    # DON'T DO THIS IN PRODUCTION!
    signing_key = nacl.signing.SigningKey.generate()

    message = 'This is my message.'
    print("message  : " + message)

    # signing
    signed, verify_key_hex = signing_Curve25519_PyNaCl.sign(signing_key,
            message)
    print("signed: " + signed)
    print("verify_key_hex: " + verify_key_hex)

    # verification
    verify_key = nacl.signing.VerifyKey(verify_key_hex,
            encoder=nacl.encoding.HexEncoder)
    try:
        print()
        print("verification positive:")
        print(verify_key.verify(signed, encoder=nacl.encoding.HexEncoder))
        print()
        print("verification negative:")
        print("="*79)
        print("THIS WILL FAIL WITH AN ERROR. THIS IS EXPECTED.")
        print("="*79)
        print(verify_key.verify("0"*len(signed),
            encoder=nacl.encoding.HexEncoder))
    except:
        raise

    finally:
        print("="*79)
        print("Yes, clean-up is still executed, even after raising errors.")
        print("begin cleanup")
        # make sure all memory is flushed after operations
        del signing_key
        del signed
        del message
        del verify_key
        del verify_key_hex
        gc.collect()
        print("end cleanup")
        print("="*79)

def test_export_key():
    from PQencryption import utilities
    s, v = utilities.generate_signing_keys()
    path = "."
    s_header = ("# This is an encrypted private signing key."
            "KEEP IT PRIVATE!\n")
    v_header = ("# This is a public verification key."
            "Distribute it to your respondents.\n")
    s_name = "_PRIVATE_signing_key_CBS"
    v_name = "verify_key_CBS"
    utilities.export_key(s, path, s_name, s_header,
            private=True)
    utilities.export_key(v, path, v_name, v_header, private=False)
    return path, s, s_name, v, v_name

def test_import_key(path, signing_key, s_name, verify_key, v_name):
    import nacl.encoding
    from PQencryption import utilities

    print("="*79)
    print("signing_key", signing_key)
    print("verify_key", verify_key)
    print("="*79)
    print()
    print("Importing signing key.")
    imported_signing_key = utilities.import_key(path, s_name, "SigningKey")
    print("Importing verify key.")
    imported_verify_key = utilities.import_key(path, v_name, "VerifyKey")
    print("="*79)
    print("imported_signing_key", imported_signing_key.encode(
        encoder=nacl.encoding.HexEncoder))
    print("imported_verify_key", imported_verify_key.encode(
        encoder=nacl.encoding.HexEncoder))
    print("="*79)

def test_generate_signing_key():
    from PQencryption import utilities
    signing_key_hex, verify_key_hex = utilities.generate_signing_keys()
    print(signing_key_hex)
    print(verify_key_hex)

def test_generate_symmetric_key():
    from PQencryption import utilities
    symmetric_key = utilities.generate_symmetric_key()
    print(symmetric_key)

if __name__ == "__main__":
    #test_hashing_PyNaCl()

    #test_hashing_hashlib()

    #test_AES256()

    #test_salsa20_256_PyNaCl()

    #test_generate_signing_key()

    #test_generate_symmetric_key()

    #path, signing_key, s_name, verify_key, v_name = test_export_key()
    #test_import_key(path, signing_key, s_name, verify_key, v_name)

    #test_quantum_vulnerable_signing()

    #test_quantum_vulnerable_encryption()
