import requests
from flask import g, request, current_app
from .crypto_utils import aes_encrypt, aes_decrypt, rsa_encrypt, aes_generate_key
import json
import time

class CryptoInterceptor:
    def __init__(self, server_base_url):
        self.server_base_url = server_base_url.rstrip("/")
        self.original_request = requests.Session.request
        self._patch_requests()

    def _patch_requests(self):
        def intercepted_request(session, method, url, **kwargs):
            # Only intercept specific domain
            if url.startswith(self.server_base_url):
                self._ensure_keys()

                # Encrypt request body if it's JSON
                if "json" in kwargs:
                    data = json.dumps(kwargs.pop("json")).encode()
                    iv, ct = aes_encrypt(g.aes_key, data)
                    kwargs["json"] = {"iv": iv, "ct": ct}
                    kwargs.setdefault("headers", {})["X-Key-Id"] = g.key_id

                # Proceed with original request
                response = self.original_request(session, method, url, **kwargs)

                # Decrypt response body if needed
                try:
                    body = response.json()
                    if "iv" in body and "ct" in body:
                        decrypted = aes_decrypt(g.aes_key, body["iv"], body["ct"])
                        response._content = decrypted.encode()
                        response.headers["Content-Type"] = "application/json"
                except Exception:
                    pass  # not encrypted or failed

                return response
            else:
                return self.original_request(session, method, url, **kwargs)

        requests.Session.request = intercepted_request

    def _ensure_keys(self):
        if not hasattr(g, "aes_key") or time.time() > getattr(g, "aes_expiry", 0):
            self._handshake()

    def _handshake(self):
        resp = requests.get(f"{self.server_base_url}/handshake")
        pub = resp.json()
        g.key_id = pub["key_id"]
        g.aes_key = aes_key = aes_generate_key()
        g.aes_expiry = time.time() + 3600  # 1hr default

        enc_key = rsa_encrypt(pub["pub_pem"], aes_key)
        requests.post(f"{self.server_base_url}/handshake/confirm", json={
            "key_id": g.key_id,
            "enc_aes_b64": enc_key
        })


class FlaskClientCryptoMiddleware:
    def __init__(self, app=None, server_base_url=None):
        self.server_base_url = server_base_url
        if app:
            self.init_app(app)

    def init_app(self, app):
        app.before_request(self.before_request)
        app.extensions = getattr(app, 'extensions', {})
        app.extensions['crypto_interceptor'] = CryptoInterceptor(self.server_base_url)
        app.logger.info("Crypto middleware initialized")

    def before_request(self):
        # Clear any per-request crypto data
        g.aes_key = None
        g.key_id = None
        g.aes_expiry = 0
