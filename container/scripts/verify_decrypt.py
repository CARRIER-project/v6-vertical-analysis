#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This script is to verify and decrypt the data files and key files.
Signed model files will be also verified for the next step - analysis.
Once the files are successfully verified and decrypted, the file of 
hashed linking features + acutal data will be saved in the Docker 
container for next steps (matching).
"""


import time
start_time = time.time()

import json, yaml, sys
import base64
import shutil
import requests
import nacl.encoding
import PQencryption as cr
import redacted_logging as rlog
from PQencryption.salsa20 import Salsa20Key
from PQencryption.eddsa import EdDSA


def load_yaml_file(file_name, logger):
    """loads a yaml file, logs to logger if errors occur

    Args:
        file_name (str): File name of the YAML file to be loaded.
        logger (logging.Logger): Logger class handling log messages.

    Returns:
        dict: yaml file content as a dictionary.
    """
    try:
        with open(file_name) as file:
            inputYAML = yaml.load(file, Loader=yaml.FullLoader)
            logger.debug("Reading request.yaml file...")
    except yaml.parser.ParserError:
        logger.error(f"File {file} is not valid YAML.")
        raise
    except FileNotFoundError:
        logger.error(f"Trying to read file '{file}', but it does not exist.")
        raise

    return inputYAML



def read_write_encrypted_file(receiver_url, parties, keys_dict, modelNames, logger):
    """ read encrypted data files and signed models files and write to the container

    Args:
        receiver_url (URL/Boolean): request data from URL or read it locally (false).
        parties (list): a list of involving parties.
        keys_dict (dict): a dictionary of all verify and decryption keys.
        modelNames (list/str): one or more model file names.
        logger (logging.Logger): Logger class handling log messages.

    Returns:
        No returns
    """

    if not receiver_url:
        try:
            ### When the files are from local machine ###
            for each_party in parties:
                ### Read encrypted data files from the local machine ###
                fileUUID = keys_dict["%sfileUUID" %(each_party)]
                with open("/inputVolume/"+fileUUID+".enc", 'r') as read_data_file:
                    contents = read_data_file.read()
                ### Write encrypted data files to the docker container ###
                with open("/data/%sData.enc" %(each_party), "w") as write_data_file:
                    write_data_file.write(contents)

                ### Read signed model files ###
                for each_model in modelNames:
                    ### Read signed model files from the local machine ###
                    with open("/inputVolume/%s_%s.enc" %(each_party, each_model), 'r') as read_model_file:
                        contents = read_model_file.read()
                    ### Write signed model files to the docker container ###
                    with open("/%s_%s.enc" %(each_party, each_model), "w") as write_model_file:
                        write_model_file.write(contents)
        except FileNotFoundError:
            logger.error("Please provide the right file UUID number in your YAML Input file.")
        
    else: 

        ### When the files are from an URL ###
        for each_party in parties:
            ### Read encrypted data files from an URL ###
            url = receiver_url+'/file/%s' % keys_dict["%sfileUUID" %(each_party)]
            response = requests.get(url, stream=True)
            with open('/data/%sData.enc' %(each_party), 'w') as out_file:
                shutil.copyfileobj(response.raw, out_file)
            del response
            
            ### Read signed model files from an URL ###
            for each_model in modelNames:
                url = receiver_url+"/file/%s_%s.enc" %(each_party, each_model)####
                response = requests.get(url, stream=True)
                with open("/%s_%s.enc" %(each_party, each_model), 'w') as out_file:
                    shutil.copyfileobj(response.raw, out_file)
                del response


### run decryption and verification on data files ###
def verify_and_decrypt(verifying_key, quantum_safe_secret_key, classic_secret_key, classic_public_key,\
                        decryptKey_, encFile, newFile, logger):
    """ verify-decrypt-verify symmetric key and data file 

    Args:
        verifying_key (str): key string
        quantum_safe_secret_key (str): key string
        classic_secret_key (str): key string
        classic_public_key (str): key string
        decryptKey_ (str): key string
        encFile (str): the path to the encrypted data file
        newFile (str): a path to save the decrypted data file
        logger (logging.Logger): Logger class handling log messages.

    Returns:
        No return
    """
    
    ### Key file verification and decryption (verify-decrypt-verify) ###
    try:
        encryption_key_base64 = cr.verify_decrypt_verify_pubkey(verifying_key, quantum_safe_secret_key, classic_secret_key,\
                                            classic_public_key, decryptKey_)
        encryption_key = Salsa20Key(bytearray(nacl.encoding.Base64Encoder.decode(encryption_key_base64)))
    except:
        logger.error("Failed to verify-decrypt-verify key file.")
        raise

    #read encrypted data
    with open(encFile, 'r') as encrypted_file:
        myStr =encrypted_file.read()

    try:
        ### Use verified and decrypted key to verify and decrypt and verify the data file ### 
        verified_decrypted_verified_message = cr.verify_decrypt_verify_symmetric(verifying_key, encryption_key, myStr)
    except:
        logger.error("Failed to verify-decrypt-verify data file.")
        raise

    #save encrypted file temporarily
    with open(newFile, "w") as text_file:
        text_file.write(verified_decrypted_verified_message)

### run verification on model files ###
def verify_model(verifying_key_list, modelFile_list, newFile, logger):
    """loads a yaml file, logs to logger if errors occur

    Args:
        verifying_key_list (list): a list of verifying keys of all data parties.
        modelFile_list (list): a list of names of model files
        newFile (str): a path to save the verified model file
        logger (logging.Logger): Logger class handling log messages.

    Returns:
        No return
    """
   
    verified_models = []

    for i in range(0, len(verifying_key_list)):
        try:
            #read signed model file
            with open(modelFile_list[i], 'r') as m_file:
                myModel = m_file.read()

            #verify-model
            verified_models.append(EdDSA(verifying_key_list[i]).verify(myModel))

        except FileNotFoundError:
            logger.error("Trying to read model file: %s, but it does not exist." %modelFile_list[i])
        except:
            logger.error("%s model verification failed." %str(i))
            raise
    
    if all(each_model == verified_models[0] for each_model in verified_models):
        logger.debug("%s Signed models has been verified successfully!" %newFile)
    else:
        logger.error("Signed models from all parties are not the same!")
        sys.exit("Execution interrupted!")

    # save verified model file temporarily #
    with open(newFile, "w") as text_file:
        text_file.write(verified_models[0])


def main(): 
    """main function

    The main function will read the configuration file (security_input.yaml), read signed-encrypted-signed 
    data and key files, and import all required keys . 
    Then, symmetric key will be verified-decrypted-verified so that it can be used to verify-decrypt-verify
    the data files. Decrypted data files will be temporarily saved in the Docker container.
    Signed model files will be verified and saved in the Docker container temporarily.
    
    """
    logger = rlog.get_logger(__name__)
    input_yaml_file_name = r'/inputVolume/security_input.yaml'
    inputYAML = load_yaml_file(input_yaml_file_name, logger)


    try:
        parties = inputYAML['parties']
        modelNames = inputYAML["modelNames"]
        receiver_url = inputYAML['receiver_url']

        keys_dict = dict()
        for each_party in parties:
            keys_dict.update({"%sfileUUID" %(each_party): inputYAML["%sfileUUID" %(each_party)]})
            keys_dict.update({"%sencryptKey" %(each_party): inputYAML["%sencryptKey" %(each_party)]})
            
            keys_dict.update({"%sverifying_key" %(each_party): inputYAML["%sverifying_key" %(each_party)]})
            keys_dict.update({"%squantum_safe_secret_key" %(each_party): inputYAML["%squantum_safe_secret_key" %(each_party)]})
            keys_dict.update({"%sclassic_secret_key" %(each_party): inputYAML["%sclassic_secret_key" %(each_party)]})
            keys_dict.update({"%sclassic_public_key" %(each_party): inputYAML["%sclassic_public_key" %(each_party)]})
    except KeyError:
        logger.error("YAML file not valid. Please consult the example " +
                        "'security_input.yaml' file and edit in your settings.")

    read_write_encrypted_file(receiver_url, parties, keys_dict, modelNames, logger)


    #run decryption and verification on data
    key_export_time = 0
    for each_party in parties:
        logger.debug('Verifying %s' %each_party)

        path = '/inputVolume/'
        try:
            verifying_key = cr.import_key(path + keys_dict["%sverifying_key" %(each_party)], silent=False)
            
            logger.info("*** Please input your password for Quantum Safe Secret Key of %s: " %(each_party))
            start_key_export = time.time()
            quantum_safe_secret_key = cr.import_key(path + keys_dict["%squantum_safe_secret_key" %(each_party)], silent=False)
            end_key_export = time.time()
            key_export_time += end_key_export - start_key_export

            start_key_export = time.time()
            logger.info("*** Please input your password for Classic Secret Key of %s: " %(each_party))
            classic_secret_key = cr.import_key(path + keys_dict["%sclassic_secret_key" %(each_party)], silent=False)
            end_key_export = time.time()
            key_export_time += end_key_export - start_key_export
            
            classic_public_key = cr.import_key(path + keys_dict["%sclassic_public_key" %(each_party)], silent=False)
        except:
            logger.error("Failed to import verifying and public-priavte key. Please chekc if keys are in the input folder and give the correct names in the security_input.yaml file.")
            raise

        try:
            verify_and_decrypt(verifying_key, quantum_safe_secret_key, classic_secret_key, classic_public_key,\
                                keys_dict["%sencryptKey" %(each_party)], "/data/%sData.enc" %(each_party), "/data/encrypted_%s.csv" %(each_party), logger)
        except:
            logger.error("Failed to verify and decrypt the data files.")
            raise

    logger.debug("Your signiture is verified and datasets are decrypted!")



    # run verification on model files # 
    modelKeys = {}
    modelFileNames = {}
    for i in range(0, len(modelNames)):
        temp = []
        modelPath = []
        for each_party in parties:
            try:
                key = cr.import_key(path + keys_dict["%sverifying_key" %(each_party)], silent=False)
                temp.append(key)
                modelPath.append("%s_%s.enc" %(each_party, modelNames[i]))
            except:
                logger.error("Failed to import %sverifying_key file" %each_party)
                raise
        modelKeys.update({modelNames[i]:temp})
        modelFileNames.update({modelNames[i]:modelPath})

    try:
        for key_item in modelKeys.keys():
            verify_model(modelKeys[key_item], modelFileNames[key_item], "/scripts/MLmodel.py", logger)
        logger.info("Your model is verified successfully. ")
    except:
        logger.error("Model verification failed!")
        raise

    end_time = time.time()
    run_time = end_time - start_time - key_export_time
    logger.info("Verification and decryption took {runtime:.4f}s to run (excluding key exports)".format(runtime=run_time))


if __name__ == "__main__":
    main()
