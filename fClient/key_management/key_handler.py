import hashlib
import base64

def get_key(variable_length_key: str) -> bytes:
    """
    Converts a variable-length key to a fixed-length key suitable for Fernet.
    """
    sha256 = hashlib.sha256()
    sha256.update(variable_length_key.encode('utf-8'))
    hashed_key = sha256.digest()
    return base64.urlsafe_b64encode(hashed_key)
