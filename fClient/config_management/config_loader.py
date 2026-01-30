import json
from cryptography.fernet import Fernet

def load_config(encrypted_file_path: str, key: bytes) -> dict:
    """
    Decrypts an encrypted configuration file using the provided key.
    """
    fernet = Fernet(key)
    with open(encrypted_file_path, 'rb') as encrypted_file:
        encrypted_data = encrypted_file.read()
    decrypted_data = fernet.decrypt(encrypted_data)
    return json.loads(decrypted_data)
