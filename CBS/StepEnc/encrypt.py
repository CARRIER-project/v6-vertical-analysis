import time
start_time = time.time()

import requests
import json
import uuid

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
with open('input.json', 'r') as f:
    input = json.load(f)
fileStr = input['party_name']

myStr = open('/data/encrypted_%s.csv' %(fileStr), 'rb').read()

#sign->encrypt->sign procedure
signed_encrypted_signed_message = utilities.sign_encrypt_sign(myStr, signing_key, encryption_key)

#save encrypted file temporarily
text_file = open("/data/%s.enc" %(fileStr), "wb")
text_file.write(signed_encrypted_signed_message)
text_file.close()

#########################################################
# data sending
#########################################################

# Send file to TTP service
input_address = input['receiver_address']
if input_address != False:
    res = requests.post(url=input_address+'/addFile',
        files={"fileObj": open('/data/%s.enc' %(fileStr), 'rb')})

    #get the uuid of the stored file at TTP
    resultJson = json.loads(res.text.encode("utf-8"))
    saved_status = resultJson["status"]
    saved_uuid = resultJson["uuid"]
elif input_address == False:
    saved_status = "Succeed (locally saved)"
    saved_uuid = str(uuid.uuid4())

# Save file locally (optional)
local_save = input['local_save']
if local_save == True:
    output_file = open("/output/%s.enc" %(saved_uuid), "wb")
    output_file.write(signed_encrypted_signed_message)
    output_file.close()

#print output
print("Stored encrypted file as %s" % (saved_status))
print("UUID: %s" % saved_uuid)

result = {
    "%sfileUUID" %(fileStr): saved_uuid,
    "%sencryptKey" %(fileStr): encryptionKeyBase64.decode('ascii'),
    "%sverifyKey" %(fileStr): verifyBase64.decode('ascii')
}

with open('encryption/%s_keys.json' %(fileStr), 'w') as fp:
    json.dump(result, fp)

print("My encryption program took", time.time() - start_time, "to run")