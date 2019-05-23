import requests
import shutil
import json
import os

#read input file
with open('input.txt') as data_file:    
    inputJson = json.load(data_file)

# url = 'http://dockerhost:5001/file/%s' % inputJson["umData"]
# response = requests.get(url, stream=True)
# with open('/data/umData.enc', 'wb') as out_file:
#     shutil.copyfileobj(response.raw, out_file)
# del response

shutil.move(os.path.join("/temp", inputJson["umData"]), "/data/umData.enc")

# url = 'http://dockerhost:5001/file/%s' % inputJson["cbsData"]
# response = requests.get(url, stream=True)
# with open('/data/cbsData.enc', 'wb') as out_file:
#     shutil.copyfileobj(response.raw, out_file)
# del response

shutil.move(os.path.join("/temp", inputJson["cbsData"]), "/data/cbsData.enc")

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
    myStr = open(encFile, 'r').read()

    #verify-decrypt-verify
    verified_decrypted_verified_message = utilities.verify_decrypt_verify(myStr, verify_key, encryption_key)

    #save encrypted file temporarily
    text_file = open(newFile, "w")
    text_file.write(verified_decrypted_verified_message)
    text_file.close()

#run decryption and verify
verify_and_decrypt(inputJson["cbsVerify"], inputJson["cbsKey"], '/data/cbsData.enc', "/data/cbsData.csv")
verify_and_decrypt(inputJson["umVerify"], inputJson["umKey"], '/data/umData.enc', "/data/umData.csv")