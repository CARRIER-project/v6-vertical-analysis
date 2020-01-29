import time
start_time = time.time()

import json, yaml, sys
import shutil
import requests
import redacted_logging as rlog
logger = rlog.get_logger(__name__)

#read input file
try:
    with open(r'security_input.yaml') as file:
        inputYAML = yaml.load(file, Loader=yaml.FullLoader)
        logger.info("Reading request.yaml file...")

    parties = inputYAML['parties']
    modelNames = inputYAML["modelNames"]

    receiver_url = inputYAML['receiver_url']
    if receiver_url != False:
        ### Read encrypted data files ###
        for p in parties:
            url = receiver_url+'/file/%s' % inputYAML["%sfileUUID" %(p)]
            response = requests.get(url, stream=True)
            with open('/data/%sData.enc' %(p), 'wb') as out_file:
                shutil.copyfileobj(response.raw, out_file)
            del response
        
            ### Read signed model files ###
        for m in modelNames:
            for p in parties:
                url = receiver_url+"/file/%s_%s.enc" %(p,m)####
                response = requests.get(url, stream=True)
                with open("/%s_%s.enc" %(p, m), 'wb') as out_file:
                    shutil.copyfileobj(response.raw, out_file)
                del response

    elif receiver_url == False:
        ### Read encrypted data files ###
        for p in parties:
            fileUUID = inputYAML["%sfileUUID" %(p)]
            with open("/input/"+fileUUID+".enc", 'rb') as f:
                contents = f.read()
            contents_file = open("/data/%sData.enc" %(p), "wb")
            contents_file.write(contents)
            contents_file.close()

        ### Read signed model files ###
        for m in modelNames:
            for p in parties:
                with open("/input/%s_%s.enc" %(p,m), 'rb') as f:
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
    from PQencryption.pub_key.pk_signature.quantum_vulnerable import signing_Curve25519_PyNaCl
    from PQencryption.pub_key.pk_encryption.quantum_vulnerable import encryption_Curve25519_PyNaCl
    from PQencryption.symmetric_encryption import salsa20_256_PyNaCl
    from PQencryption import utilities
    import nacl.encoding
    import base64

    ### run decryption and verification on data files ###
    def verify_and_decrypt(verifyBase64, decryptKey, encFile, newFile):
        #create signing key
        verify_key = nacl.signing.VerifyKey(verifyBase64, encoder=nacl.encoding.Base64Encoder)

        #create symmetrical encryption key
        encryption_key= base64.b64decode(decryptKey)

        #read encrypted data
        with open(encFile, 'rb') as encrypted_file:
            myStr =encrypted_file.read()

        #verify-decrypt-verify
        verified_decrypted_verified_message = utilities.verify_decrypt_verify(myStr, verify_key, encryption_key)

        #save encrypted file temporarily
        with open(newFile, "wb") as text_file:
            text_file.write(verified_decrypted_verified_message)

    ### run verification on model files ###
    def verify_model(verifyBase64_list, modelFile_list, newFile):
        verified_models = []

        for i in range(0, len(verifyBase64_list)):
            # try:
            verify_key_model = nacl.signing.VerifyKey(verifyBase64_list[i], encoder=nacl.encoding.Base64Encoder)

            #read signed model file
            with open(modelFile_list[i], 'rb') as m_file:
                myModel = m_file.read()

            #verify-model
            verified_models.append(utilities.verify_models(myModel, verify_key_model))
            # except:
            #     logger.error("%s model verification failed." %str(i))
            
        if all(m == verified_models[0] for m in verified_models):
            logger.info("Signed models has been verified successfully!")
        else:
            logger.error("Signed models from all parties are not the same!")
            sys.exit("Execution interrupted!")

        # save verified model file temporarily #
        with open(newFile, "wb") as text_file:
            text_file.write(verified_models[0])


    #run decryption and verification on data
    try:
        for p in parties:
            logger.debug('Verifying %s' %p)
            verify_and_decrypt(inputYAML["%sverifyKey" %(p)], inputYAML["%sencryptKey" %(p)], '/data/%sData.enc' %(p), "/data/encrypted_%s.csv" %(p) )
        logger.debug("Your signiture is verified and datasets are decrypted!")
    except:
        logger.error("Verification and decrption failed. Please check all your keys")
        sys.exit("Execution interrupted!")

    # run verification on model files # 

    modelKeys = {}
    modelFileNames = {}
    for i in range(0, len(modelNames)):
        temp = []
        modelPath = []
        for p in parties:
            keys = inputYAML["%sModelKey" %(p)]
            temp.append(keys[i])
            modelPath.append("/%s_%s.enc" %(p,modelNames[i]))
        modelKeys.update({modelNames[i]:temp})
        modelFileNames.update({modelNames[i]:modelPath})

    try:
        for m in modelKeys.keys():
            verify_model(modelKeys[m], modelFileNames[m], "/MLmodel.py")
    except:
        logger.error("Model verification failed!")
    else:
        logger.info("Verification and decryption took {runtime:.4f}s to run".format(runtime=(time.time() - start_time)))
