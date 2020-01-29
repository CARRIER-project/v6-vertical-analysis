import time
start_time = time.time()

import requests, json, yaml, uuid,sys

####################################
# encryption part
####################################
from PQencryption.pub_key.pk_signature.quantum_vulnerable import signing_Curve25519_PyNaCl
from PQencryption.pub_key.pk_encryption.quantum_vulnerable import encryption_Curve25519_PyNaCl
from PQencryption.symmetric_encryption import salsa20_256_PyNaCl
from PQencryption import utilities
import nacl.encoding
import base64

import redacted_logging as rlog
logger = rlog.get_logger(__name__)

try:
    #read input file
    with open(r'encrypt_input.yaml') as file:
        inputYAML = yaml.load(file, Loader=yaml.FullLoader)
        logger.info("Reading encrypt_input.yaml file...")
except FileNotFoundError:
    logger.error("Cannot find encrypt_input.yaml file ")

else:
    party_name = inputYAML['party_name']
    model_files = inputYAML['model_files']
    verKey_list = []

    for m in model_files:
        try:
            myModel = open(m, 'rb').read()
            
        except FileNotFoundError:
            logger.error("Cannot find model file %s" %str(m))
            sys.exit("Execution interrupted!")
        except:
            logger.error("Error occurs when reading %s" %str(m)) 
            sys.exit("Execution interrupted!")
        else:
            try:
                ### create signing key for model files ###
                signing_key_model, verify_key_model = signing_Curve25519_PyNaCl.key_gen()
                verifyBase64_model = verify_key_model.encode(encoder=nacl.encoding.Base64Encoder)
                
                ### Sign the model file ###
                signed_models = utilities.sign_models(myModel, signing_key_model)

                #save signed model file temporarily
                wb_model_file = open("/models/%s.enc" %str(m), "wb")
                wb_model_file.write(signed_models)
                wb_model_file.close()

                verKey_list.append(verifyBase64_model.decode('ascii'))

            except:
                logger.error("Signing model file {modelName} failed. ".format(modelName=str(m)))
                sys.exit("Execution interrupted!")
            
            else:
                #############################################
                ##### encrypted data and model sending ######
                #############################################
                try:
                    if inputYAML['local_save'] == True:
                        output_model = open("/output/%s_%s.enc" %(party_name, m), "wb")
                        output_model.write(signed_models)
                        output_model.close()

                    # Send file to TTP service
                    if inputYAML['receiver_address'] != False:
                        input_address = inputYAML['receiver_address']
                        # Send model file #
                        if inputYAML['model_files'] != False:
                            model_files = inputYAML['model_files']
                            for m in model_files:
                                res = requests.post(url=input_address+'/addFile',
                                        files={"fileObj": open('/%s_%s.enc' %(party_name, m), 'rb')})
                except:
                    logger.error("Failed to save or send files for TSE")
                    sys.exit("Execution interrupted!")
    
    ##############################
    ### Save verification keys ###
    ##############################

    model_verKeys = {}
    model_files = inputYAML['model_files']
    for i in range(0, len(verKey_list)):
        model_verKeys.update({model_files[i] : verKey_list[i]})
        with open('output/%s_%s_verKeys.json' %(party_name, model_files[i]), 'w') as fp:
            json.dump(model_verKeys, fp)
    
    logger.info("Your model verification keys are stored in output folder!")

    logger.info("Siging model files took {runtime:.4f}s to run".format(runtime=time.time() - start_time))