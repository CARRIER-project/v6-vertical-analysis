#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This script is to read the anaylsis model file and sign the file. Signed file will be sent to TSE (URL)
or saved locally

"""

import time
start_time = time.time()
import base64
import nacl.encoding
import PQencryption as cr
import requests, yaml, sys
import redacted_logging as rlog
from PQencryption.eddsa import EdDSA

def load_yaml_file(file_name, logger):
    """loads a yaml file, logs to logger if errors occur

    Args:
        file_name (str): File name of the YAML file to be loaded.
        logger (logging.Logger): Logger class handling log messages.

    Raises:
        FileNotFoundError: If the yaml file can not be found.

    Returns:
        dict: yaml file content as a dictionary.
    """
    try:
        with open(file_name) as file:
            inputYAML = yaml.load(file, Loader=yaml.FullLoader)
            logger.debug("Reading encrypt_input.yaml file...")
    except yaml.parser.ParserError:
        logger.error(f"File {file} is not valid YAML.")
        raise
    except FileNotFoundError:
        logger.error(f"Trying to read file '{file}', but it does not exist.")
        raise

    return inputYAML



def save_signed_model_file(signed_models, local_save, receiver_address, party_name, model, logger):
    """send the signed_model file to TSE(URL)
        or save it locally 

    Args:
        signed_model (str): signed model file.

    Raises:
       errors in sending or saving file procedure

    Returns:
        Nothing
    """

    ### Send or save encrypted data file ###
    # Send file to TTP service
    if receiver_address != False:
        #save encrypted file temporarily
        wb_model_file = open("/output/%s_%s.enc" %(party_name, model), "w")
        wb_model_file.write(signed_models)
        wb_model_file.close()

        # Send data file #
        try: 
            res = requests.post(url=receiver_address+'/addFile',
                files={"fileObj": open("/output/%s_%s.enc" %(party_name, model), 'r')})
            #get the uuid of the stored file at TTP
            resultJson = json.loads(res.text.encode("utf-8"))
            saved_status = resultJson["status"]
            saved_uuid = resultJson["uuid"]
        except:
            logger.error("Failed to send files to %s" %receiver_address)
            raise


    # Save signed model file locally #
    if local_save:
        try:
            output_model = open("/output/%s_%s.enc" %(party_name, model), "w")
            output_model.write(signed_models)
            output_model.close()
        except:
            logger.error("Failed to seve files locally")
            raise


def main():
    """main function
    The main function will import all model files and sign them by using signing key
    """

    logger = rlog.get_logger(__name__)
    input_yaml_file_name = r'/inputVolume/sign_model_input.yaml'
    inputYAML = load_yaml_file(input_yaml_file_name, logger)

    try:
        party_name = inputYAML['party_name']
        model_files = inputYAML['model_files']
        signing_key_yaml = inputYAML['signing_key']
        local_save = inputYAML['local_save']
        receiver_address = inputYAML['receiver_address']
        
    except KeyError:
        logger.error("YAML file not valid. Please consult the example " +
                        "'sign_model_input.yaml' file and edit in your settings.")

    verKey_list = []

    for model in model_files:
        try:
            # Read model files #
            myModel = open('/inputVolume/'+model, 'r').read()
        except FileNotFoundError:
            logger.error("Cannot find model file %s" %str(model))
        except:
            logger.error("Error occurs when reading %s" %str(model)) 
            raise

        ### Import signing key for model files ###
        try:
            path = '/inputVolume/'
            signing_key = cr.import_key(path + signing_key_yaml, silent=False)
            signing_cipher = EdDSA(signing_key)
            
            signed_models = signing_cipher.sign(myModel)
            save_signed_model_file(signed_models, local_save, receiver_address, party_name, model, logger)

            logger.info("Siging model files took {runtime:.4f}s to run".format(runtime=time.time() - start_time))
        except:
            logger.error("Signing model file {modelName} failed. ".format(modelName=str(model)))
            raise

if __name__ == "__main__":
    main()