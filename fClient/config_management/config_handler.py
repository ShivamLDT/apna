import json
from cryptography.fernet import Fernet

def load_config(encrypted_file_path: str, key: bytes) -> dict:
    """
    Decrypts an encrypted configuration file using the provided key.
    """
    decrypted_data:bytes
    try:
        with open(encrypted_file_path, 'rb') as encrypted_file:
            encrypted_data = encrypted_file.read()
        fernet = Fernet(key)
        decrypted_data = fernet.decrypt(encrypted_data)
    except FileNotFoundError as fnf:
        create_config(encrypted_file_path,key=key)
    except Exception  as efnf:
        return False
    else:
        return json.loads(decrypted_data)

def save_config(config: dict, file_path: str, key: bytes):
    import threading
    """
    Encrypts and saves the configuration dictionary to a file using the provided key.
    """
    fernet = Fernet(key)
    encrypted_data = fernet.encrypt(json.dumps(config).encode('utf-8'))
    file_lock = threading.Lock()
    with file_lock:                                
        with open(file_path, 'wb') as encrypted_file:
            encrypted_file.write(encrypted_data)
            encrypted_file.close()

def create_config(file_path: str, key: bytes):
    """
    Creates an empty encrypted configuration file.
    """
    empty_config = {}
    save_config(empty_config, file_path, key)

def add_or_update_config(file_path: str, key: bytes, config_key: str, config_value):
    """
    Adds or updates a configuration point in the encrypted configuration file.
    """
    config = load_config(file_path, key)
    config[config_key] = config_value
    save_config(config, file_path, key)

def delete_config(file_path: str, key: bytes, config_key: str):
    """
    Deletes a configuration point from the encrypted configuration file.
    """
    config = load_config(file_path, key)
    if config_key in config:
        del config[config_key]
    save_config(config, file_path, key)

#=========================================================
#=========INI CONFIG FILE ===============
#=========================================================


def load_config_ini(file_path: str, key: bytes) -> dict:
    """
    Decrypts an encrypted configuration file using the provided key.
    """
    decrypted_data:bytes
    try:
        with open(file_path, 'rb') as encrypted_file:
            encrypted_data = encrypted_file.read()
        fernet = Fernet(key)
        decrypted_data = fernet.decrypt(encrypted_data)
    except FileNotFoundError as fnf:
        create_config_ini(file_path,key=key)
    except Exception  as efnf:
        return False
    else:
        return json.loads(decrypted_data)

def save_config_ini(config: dict, file_path: str, key: bytes):
    import threading
    """
    Encrypts and saves the configuration dictionary to a file using the provided key.
    """
    fernet = Fernet(key)
    encrypted_data = fernet.encrypt(json.dumps(config).encode('utf-8'))
    file_lock = threading.Lock()
    with file_lock:                                
        with open(file_path, 'wb') as encrypted_file:
            encrypted_file.write(encrypted_data)
            encrypted_file.close()

def create_config_ini(file_path: str, key: bytes):
    """
    Creates an empty encrypted configuration file.
    """
    empty_config = {}
    save_config_ini(empty_config, file_path, key)

def add_or_update_config_ini(file_path: str, key: bytes, config_key: str, config_value):
    """
    Adds or updates a configuration point in the encrypted configuration file.
    """
    config = load_config_ini(file_path, key)
    config[config_key] = config_value
    save_config_ini(config, file_path, key)

def delete_config_ini(file_path: str, key: bytes, config_key: str):
    """
    Deletes a configuration point from the encrypted configuration file.
    """
    config = load_config_ini(file_path, key)
    if config_key in config:
        del config[config_key]
    save_config_ini(config, file_path, key)
