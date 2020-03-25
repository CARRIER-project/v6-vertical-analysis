#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Generate quantum-vulnerable and quantum-safe public-private key pairs for the
TSE (receiver of data) and export them to a file.
"""

import time
import yaml
import PQencryption as cr
import redacted_logging as rlog


KEYGEN_INPUT_FILE = "/inputVolume/genKeys_input.yaml"
KEY_OUTPUT_PATH = "/output/"


def main():
    """Generate quantum-safe- and quantum-vulnerable public-private key pairs
    and exports them to an output folder. Their configuration is read from
    a yaml file.

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
        logger.error(f"Cannot find '{KEYGEN_INPUT_FILE}'.")
        raise

    party_name = input_yaml['party_name']

    # Quantum safe public-private key generation
    keyset_quantum_safe_sign_verify = cr.McBits.key_gen()
    logger.debug("Exporting McBits keys to folder " +
                 "'{KEY_OUTPUT_PATH}'.")
    for key_object in keyset_quantum_safe_sign_verify:
        key_object.export_key(KEY_OUTPUT_PATH, party_name,
                              force=True, silent=False)

    # Quantum vulnerable public-private key generation
    keyset_quantum_vulnerable_pub_priv = cr.DiffieHellman.key_gen()
    logger.debug("Export Diffie Hellman keys to folder " +
                 "'{KEY_OUTPUT_PATH}'.")
    for key_object in keyset_quantum_vulnerable_pub_priv:
        key_object.export_key(KEY_OUTPUT_PATH, party_name,
                              force=True, silent=False)

    end_time = time.time()
    logger.info("Public-private keys generation took {runtime:.4f}s to " +
                "run.".format(runtime=(end_time - start_time)))


if __name__ == "__main__":
    main()
