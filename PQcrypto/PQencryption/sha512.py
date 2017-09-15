#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on 4 jul 2017 16:24:30 CEST

@author: BMMN

SHA 512 hashlib
"""

from __future__ import print_function  # make print python3 compatible

import hashlib
import nacl.encoding

def hash512(string):
    return nacl.encoding.Base64Encoder.encode(
            hashlib.sha512(string.encode("utf-8")).digest()).decode("utf-8")

def salthash(salt, string):
    """SHA 512 hashing with salt, using hashlib.

    Args:
        salt (str): (random) string of length 128
        string (str): arbitrary length string
    Returns:
        hashed 'salt + string'
    Raises:
        ValueError: if salt is not of length 128
    """
    if len(salt) != 128:
        raise ValueError('Salt must be 128 bytes long.')

    return hash512(salt + string)

if __name__ == "__main__":
    import gc  # garbage collector

    # In production the salt should come from a hardware random number generator
    # and will be shared between parties. Salt must be 128 bytes in base64.
    salt = "a" * 128

    message = "This is a message. Hash me!"
    print(message)

    hashed = hash(salt, message)
    print(hashed)

    # make sure all memory is flushed after operations
    del salt
    del message
    gc.collect()
