import rsa, os, base64, hashlib
from backend_shared import configurator
from cryptography.fernet import Fernet
from backend_shared.logger import logger


class Encrpyter:
    def __init__(self, config):
        self.config = config
        self.private_key_path = self.config["security"]["keys"]["private_key_path"] 
        self.public_key_path = self.config["security"]["keys"]["public_key_path"]
        self.private_key = self.load_private_key()
        self.public_key = self.load_public_key()
        self.fernet = Fernet
        self.logger = logger.Logger()

    def load_binary_private_key(self):
        with open(f"{os.getcwd()}/{self.private_key_path}", "rb") as private_file:
            return private_file.read()

    def load_private_key(self):
        if os.path.isfile(f"{os.getcwd()}/{self.private_key_path}"):
            with open(f"{os.getcwd()}/{self.private_key_path}", "r") as private_file:
                key_data = private_file.read()
            return rsa.PrivateKey.load_pkcs1(key_data,'PEM')
        print(f"No private key found @{os.getcwd()}/{self.private_key_path}\n Provide a key or disable rsa in your config file")
        import time
        time.sleep(300)
        exit()

    def load_binary_public_key(self):
        with open(f"{os.getcwd()}/{self.public_key_path}", "rb") as public_file:
            return public_file.read()
        
    def load_public_key(self):
        if os.path.isfile(f"{os.getcwd()}/{self.public_key_path}"):
            with open(f"{os.getcwd()}/{self.public_key_path}", "r") as public_file:
                key_data = public_file.read()
            return rsa.PublicKey.load_pkcs1(key_data,'PEM')
        print(f"No private key found @{os.getcwd()}/{self.public_key_path}\n Provide a key or disable rsa in your config file")
        exit()

    def enc_private_key(self, value: str):
        enc_value = rsa.encrypt(value.encode(), self.private_key)
        return enc_value

    def dec_private_key(self, value: bytes):
        dec_value = rsa.decrypt(bytes.fromhex(value.decode()), self.private_key).decode()
        return dec_value

    def enc_public_key(self, value: str):
        enc_value = rsa.encrypt(value.encode(), self.private_key)
        return enc_value

    def dec_public_key(self, value: bytes):
        dec_value = rsa.decrypt(bytes.fromhex(value.decode()), self.private_key).decode()
        return dec_value

    def has_private_key(self):
        if not self.load_private_key():
            return False
        return True
    
    def has_public_key(self):
        if not self.load_public_key():
            return False
        return True
    
    def fernet_encryption(self, data):
        fKey = hashlib.md5(str(self.private_key).encode()).hexdigest()
        fKey = base64.urlsafe_b64encode(fKey.encode())
        fernit = self.fernet(fKey)
        return fernit.encrypt(data.encode("utf-8")).decode()
    
    def fernet_decryption(self, data):
        fKey = hashlib.md5(str(self.private_key).encode()).hexdigest()
        fKey = base64.urlsafe_b64encode(fKey.encode())
        fernit = self.fernet(fKey)
        return fernit.decrypt(data.encode()).decode()

    
    def calc_data_hash(self, data):
        hSha = hashlib.sha1()
        hSha.update(data)
        return hSha.hexdigest()

class Keygen:
    def __init__(self, key_length=2048, config=None):
        self.key_length = key_length
        self.config = config
        self.logger = logger.Logger()

    def public_key_exists(self):
        return os.path.isfile(f"{os.getcwd()}/{self.config['security']['keys']['public_key_path']}")

    def private_key_exists(self):
        return os.path.isfile(f"{os.getcwd()}/{self.config['security']['keys']['private_key_path']}")
    
    def create_key_pair(self):
        publicKey, privateKey = rsa.newkeys(self.key_length)
        if self.config:
            if not self.public_key_exists():
                with open(f"{os.getcwd()}/{self.config['security']['keys']['public_key_path']}", 'wb') as pubKeyFile:
                    pubKeyFile.write(publicKey.save_pkcs1())
                    self.logger.log("INFO", f"Creating public-key: {os.getcwd()}/{self.config['security']['keys']['public_key_path']}")
            if not self.private_key_exists():
                with open(f"{os.getcwd()}/{self.config['security']['keys']['private_key_path']}", 'wb') as privKeyFile:
                    privKeyFile.write(privateKey.save_pkcs1())
                    self.logger.log("INFO", f"Creating private-key: {os.getcwd()}/{self.config['security']['keys']['private_key_path']}")

        else:
            with open(f"{os.getcwd()}/private_key.pem", 'wb') as privKeyFile:
                privKeyFile.write(privateKey.save_pkcs1())
                print(f"Creating private-key: {os.getcwd()}/private_key.pem")
            with open(f"{os.getcwd()}/public_key.pem", 'wb') as pubKeyFile:
                pubKeyFile.write(publicKey.save_pkcs1())
                print(f"Creating public-key: {os.getcwd()}/public_key.pem")
