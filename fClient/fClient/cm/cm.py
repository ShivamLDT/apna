import base64
import os
import win32cred
from cryptography.fernet import Fernet
from fClient import app
from fClient.fingerprint import getKey

def ensure_str(data, encoding='utf-8'):
    if isinstance(data, bytes):
        return data.decode(encoding)  
    elif isinstance(data, str):
        return data  
    else:
        raise TypeError(f"Input must be str or bytes, got {type(data)}")

class  CredentialManager:
    def __init__(self, key_file="ms.wind.10.90",keyx=None):
        key_file= os.path.join( app.config["AppFolders"].site_config_dir,key_file)
        self.keyx=keyx
        self.key_file = key_file
        if not os.path.exists(self.key_file):
            self.generate_key()
        self.key = self.load_key()

    def generate_key(self):
        key = Fernet.generate_key()
        #if self.keyx:
        key=getKey(keya=None,keyx=self.keyx)
        key = base64.urlsafe_b64encode(key)
        with open(self.key_file, 'wb') as key_file:
            key_file.write(key)
        # print(f"Encryption key generated and saved to {self.key_file}")

    def load_key(self):
        with open(self.key_file, 'rb') as key_file:
            key = key_file.read()
        return key

    def encrypt_data(self, data):
        fernet = Fernet(self.key)
        encrypted_data = fernet.encrypt(data.encode())
        return encrypted_data

    def decrypt_data(self, encrypted_data):
        fernet = Fernet(self.key)
        decrypted_data = fernet.decrypt(encrypted_data).decode()
        return decrypted_data

    def store_credentials(self, target, username, password):
        encrypted_username = self.encrypt_data(username)
        encrypted_password = self.encrypt_data(password)
        encrypted_username = username
        encrypted_password = password
        
        credential = {
            'Type': win32cred.CRED_TYPE_GENERIC,
            'TargetName': target,
            'UserName': ensure_str(encrypted_username),
            'CredentialBlob': ensure_str(encrypted_password),
            #'Persist': win32cred.CRED_PERSIST_LOCAL_MACHINE
            'Persist': win32cred.CRED_PERSIST_ENTERPRISE 
        }
        win32cred.CredWrite(credential, 0)
        print(f"Credentials for {target} stored successfully.")

    def retrieve_credentials(self, target):
        try:
            credential = win32cred.CredRead(target, win32cred.CRED_TYPE_GENERIC, 0)
            # encrypted_username = credential['UserName'].encode()
            # encrypted_password = credential['CredentialBlob']
            
            # username = self.decrypt_data(encrypted_username)
            #password = self.decrypt_data(encrypted_password)

            encrypted_username = credential['UserName']
            encrypted_password = credential['CredentialBlob']
            

            username = encrypted_username
            null_byte_pos = encrypted_password.find(b'\x00') 
            if null_byte_pos != -1:
                extracted_password = encrypted_password[:null_byte_pos].decode('utf-8') 
            else:
                extracted_password = encrypted_password.decode('utf-8') 

            print(extracted_password)  # Output: "some_encrypted_password"

            password = encrypted_password.replace(b'\x00', b'').decode('utf-8')
            
            return username, password
        except Exception as e:
            print(f"Failed to retrieve credentials: {e}")
            return None, None

    def delete_credentials(self, target):
        try:
            win32cred.CredDelete(target, win32cred.CRED_TYPE_GENERIC, 0)
            print(f"Credentials for {target} deleted successfully.")
        except Exception as e:
            print(f"Failed to delete credentials: {e}")


# Example usage
if __name__ == "__main__":
    key_file_path = 'encryption.key'
    
    # Initialize the CredentialManager
    manager = CredentialManager(key_file_path)
    
    # Store credentials
    manager.store_credentials('my_PC', 'my_username', 'my_password')
    
    # Retrieve credentials
    username, password = manager.retrieve_credentials('my_PC')
    if username and password:
        print(f"Retrieved credentials - Username: {username}, Password: {password}")
    
    # Delete credentials
    manager.delete_credentials('my_PC')

