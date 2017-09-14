#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Fri Jul  7 16:36:41 CEST 2017

@author: BMMN
"""

from __future__ import print_function  # make print python3 compatible

import nacl.encoding
import nacl.hash


def salthash(salt, string):
    """SHA 512 hashing with salt using PyNaCl.

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

    return nacl.hash.sha512(salt.encode("utf-8") + string.encode("utf-8"), encoder=nacl.encoding.HexEncoder).decode("utf-8")

if __name__ == "__main__":
    import gc  # garbage collector
    # In production the salt should come from a hardware random number generator
    # and will be shared between parties. Salt must be 128 bytes in hex.
    salt = "a" * 128

    message = "This is a message. Hash me!"
    print(message)

    hashed = hash(salt, message)
    print(hashed)

    # make sure all memory is flushed after operations
    del salt
    del message
    gc.collect()
