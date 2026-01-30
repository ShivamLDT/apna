## as like axios interceptor client side code
'''
from crypto_client import CryptoClient

client = CryptoClient("http://localhost:5000")

# POST encrypted request
response = client.post("/secure-data", json_data={"msg": "hello world"})
print("Decrypted response:", response)

# GET request with encrypted headers
response = client.get("/secure-status", headers={"User-Agent": "MyCryptoClient/1.0"})
print("Decrypted GET:", response)


'''

import requests
import json
import base64
import time
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.backends import default_backend
import os


class CryptoClient:
    def __init__(self, base_url):
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.key_id = None
        self.aes_key = None
        self.aes_key_expires = 0

    def _gen_aes_key(self):
        return AESGCM.generate_key(bit_length=256)

    def _rsa_encrypt(self, pub_pem: str, plaintext: bytes) -> str:
        pub_key = serialization.load_pem_public_key(pub_pem.encode(), backend=default_backend())
        encrypted = pub_key.encrypt(
            plaintext,
            padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)
        )
        return base64.b64encode(encrypted).decode()

    def _aes_encrypt(self, key: bytes, data: bytes) -> dict:
        aesgcm = AESGCM(key)
        iv = os.urandom(12)
        ct = aesgcm.encrypt(iv, data, None)
        return {
            "iv": base64.b64encode(iv).decode(),
            "ct": base64.b64encode(ct).decode()
        }

    def _aes_decrypt(self, key: bytes, iv_b64: str, ct_b64: str) -> bytes:
        aesgcm = AESGCM(key)
        iv = base64.b64decode(iv_b64)
        ct = base64.b64decode(ct_b64)
        return aesgcm.decrypt(iv, ct, None)

    def _handshake(self):
        """Performs handshake and establishes AES session."""
        # 1. Get RSA pub key from server
        resp = self.session.get(f"{self.base_url}/handshake")
        resp.raise_for_status()
        data = resp.json()
        key_id = data["key_id"]
        pub_pem = data["pub_pem"]

        # 2. Generate AES key and encrypt it with RSA
        aes_key = self._gen_aes_key()
        encrypted_aes = self._rsa_encrypt(pub_pem, aes_key)

        # 3. Confirm with server
        resp = self.session.post(f"{self.base_url}/handshake/confirm", json={
            "key_id": key_id,
            "enc_aes_b64": encrypted_aes
        })
        resp.raise_for_status()
        confirm = resp.json()

        if not confirm.get("ok"):
            raise Exception("Handshake failed")

        self.key_id = key_id
        self.aes_key = aes_key
        self.aes_key_expires = time.time() + confirm["ttl"]

    def _ensure_key(self):
        if not self.aes_key or time.time() >= self.aes_key_expires:
            self._handshake()

    def _prepare_encrypted_headers(self, extra_headers: dict = None):
        if not extra_headers:
            return {}

        plain_hdrs = json.dumps(extra_headers).encode()
        enc = self._aes_encrypt(self.aes_key, plain_hdrs)
        return {
            "X-Enc-Headers": base64.b64encode(json.dumps(enc).encode()).decode()
        }

    def post(self, path, json_data, headers=None):
        """Encrypts and sends POST request, decrypts response."""
        self._ensure_key()
        enc_payload = self._aes_encrypt(self.aes_key, json.dumps(json_data).encode())

        req_headers = {
            "X-Key-Id": self.key_id,
            "Content-Type": "application/json"
        }

        # Encrypt any custom headers
        if headers:
            encrypted_headers = self._prepare_encrypted_headers(headers)
            req_headers.update(encrypted_headers)

        resp = self.session.post(
            f"{self.base_url}{path}",
            json=enc_payload,
            headers=req_headers
        )

        return self._process_response(resp)

    def get(self, path, headers=None):
        """Sends GET request with encrypted headers (optional)."""
        self._ensure_key()

        req_headers = {
            "X-Key-Id": self.key_id,
        }

        if headers:
            encrypted_headers = self._prepare_encrypted_headers(headers)
            req_headers.update(encrypted_headers)

        resp = self.session.get(
            f"{self.base_url}{path}",
            headers=req_headers
        )

        return self._process_response(resp)

    def _process_response(self, resp):
        """Decrypts AES-encrypted JSON response if applicable."""
        content_type = resp.headers.get("Content-Type", "").lower()
        if "application/json" in content_type:
            try:
                payload = resp.json()
                if "iv" in payload and "ct" in payload:
                    plaintext = self._aes_decrypt(self.aes_key, payload["iv"], payload["ct"])
                    return json.loads(plaintext.decode())
                else:
                    return payload
            except Exception as e:
                raise Exception(f"Decryption failed: {e}")
        else:
            return resp.content
