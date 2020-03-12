#######################################
# Generate public keys for data parties
# Generate private keys for TSE
#######################################
import time
start_time = time.time()

# import pp_enc
import PQencryption as cr
import requests, json, yaml, uuid,sys, nacl

import redacted_logging as rlog
logger = rlog.get_logger(__name__)


try:
    #read input file
    with open(r'/inputVolume/genKeys_input.yaml') as file:
        inputYAML = yaml.load(file, Loader=yaml.FullLoader)
        logger.debug("Reading ppkeys_input.yaml file...")
        party_name = inputYAML['party_name']
        local_save = inputYAML['local_save']

except FileNotFoundError:
    logger.error("Cannot find ppkeys_input.yaml file ")

else:
    try:
        if local_save == True:
            path = '/output/'
            ### Signing - verifying key generation ###
            keyset_sv = cr.EdDSA.key_gen()
            logger.debug("Export EdDSA keys ... ...")
            for keyObject in keyset_sv:
                keyObject.export_key(path, party_name, force=True, silent=False)
            
            ### Quantum safe public-private key generation ###
            keyset_qv = cr.DiffieHellman.key_gen()
            logger.debug("Export DiffieHellman keys ... ...")
            for keyObject in keyset_qv:
                keyObject.export_key(path, party_name, force=True, silent=False)
    except:
        logger.error("Public-private key generation failed!")
    else:
        logger.info("Public-private keys generation took {runtime:.4f}s to run".format(runtime=(time.time() - start_time)))