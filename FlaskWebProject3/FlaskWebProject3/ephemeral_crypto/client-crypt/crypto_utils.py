from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import base64
import os
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP

def aes_generate_key():
    return AESGCM.generate_key(bit_length=256)

def aes_encrypt(key, plaintext: bytes):
    aesgcm = AESGCM(key)
    iv = os.urandom(12)
    ct = aesgcm.encrypt(iv, plaintext, None)
    return base64.b64encode(iv).decode(), base64.b64encode(ct).decode()

def aes_decrypt(key, iv_b64, ct_b64):
    aesgcm = AESGCM(key)
    iv = base64.b64decode(iv_b64)
    ct = base64.b64decode(ct_b64)
    pt = aesgcm.decrypt(iv, ct, None)
    return pt.decode()

def rsa_encrypt(pub_pem: str, data: bytes):
    pubkey = RSA.import_key(pub_pem)
    cipher = PKCS1_OAEP.new(pubkey)
    enc = cipher.encrypt(data)
    return base64.b64encode(enc).decode()
