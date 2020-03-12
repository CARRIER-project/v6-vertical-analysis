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
import pp_enc

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
        ### Signing + encrypt data files ###
        ####################################
        ### create signing key for data files ###
        signing_key, verify_key = signing_Curve25519_PyNaCl.key_gen()

        verifyBase64 = verify_key.encode(encoder=nacl.encoding.Base64Encoder)

        ### create symmetrical encryption key ###
        encryption_key = salsa20_256_PyNaCl.key_gen()
        encryptionKeyBase64 = base64.b64encode(encryption_key)
    except: 
        logger.error("Failed to create verification and encrpution key!")

    else:
        fileStr = inputYAML['party_name']
        # myStr = open("/data/encrypted_%s.csv" %(fileStr), 'rb').read()
        myStr = open("data_file.csv", 'rb').read()

        try:
            #sign->encrypt->sign procedure
            signed_encrypted_signed_message = utilities.sign_encrypt_sign(myStr, signing_key, encryption_key)

            #save encrypted file temporarily
            text_file = open("/data/%s.enc" %(fileStr), "wb")
            text_file.write(signed_encrypted_signed_message)
            text_file.close()
        except:
            logger.error("Procedure of Sign-encrypt-sign failed!")
        
        else:
            
            # ####################################
            # ### Signing + encrypt model files ##
            # ####################################
            # if inputYAML['model_files'] == False:
            #     logger.info("No model files are signed and sent to TSE!")
            # elif inputYAML['model_files'] != False:
            #     model_files = inputYAML['model_files']
            #     verKey_list = []

            #     for m in model_files:
            #         try:
            #             myModel = open(m, 'rb').read()
                        
            #         except FileNotFoundError:
            #             logger.error("Cannot find model file %s" %str(m))
            #         else:
            #             try:
            #                 ### create signing key for model files ###
            #                 signing_key_model, verify_key_model = signing_Curve25519_PyNaCl.key_gen()
            #                 verifyBase64_model = verify_key_model.encode(encoder=nacl.encoding.Base64Encoder)
                            
            #                 ### Sign the model file ###
            #                 signed_models = utilities.sign_models(myModel, signing_key_model)

            #                 #save signed model file temporarily
            #                 wb_model_file = open("/models/%s.enc" %str(m), "wb")
            #                 wb_model_file.write(signed_models)
            #                 wb_model_file.close()

            #                 verKey_list.append(verifyBase64_model.decode('ascii'))

            #                 if inputYAML['local_save'] == True:
            #                     output_model = open("/output/%s.enc" %(m), "wb")
            #                     output_model.write(signed_models)
            #                     output_model.close()
            #             except:
            #                 logger.error("Signing model file {modelName} failed. ".format(modelName=str(m)))
            #                 sys.exit("Execution interrupted!")

            #########################################################
            # encrypted data and model sending
            #########################################################
            try: 
                # Send file to TTP service
                input_address = inputYAML['receiver_address']
                if input_address != False:
                    # Send data file #
                    res = requests.post(url=input_address+'/addFile',
                        files={"fileObj": open('/data/%s.enc' %(fileStr), 'rb')})
                    #get the uuid of the stored file at TTP
                    resultJson = json.loads(res.text.encode("utf-8"))
                    saved_status = resultJson["status"]
                    saved_uuid = resultJson["uuid"]

                    # # Send model file #
                    # if inputYAML['model_files'] != False:
                    #     model_files = inputYAML['model_files']
                    #     for m in model_files:
                    #         res = requests.post(url=input_address+'/addFile',
                    #                 files={"fileObj": open('/models/%s.enc' %str(m), 'rb')})
                

                # Save data file locally (optional)
                if inputYAML['local_save'] == True:
                    # Save encrypted data file locally #
                    saved_uuid = str(uuid.uuid4())
                    output_file = open("/output/%s.enc" %(saved_uuid), "wb")
                    output_file.write(signed_encrypted_signed_message)
                    output_file.close()
                    logger.info("Encrypted data is successfully saved at local machine.")
                    logger.info("UUID: %s" % saved_uuid)

            except:
                logger.error("Failed to save or send files for TSE")
            else:
                
                # Load the public key
                publicKey = pp_enc.pp_importKey(inputYAML['pubkey_path'])

                ### Save keys files in output folder ###
                result = {
                    "%sfileUUID" %(fileStr): saved_uuid,
                    "%sencryptKey" %(fileStr): pp_enc.pp_encrypt(encryptionKeyBase64.decode('ascii'), publicKey),
                    "%sverifyKey" %(fileStr): pp_enc.pp_encrypt(verifyBase64.decode('ascii'), publicKey)

                }
                with open('output/%s_data_keys.json' %(fileStr), 'w') as fp:
                    json.dump(result, fp)
                logger.info("Your data keys are stored in output folder")


                # model_verKeys = {}
                # model_files = inputYAML['model_files']
                # for i in range(0, len(verKey_list)):
                #     model_verKeys.update({model_files[i] : verKey_list[i]})
                # with open('output/%s_models_keys.json' %(fileStr), 'w') as fp:
                #     json.dump(model_verKeys, fp)
                # logger.info("Your model verification keys are stored in output folder!")

                logger.info("Data encryption program took {runtime:.4f}s to run".format(runtime=time.time() - start_time))