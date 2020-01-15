import time
start_time = time.time()

import json
import shutil
import requests
import redacted_logging as rlog
logger = rlog.get_logger(__name__)

#read input file
try:
    with open('security_input.json') as data_file:    
        inputJson = json.load(data_file)
    parties = inputJson['parties']
    
    receiver_url = inputJson['receiver_url']
    if receiver_url != False:
        for p in parties:
            url = receiver_url+'/file/%s' % inputJson["%sfileUUID" %(p)]
            response = requests.get(url, stream=True)
            with open('/data/%sData.enc' %(p), 'wb') as out_file:
                shutil.copyfileobj(response.raw, out_file)
            del response
    elif receiver_url == False:
        for p in parties:
            fileUUID = inputJson["%sfileUUID" %(p)]
            with open("/input/"+fileUUID+".enc", 'rb') as f:
                contents = f.read()
            contents_file = open("/data/%sData.enc" %(p), "wb")
            contents_file.write(contents)
            contents_file.close()

except FileNotFoundError:
    logger.error("Please provide the right keys in your JSON Input file, and mount correctly to 'security_input.josn' in container.")
    

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


    #run decryption and verify
    try:
        for p in parties:
            logger.debug('Verifying %s' %p)
            verify_and_decrypt(inputJson["%sverifyKey" %(p)], inputJson["%sencryptKey" %(p)], '/data/%sData.enc' %(p), "/data/encrypted_%s.csv" %(p) )
    except:
        logger.error("Verification and decrption failed. Please check all your keys")

    else:
        logger.debug("Your signiture is verified and datasets are decrypted!")
        logger.info("Verification and decryption took {runtime:.4f}s to run".format(runtime=(time.time() - start_time)))
