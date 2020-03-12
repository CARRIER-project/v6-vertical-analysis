import time
start_time = time.time()

import requests, json, yaml, uuid,sys

####################################
# encryption part
####################################

import PQencryption as cr
import nacl.encoding
import base64

import redacted_logging as rlog
logger = rlog.get_logger(__name__)

try:
    #read input file
    with open(r'/inputVolume/sign_model_input.yaml') as file:
        inputYAML = yaml.load(file, Loader=yaml.FullLoader)
        logger.debug("Reading sign_model_input.yaml file...")
except FileNotFoundError:
    logger.error("Cannot find sign_model_input.yaml file ")

else:
    party_name = inputYAML['party_name']
    model_files = inputYAML['model_files']
    verKey_list = []

    for m in model_files:
        try:
            myModel = open('/inputVolume/'+m, 'r').read()
            
        except FileNotFoundError:
            logger.error("Cannot find model file %s" %str(m))
            sys.exit("Execution interrupted!")
        except:
            logger.error("Error occurs when reading %s" %str(m)) 
            sys.exit("Execution interrupted!")
        else:
            try:
                ### create signing key for model files ###
                path = '/inputVolume/'
                signing_key = cr.import_key(path + inputYAML['signing_key'], silent=False)

                from PQencryption.eddsa import EdDSA
                signing_cipher = EdDSA(signing_key)
                signed_models = signing_cipher.sign(myModel)

                #save signed model file temporarily
                wb_model_file = open("/models/%s.enc" %str(m), "w")
                wb_model_file.write(signed_models)
                wb_model_file.close()


            except:
                logger.error("Signing model file {modelName} failed. ".format(modelName=str(m)))
                sys.exit("Execution interrupted!")
            
            else:
                #############################################
                ##### encrypted data and model sending ######
                #############################################
                try:
                    if inputYAML['local_save'] == True:
                        output_model = open("/output/%s_%s.enc" %(party_name, m), "w")
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
                                        files={"fileObj": open('/%s_%s.enc' %(party_name, m), 'r')})
                except:
                    logger.error("Failed to save or send files for TSE")
                    sys.exit("Execution interrupted!")
    
    ##############################
    ### Save verification keys ###
    ##############################
    
    logger.info("Your model verification keys are stored in output folder!")

    logger.info("Siging model files took {runtime:.4f}s to run".format(runtime=time.time() - start_time))