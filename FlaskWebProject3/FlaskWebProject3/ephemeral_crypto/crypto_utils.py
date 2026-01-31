
"""
crypto_utils.py - Cryptographic utilities for secure session management
"""
import os
import base64
import uuid
import time
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

SESSION_TTL_SECONDS = 60 * 60  # 60 min (was 10 min) - fewer expiry issues for long-running restore flows
RSA_HANDSHAKE_LIFETIME = 2 * 60


def gen_rsa_keypair(key_size=2048):
    """
    Generate RSA key pair for handshake encryption.
    
    Returns:
        tuple: (private_key_pem, public_key_pem) as bytes
    """
    priv = rsa.generate_private_key(public_exponent=65537, key_size=key_size)
    pub = priv.public_key()
    
    priv_pem = priv.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    )
    pub_pem = pub.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    return priv_pem, pub_pem


def rsa_decrypt(priv_pem: bytes, ciphertext_b64: str) -> bytes:
    """
    Decrypt RSA-encrypted AES key.
    
    Args:
        priv_pem: Private key in PEM format
        ciphertext_b64: Base64-encoded ciphertext
        
    Returns:
        bytes: Decrypted AES key
    """
    private_key = serialization.load_pem_private_key(priv_pem, password=None)
    ciphertext = base64.b64decode(ciphertext_b64)
    return private_key.decrypt(ciphertext, padding.PKCS1v15())


def aes_encrypt(aes_key: bytes, plaintext_bytes: bytes):
    """
    Encrypt data using AES-GCM.
    
    Args:
        aes_key: 32-byte AES key
        plaintext_bytes: Data to encrypt
        
    Returns:
        dict: {'iv': base64_string, 'ct': base64_string}
              where 'ct' contains ciphertext + authentication tag
    """
    aesgcm = AESGCM(aes_key)
    iv = os.urandom(12)
    ct_and_tag = aesgcm.encrypt(iv, plaintext_bytes, None)
    
    return {
        "iv": base64.b64encode(iv).decode(),
        "ct": base64.b64encode(ct_and_tag).decode(),
    }


def aes_decrypt(aes_key: bytes, iv_b64: str, ct_b64: str, tag_b64: str = None) -> bytes:
    """
    Decrypt AES-GCM encrypted data.
    
    Args:
        aes_key: 32-byte AES key
        iv_b64: Base64-encoded initialization vector
        ct_b64: Base64-encoded ciphertext (with or without tag)
        tag_b64: Optional base64-encoded authentication tag (for backward compatibility)
        
    Returns:
        bytes: Decrypted plaintext
    """
    aesgcm = AESGCM(aes_key)
    iv = base64.b64decode(iv_b64)
    
    if tag_b64 is not None:
        ct = base64.b64decode(ct_b64)
        tag = base64.b64decode(tag_b64)
        ciphertext_with_tag = ct + tag
    else:
        ciphertext_with_tag = base64.b64decode(ct_b64)
    
    return aesgcm.decrypt(iv, ciphertext_with_tag, None)


def make_key_id() -> str:
    """Generate unique session key identifier."""
    return str(uuid.uuid4())


def now_ts() -> float:
    """Get current Unix timestamp."""
    return time.time()