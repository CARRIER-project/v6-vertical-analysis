#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Generate a public-private key pair as well as a signing key pair for the
Data Party (sender of data) and export them to a file.
"""

import os
import time
import PQencryption as cr
import redacted_logging as rlog


KEY_OUTPUT_PATH = "/output/"


def main():
    """Generate a quantum-vulnerable encryption key pair and a
    quantum-vulnerable signing-verify key pair and exports them to an output
    folder. Their configuration is read from an environment variable.

    Raises:
        KeyError: If the environment variable can not be found.
    """
    start_time = time.time()
    key_export_time = 0
    logger = rlog.get_logger(__name__)

    try:
        party_name = os.environ["PARTY_NAME"]
    except KeyError:
        logger.error("No environment variable 'PARTY_NAME' set. Please run "
                     "docker with '-e PARTY_NAME=\"your_party_name\"'.")
        raise

    # Sign-verify key generation
    keyset_sign_verify = cr.EdDSA.key_gen()
    logger.info("Export EdDSA keys ... ...")
    for key_object in keyset_sign_verify:
        start_key_export = time.time()
        key_object.export_key(KEY_OUTPUT_PATH, party_name,
                              force=True, silent=False)
        end_key_export = time.time()
        key_export_time += end_key_export - start_key_export

    # Quantum vulnerable public-private key generation
    keyset_quantum_vulnerable_pub_priv = cr.DiffieHellman.key_gen()
    logger.info("Export DiffieHellman keys ... ...")
    for key_object in keyset_quantum_vulnerable_pub_priv:
        start_key_export = time.time()
        key_object.export_key(KEY_OUTPUT_PATH, party_name,
                              force=True, silent=False)
        end_key_export = time.time()
        key_export_time += end_key_export - start_key_export

    end_time = time.time()
    run_time = end_time - start_time - key_export_time
    logger.info(f"Signing-verify key generation and public-private-key " +
                f"generation took {run_time:.4f}s to run. (excluding key " +
                f"exports)")


if __name__ == "__main__":
    main()
