#######################################
# Generate public keys for data parties
# Generate private keys for TSE
#######################################
import time
start_time = time.time()

import pp_enc
import requests, json, yaml, uuid,sys

import redacted_logging as rlog
logger = rlog.get_logger(__name__)

try:
    #read input file
    with open(r'/inputVolume/ppkeys_input.yaml') as file:
        inputYAML = yaml.load(file, Loader=yaml.FullLoader)
        logger.debug("Reading ppkeys_input.yaml file...")
        party_name = inputYAML['party_name']
        local_save = inputYAML['local_save']
        try:
            bits = int(inputYAML['bits'])
        except:
            logger.error("Key length (bits) has to be integer!")
except FileNotFoundError:
    logger.error("Cannot find ppkeys_input.yaml file ")

else:
    try:
        if local_save == True:
            privateKey = pp_enc.pp_generatePrivateKey(bits, '/output/privateKey_%s.pem' %(party_name)) ### For decryption, TSE
            pp_enc.pp_generatePublicKey(privateKey, '/output/publicKey_%s.pem' %(party_name))### For encryption, data parties
    except:
        logger.error("Public-private key generation failed!")
    else:
        logger.info("Public-private keys generation took {runtime:.4f}s to run".format(runtime=(time.time() - start_time)))
