import time
start_time = time.time()

import requests, json, yaml, uuid,sys

####################################
# encryption part
####################################
import PQencryption as cr
from PQencryption import utilities
import nacl.encoding
import base64

import redacted_logging as rlog
logger = rlog.get_logger(__name__)

try:
    #read input file
    with open(r'/inputVolume/encrypt_input.yaml') as file:
        inputYAML = yaml.load(file, Loader=yaml.FullLoader)
        logger.debug("Reading encrypt_input.yaml file...")
except FileNotFoundError:
    logger.error("Cannot find encrypt_input.yaml file ")

else:
    try:
    ####################################
    ### Sign + encrypt + sign data files ###
    ####################################
    ### create and reading keys ###

        # symmetric_encryption_key 
        encryption_key = cr.Salsa20.key_gen()
        encryptionKeyBase64 = nacl.encoding.Base64Encoder.encode(bytes(encryption_key.key)).decode("utf-8")

        path = '/inputVolume/'
        # read signing key from itself
        signing_key = cr.import_key(path + inputYAML['signing_key'], silent=False) #importKeys(inputYAML['signing_key'])
        # read quantum safe public key from tse
        quantum_safe_public_key = cr.import_key(path + inputYAML['quantum_safe_public_key'], silent=False) # importKeys(inputYAML['quantum_safe_public_key'])
        # read quantum vulnerable public key from tse
        classic_public_key_tse = cr.import_key(path + inputYAML['classic_public_key_tse'], silent=False) # importKeys(inputYAML['classic_public_key_tse'])
        # read quantum vulnerable private key from itself
        classic_secret_key = cr.import_key(path + inputYAML['classic_private_key'], silent=False) # importKeys(inputYAML['classic_private_key'])
       

    except: 
        logger.error("Failed to create or read keys !")

    else:
        fileStr = inputYAML['party_name']
        myStr = open("/data/encrypted_%s.csv" %(fileStr), 'r').read()

        try:
            #sign->encrypt->sign procedure
            signed_encrypted_signed_message = cr.sign_encrypt_sign_symmetric(signing_key,encryption_key, myStr)
            
            #save encrypted file temporarily
            text_file = open("/data/%s.enc" %(fileStr), "w")
            text_file.write(signed_encrypted_signed_message)
            text_file.close()

        except:
            logger.error("Procedure of Sign-encrypt-sign failed!")
        
        else:

            #########################################################
            # encrypted data and model sending
            #########################################################
            try: 
                # Send file to TTP service
                input_address = inputYAML['receiver_address']
                if input_address != False:
                    # Send data file #
                    res = requests.post(url=input_address+'/addFile',
                        files={"fileObj": open('/data/%s.enc' %(fileStr), 'r')})
                    #get the uuid of the stored file at TTP
                    resultJson = json.loads(res.text.encode("utf-8"))
                    saved_status = resultJson["status"]
                    saved_uuid = resultJson["uuid"]


                # Save data file locally (optional)
                if inputYAML['local_save'] == True:
                    # Save encrypted data file locally #
                    saved_uuid = str(uuid.uuid4())
                    output_file = open("/output/%s.enc" %(saved_uuid), "w")
                    output_file.write(signed_encrypted_signed_message)
                    output_file.close()
                    logger.info("Encrypted data is successfully saved at local machine.")
                    logger.info("UUID: %s" % saved_uuid)

            except:
                logger.error("Failed to save or send files for TSE")
            else:

                ### Save keys files in output folder ###
                result = {
                    "%sfileUUID" %(fileStr): saved_uuid,
                    "%sencryptKey" %(fileStr): cr.sign_encrypt_sign_pubkey(signing_key, quantum_safe_public_key, classic_secret_key, classic_public_key_tse, encryptionKeyBase64)
                }

                with open('output/%s_data_keys.json' %(fileStr), 'w') as fp:
                    json.dump(result, fp)
                logger.info("Your data keys are stored in output folder")

                logger.info("Data encryption program took {runtime:.4f}s to run".format(runtime=time.time() - start_time))