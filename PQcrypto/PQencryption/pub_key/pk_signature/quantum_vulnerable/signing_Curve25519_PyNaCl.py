#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Mon Jul 10 16:26:41 CEST 2017

@author: BMMN
"""

from __future__ import print_function  # make print python3 compatible

import gc  # garbage collector
import nacl.signing
import nacl.encoding

def sign(signing_key, message):
    signed = signing_key.sign(message, encoder=nacl.encoding.HexEncoder)
    verify_key = signing_key.verify_key
    verify_key_hex = verify_key.encode(encoder=nacl.encoding.HexEncoder)
    return signed, verify_key_hex


if __name__ == "__main__":
# This in an example. In production, you would want to read the key from an
# external file or the command line. The key must be 32 bytes long.

# DON'T DO THIS IN PRODUCTION!
    signing_key = nacl.signing.SigningKey.generate()

    message = 'This is my message.'
    print("message  : " + message)

# signing
    signed, verify_key_hex = sign(signing_key, message)
    print("signed: " + signed)
    print("verify_key_hex: " + verify_key_hex)

# verification
    verify_key = nacl.signing.VerifyKey(verify_key_hex,
            encoder=nacl.encoding.HexEncoder)
    print()
    print("verification positive:")
    print(verify_key.verify(signed, encoder=nacl.encoding.HexEncoder))
    print()
    print("verification negative:")
    print(verify_key.verify("0"*len(signed), encoder=nacl.encoding.HexEncoder))

# make sure all memory is flushed after operations
    del signing_key
    del signed
    del message
    del verify_key
    del verify_key_hex
    gc.collect()
