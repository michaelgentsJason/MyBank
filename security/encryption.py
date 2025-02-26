from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from base64 import b64encode, b64decode
from .key_manager import KeyManager
from utils.logger import bank_logger
from utils.exceptions import SecurityError

class EncryptionService:
    def __init__(self, key_manager: KeyManager):
        self.key_manager = key_manager
        self.fernet = None
        self._initialize_fernet()

    def _initialize_fernet(self):
        """初始化Fernet实例"""
        try:
            current_key = self.key_manager.get_current_key()
            self.fernet = Fernet(current_key)
        except Exception as e:
            bank_logger.error(f"Failed to initialize Fernet: {str(e)}")
            raise SecurityError("Encryption service initialization failed")

    def encrypt_data(self, data: str) -> str:
        """加密数据"""
        try:
            return self.fernet.encrypt(data.encode()).decode()
        except Exception as e:
            bank_logger.error(f"Encryption failed: {str(e)}")
            raise SecurityError("Failed to encrypt data")

    def decrypt_data(self, encrypted_data: str) -> str:
        """解密数据"""
        try:
            return self.fernet.decrypt(encrypted_data.encode()).decode()
        except Exception as e:
            bank_logger.error(f"Decryption failed: {str(e)}")
            raise SecurityError("Failed to decrypt data")

    def generate_signature(self, data: str) -> str:
        """生成数字签名"""
        try:
            private_key = self.key_manager.get_private_key()
            signature = private_key.sign(
                data.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return b64encode(signature).decode()
        except Exception as e:
            bank_logger.error(f"Signature generation failed: {str(e)}")
            raise SecurityError("Failed to generate signature")