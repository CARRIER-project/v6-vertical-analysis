#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 13 08:46:20 CEST 2017

@author: BMMN
"""

from __future__ import print_function  # make print python3 compatible
import os
import gc  # garbage collection
import mock
import unittest
import PQencryption as cr

temp_path = "./.tmp/"
try:
    os.mkdir(temp_path)
except:
    pass

with open(temp_path + "/README.md", 'w') as f:
    f.write("This directory stores temporary keys for testing.\n")

# list of ciphers for key generation, import-export tests
ciphers = [cr.AES256, cr.McBits, cr.Salsa20, cr.EdDSA, cr.DiffieHellman]


class TestFunctions(unittest.TestCase):
    def test_check_password(self):
        cr._check_password("Aa0!asdfasdfasdfasdf")

        with self.assertRaises(Exception) as e:
            cr._check_password("Aa0!asdfasdfasdfasd")
        self.assertEqual(type(e.exception), ValueError)
        self.assertTrue("too short" in str(e.exception))

        with self.assertRaises(Exception) as e:
            cr._check_password("Aaa!asdfasdfasdfasdf")
        self.assertEqual(type(e.exception), ValueError)
        self.assertTrue("does not contain digits" in str(e.exception))

        with self.assertRaises(Exception) as e:
            cr._check_password("AA0!ASDFASDFASDFASDF")
        self.assertEqual(type(e.exception), ValueError)
        self.assertTrue("does not contain lowercase" in str(e.exception))

        with self.assertRaises(Exception) as e:
            cr._check_password("aa0!asdfasdfasdfasdf")
        self.assertEqual(type(e.exception), ValueError)
        self.assertTrue("does not contain uppercase" in str(e.exception))

        with self.assertRaises(Exception) as e:
            cr._check_password("Aa01asdfasdfasdfasdf")
        self.assertEqual(type(e.exception), ValueError)
        self.assertTrue("does not contain any special" in str(e.exception))

    @mock.patch('getpass.getpass',
            return_value="Aa0!asdfasdfasdfasdf")
    def test_get_password(self, input):
        password = cr._get_password(validate=True,
                print_requirements=False)
        self.assertEqual(password, "Aa0!asdfasdfasdfasdf")

    @mock.patch('getpass.getpass',
            side_effect=["Aa0!asdfasdfasdfasdf", "Aa0!ASDFASDFASDFASDF"])
    def test_get_password_fail(self, input):
        with self.assertRaises(Exception) as e:
            password = cr._get_password(validate=True,
                    print_requirements=False)
        self.assertEqual(type(e.exception), ValueError)
        self.assertTrue("Passwords differ." in str(e.exception))

    def test_hashing(self):
        message = "This is a message. Hash me!"
        hashed = cr.hash512(message)
        self.assertEqual(hashed, "ekHXd/YDKU112ETowqFV9GbxGo3I8UMwcDaHk+XVHsPIuXUWy3Jsv6JrCry+Yu8ugjRL+4DAha2IM4+B/HkXIQ==")

    def test_salthashing(self):
        salt = "a" * 128
        message = "This is a message. Hash me!"
        hashed = cr.salthash(salt, message)
        self.assertEqual(hashed, "q5Cx2pzTqGJadaDgqqpcehSrnd6QBtI8rKxmXMDtvJMJ2MxxWq9xXLytYendsy6seFiB6IC/8ywiEIy1jPaovw==")

    def test_generate_keys(self):
        for cipher in ciphers:
            key_objects = cipher.key_gen()
            if type(key_objects) is not tuple:  # is it just a single key?
                key_objects = [key_objects]
            for key_object in key_objects:
                self.assertEqual(key_object._is_valid(), True)

    def test_symmetric_encryption_AES256(self):
        message = "This is my message."
        key = cr.AES256.key_gen()
        symmetric = cr.AES256(key)

        ciphertext = symmetric.encrypt(message)

        cleartext = symmetric.decrypt(ciphertext)

        self.assertNotEqual(message, ciphertext)
        self.assertEqual(message, cleartext)

    def test_symmetric_encryption_Salsa20(self):
        message = "This is my message."
        key = cr.Salsa20.key_gen()
        symmetric = cr.Salsa20(key)

        ciphertext = symmetric.encrypt(message)

        cleartext = symmetric.decrypt(ciphertext)

        self.assertNotEqual(message, ciphertext)
        self.assertEqual(message, cleartext)

    def test_asymmetric_encryption_Diffie_Hellman_Curve25519(self):
        message = "This is my message."

        secret_key_alice, pub_key_alice = cr.DiffieHellman.key_gen()
        secret_key_bob, pub_key_bob = cr.DiffieHellman.key_gen()

        # make encryption objects with correct keys
        alice_asymmetric = cr.DiffieHellman(secret_key_alice, pub_key_bob)
        bob_asymmetric = cr.DiffieHellman(secret_key_bob, pub_key_alice)

        # try to make encryption objects with wrong keys
        with self.assertRaises(Exception) as wrong_keys:
            wrong_keys = cr.DiffieHellman(pub_key_bob, pub_key_alice)
        self.assertTrue("Box must be created from a PrivateKey and a"
                + " PublicKey" in str(wrong_keys.exception))

        ciphertext = alice_asymmetric.encrypt(message)

        cleartext_1 = alice_asymmetric.decrypt(ciphertext)
        cleartext_2 = bob_asymmetric.decrypt(ciphertext)

        self.assertNotEqual(message, ciphertext)
        self.assertEqual(message, cleartext_1)
        self.assertEqual(message, cleartext_2)

        # test derived key
        derived_public_key = secret_key_alice.public_key
        self.assertEqual(bytes(pub_key_alice.key),
                bytes(derived_public_key.key))
        self.assertEqual(pub_key_alice.key_length,
                derived_public_key.key_length)
        self.assertEqual(pub_key_alice.name, derived_public_key.name)
        self.assertEqual(pub_key_alice.description,
                derived_public_key.description)
        self.assertEqual(pub_key_alice.footer, derived_public_key.footer)
        self.assertEqual(pub_key_alice.security_level,
                derived_public_key.security_level)

    def test_asymmetric_encryption_McBits(self):
        message = "This is my message."
        secret_key, pub_key = cr.McBits.key_gen()
        bob_asymmetric = cr.McBits(pub_key)
        alice_asymmetric = cr.McBits(secret_key)

        ciphertext = bob_asymmetric.encrypt(message)

        cleartext = alice_asymmetric.decrypt(ciphertext)

        self.assertNotEqual(message, ciphertext)
        self.assertEqual(message, cleartext)

    @mock.patch('getpass.getpass',
            return_value="Aa0!asdfasdfasdfasdf")
    def test_key_import_export(self, input):
        owner = "CBS"
        for cipher in ciphers:
            key_objects = cipher.key_gen()
            if type(key_objects) is not tuple:  # is it just a single key?
                key_objects = [key_objects]
            for key_object in key_objects:
                key_object.export_key(temp_path, owner, force=True,
                        silent=True)
                file_name = key_object.name + "_" + owner + ".key"
                imported_key = cr.import_key(temp_path + file_name,
                        silent=True)
                self.assertEqual(bytes(key_object.key),
                        bytes(imported_key.key))
                self.assertEqual(key_object.key_length,
                        imported_key.key_length)
                self.assertEqual(key_object.name, imported_key.name)
                self.assertEqual(key_object.description,
                        imported_key.description)
                self.assertEqual(key_object.footer, imported_key.footer)
                self.assertEqual(key_object.security_level,
                        imported_key.security_level)

    def test_signing_EdDSA_Curve25519(self):
        message = 'This is my message.'
        sign_key, verify_key = cr.EdDSA.key_gen()

        signing = cr.EdDSA(sign_key)
        verifying = cr.EdDSA(verify_key)

        signed_message = signing.sign(message)

        # try wrong keys
        with self.assertRaises(Exception) as wrong_key:
            out = verifying.sign(signed_message)
        self.assertTrue("Key is no EdDSA SigningKey"
                in str(wrong_key.exception))

        with self.assertRaises(Exception) as wrong_key:
            out = signing.verify(signed_message)
        self.assertTrue("Key is no EdDSA VerifyKey"
                in str(wrong_key.exception))

        # verify positive
        out = verifying.verify(signed_message)
        self.assertEqual(message, out)

        # verify negative
        with self.assertRaises(Exception) as bad_signature:
            spoof = "0"*len(signed_message)
            out = verifying.verify(spoof)
        self.assertTrue("Signature was forged or corrupt"
                in str(bad_signature.exception))

        # test derived key
        derived_verify_key = sign_key.verify_key
        self.assertEqual(bytes(verify_key.key), bytes(derived_verify_key.key))
        self.assertEqual(verify_key.key_length, derived_verify_key.key_length)
        self.assertEqual(verify_key.name, derived_verify_key.name)
        self.assertEqual(verify_key.description,
                derived_verify_key.description)
        self.assertEqual(verify_key.footer, derived_verify_key.footer)
        self.assertEqual(verify_key.security_level,
                derived_verify_key.security_level)

if __name__ == "__main__":
    unittest.main(verbosity=2)
