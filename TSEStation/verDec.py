import time
start_time = time.time()

import json, yaml, sys
import shutil
import requests
import redacted_logging as rlog
logger = rlog.get_logger(__name__)

#read input file
try:
    with open(r'/inputVolume/security_input.yaml') as file:
        inputYAML = yaml.load(file, Loader=yaml.FullLoader)
        logger.debug("Reading request.yaml file...")

    parties = inputYAML['parties']
    modelNames = inputYAML["modelNames"]

    receiver_url = inputYAML['receiver_url']
    if receiver_url != False:
        ### Read encrypted data files ###
        for p in parties:
            url = receiver_url+'/file/%s' % inputYAML["%sfileUUID" %(p)]
            response = requests.get(url, stream=True)
            with open('/data/%sData.enc' %(p), 'w') as out_file:
                shutil.copyfileobj(response.raw, out_file)
            del response
        
            ### Read signed model files ###
        for m in modelNames:
            for p in parties:
                url = receiver_url+"/file/%s_%s.enc" %(p,m)####
                response = requests.get(url, stream=True)
                with open("/%s_%s.enc" %(p, m), 'w') as out_file:
                    shutil.copyfileobj(response.raw, out_file)
                del response

    elif receiver_url == False:
        ### Read encrypted data files ###
        for p in parties:
            fileUUID = inputYAML["%sfileUUID" %(p)]
            with open("/inputVolume/"+fileUUID+".enc", 'rb') as f:
                contents = f.read()
            contents_file = open("/data/%sData.enc" %(p), "wb")
            contents_file.write(contents)
            contents_file.close()

        ### Read signed model files ###
        for m in modelNames:
            for p in parties:
                with open("/inputVolume/%s_%s.enc" %(p,m), 'rb') as f:
                    contents = f.read()
                contents_file = open("/%s_%s.enc" %(p, m), "wb")
                contents_file.write(contents)
                contents_file.close()

except FileNotFoundError:
    logger.error("Please provide the right keys in your YAML Input file, and mount correctly to 'security_input.yaml' in container.")
    sys.exit("Execution interrupted!")
    

else:
    ####################################
    # decryption part
    ####################################

    # from PQencryption import utilities
    import PQencryption as cr
    import nacl.encoding
    import base64


    ### run decryption and verification on data files ###
    def verify_and_decrypt(verifying_key, quantum_safe_secret_key, classic_secret_key, classic_public_key_dataParty,\
                            decryptKey_, encFile, newFile):
        
        # # read verification key #
        from PQencryption.salsa20 import Salsa20Key
        encryption_key_base64 = cr.verify_decrypt_verify_pubkey(verifying_key, quantum_safe_secret_key, classic_secret_key,\
                                            classic_public_key_dataParty, decryptKey_)
        encryption_key = Salsa20Key(bytearray(nacl.encoding.Base64Encoder.decode(encryption_key_base64)))


        #read encrypted data
        with open(encFile, 'r') as encrypted_file:
            myStr =encrypted_file.read()

        #verify-decrypt-verify
        verified_decrypted_verified_message = cr.verify_decrypt_verify_symmetric(verifying_key, encryption_key, myStr)

        #save encrypted file temporarily
        with open(newFile, "w") as text_file:
            text_file.write(verified_decrypted_verified_message)

    ### run verification on model files ###
    def verify_model(verifying_key_list, modelFile_list, newFile):
        verified_models = []

        for i in range(0, len(verifying_key_list)):
            try:
       
                #read signed model file
                with open(modelFile_list[i], 'r') as m_file:
                    myModel = m_file.read()

                #verify-model
                from PQencryption.eddsa import EdDSA, EdDSAVerifyKey

                verified_models.append(EdDSA(verifying_key_list[i]).verify(myModel))

            except:
                logger.error("%s model verification failed." %str(i))
                sys.exit("Execution interrupted!")

            
        if all(m == verified_models[0] for m in verified_models):
            logger.info("Signed models has been verified successfully!")
        else:
            logger.error("Signed models from all parties are not the same!")
            sys.exit("Execution interrupted!")

        # save verified model file temporarily #
        with open(newFile, "w") as text_file:
            text_file.write(verified_models[0])


    #run decryption and verification on data
    try:
        for p in parties:
            logger.debug('Verifying %s' %p)

            path = '/inputVolume/'
            verifying_key = cr.import_key(path + inputYAML["%sverifying_key" %(p)], silent=False)
            quantum_safe_secret_key = cr.import_key(path + inputYAML["%squantum_safe_secret_key" %(p)], silent=False)
            classic_secret_key = cr.import_key(path + inputYAML["%sclassic_secret_key" %(p)], silent=False)
            classic_public_key_dataParty = cr.import_key(path + inputYAML["%sclassic_public_key_dataParty" %(p)], silent=False)


            verify_and_decrypt(verifying_key, quantum_safe_secret_key, classic_secret_key, classic_public_key_dataParty,\
                                inputYAML["%sencryptKey" %(p)], "/data/%sData.enc" %(p), "/data/encrypted_%s.csv" %(p))

        logger.debug("Your signiture is verified and datasets are decrypted!")

    except:
        logger.error("Verification and decrption failed. Please check all your keys")
        sys.exit("Execution interrupted!")

    else: 
        # run verification on model files # 
        modelKeys = {}
        modelFileNames = {}
        for i in range(0, len(modelNames)):
            temp = []
            modelPath = []
            for p in parties:
                key = cr.import_key(path + inputYAML["%sverifying_key" %(p)], silent=False)
                temp.append(key)
                modelPath.append("%s_%s.enc" %(p,modelNames[i]))
            modelKeys.update({modelNames[i]:temp})
            modelFileNames.update({modelNames[i]:modelPath})

        try:
            for m in modelKeys.keys():
                verify_model(modelKeys[m], modelFileNames[m], "/MLmodel.py")
        except:
            logger.error("Model verification failed!")
        else:
            logger.info("Verification and decryption took {runtime:.4f}s to run".format(runtime=(time.time() - start_time)))
