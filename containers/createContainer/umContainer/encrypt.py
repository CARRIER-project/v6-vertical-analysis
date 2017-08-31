import requests
import json

####################################
# encryption part
####################################
from PQencryption.pub_key.pk_signature.quantum_vulnerable import signing_Curve25519_PyNaCl
from PQencryption.pub_key.pk_encryption.quantum_vulnerable import encryption_Curve25519_PyNaCl
from PQencryption.symmetric_encryption import salsa20_256_PyNaCl
from PQencryption import utilities
import nacl.encoding
import base64

#create signing key
signing_key, verify_key = signing_Curve25519_PyNaCl.key_gen()

verifyBase64 = verify_key.encode(encoder=nacl.encoding.Base64Encoder)

#create symmetrical encryption key
encryption_key = salsa20_256_PyNaCl.key_gen()
encryptionKeyBase64 = base64.b64encode(encryption_key)

#read file
myStr = open('/data/dms.csv', 'r').read()

#sign->encrypt->sign procedure
signed_encrypted_signed_message = utilities.sign_encrypt_sign(myStr, signing_key, encryption_key)

#save encrypted file temporarily
text_file = open("/data/dms.enc", "w")
text_file.write(signed_encrypted_signed_message)
text_file.close()

#########################################################
# data sending
#########################################################

#send file to TTP service
res = requests.post(url='http://dockerhost:5001/addFile',
    files={"fileObj": open('/data/dms.enc', 'rb')})

#get the uuid of the stored file at TTP
resultJson = json.loads(res.text.encode("utf-8"))

#print output
print("Stored encrypted file as %s" % (resultJson["status"].encode("utf-8")))
print("UUID: %s" % resultJson["uuid"].encode("utf-8"))

result = {
    "verifyKey": verifyBase64,
    "encryptKey": encryptionKeyBase64,
    "fileUUID": resultJson["uuid"].encode("utf-8")
}

with open('output.txt', 'w') as fp:
    json.dump(result, fp)