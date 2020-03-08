#######################################
# requires Crypto library
# install using "pip install pycrypto"
#######################################

from Crypto import Random
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
import base64

random_generator = Random.new().read

def pp_generatePrivateKey(multiplierBits, fileName):
    privateKey = RSA.generate(2048*multiplierBits)
    f = open(fileName, 'w')
    f.write(privateKey.exportKey('PEM').decode("UTF-8"))
    f.close()
    return privateKey

def pp_generatePublicKey(privateKey, fileName):
    f = open(fileName, 'w')
    f.write(privateKey.publickey().exportKey('PEM').decode("UTF-8"))
    f.close()
    # return privateKey.publickey()

# def pp_exportKey(key, fileName):
#     f = open(fileName, 'w')
#     f.write(key.exportKey('PEM').decode("UTF-8"))
#     f.close()

def pp_importKey(fileName):
    f = open(fileName, 'r')
    key = RSA.importKey(f.read())
    return key

def pp_encrypt(text, publicKey):
    if publicKey.has_private():
        raise Exception("Private key used for encryption")
    
    cipher = PKCS1_OAEP.new(publicKey)
    encrypted = cipher.encrypt(text.encode())
    encryptedBase64 = base64.b64encode(encrypted).decode("UTF-8")
    return encryptedBase64

def pp_decrypt(encryptedString, privateKey):
    if not privateKey.has_private():
        raise Exception("Wrong key used for decryption, please use private key")
    encrypted = base64.b64decode(encryptedString)
    cipher = PKCS1_OAEP.new(privateKey)
    decryptedText = cipher.decrypt(encrypted).decode("UTF-8")
    return decryptedText