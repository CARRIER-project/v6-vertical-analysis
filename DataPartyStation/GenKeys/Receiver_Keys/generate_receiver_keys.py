#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Generate a public-private key pair as well as a signing key pair for the
Data Party (sender of data) and export them to a file.
"""

import time
import yaml
import PQencryption as cr
import redacted_logging as rlog


KEYGEN_INPUT_FILE = "/inputVolume/genKeys_input.yaml"
KEY_OUTPUT_PATH = "/output/"


def main():
    """Generate a quantum-vulnerable encryption key pair and a
    quantum-vulnerable signing-verify key pair and exports them to an output
    folder. Their configuration is read from a yaml file.

    Raises:
        FileNotFoundError: If the yaml config file can not be found.
    """
    start_time = time.time()
    logger = rlog.get_logger(__name__)

    try:
        with open(KEYGEN_INPUT_FILE) as file:
            input_yaml = yaml.load(file, Loader=yaml.FullLoader)
            logger.debug(f"Reading '{KEYGEN_INPUT_FILE}'.")
    except FileNotFoundError:
        logger.error("Cannot find ppkeys_input.yaml file ")

    party_name = input_yaml['party_name']

    # Sign-verify key generation
    keyset_sign_verify = cr.EdDSA.key_gen()
    logger.debug("Export EdDSA keys ... ...")
    for key_object in keyset_sign_verify:
        key_object.export_key(KEY_OUTPUT_PATH, party_name,
                              force=True, silent=False)

    # Quantum vulnerable public-private key generation
    keyset_quantum_vulnerable_pub_priv = cr.DiffieHellman.key_gen()
    logger.debug("Export DiffieHellman keys ... ...")
    for key_object in keyset_quantum_vulnerable_pub_priv:
        key_object.export_key(KEY_OUTPUT_PATH, party_name,
                              force=True, silent=False)

    end_time = time.time()
    run_time = end_time - start_time
    logger.info(f"Signing-verify key generation and public-private-key " +
                f"generation took {run_time:.4f}s to run.")


if __name__ == "__main__":
    main()
