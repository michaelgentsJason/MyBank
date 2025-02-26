from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from datetime import datetime, timedelta
from utils.logger import bank_logger
from utils.exceptions import SecurityError
from dal.repositories.encryption_keys import EncryptionKeyRepository


class KeyManager:
    def __init__(self, key_repository: EncryptionKeyRepository):
        self.key_repository = key_repository
        self.current_key = None
        self.private_key = None
        self.public_key = None
        self._initialize_keys()

    def get_current_key(self) -> str:
        """获取当前活跃的密钥"""
        if not self.current_key:
            current_key = self.key_repository.get_current_key()
            if current_key:
                self.current_key = current_key.key_value
            else:
                self.generate_new_key()
        return self.current_key

    def _initialize_keys(self):
        """初始化密钥"""
        try:
            # 获取或生成对称密钥
            current_key = self.key_repository.get_current_key()
            if current_key:
                self.current_key = current_key.key_value  # 使用key_value
            else:
                self.generate_new_key()

            # 获取或生成非对称密钥对
            if not self.private_key:
                self.generate_key_pair()
        except Exception as e:
            bank_logger.error(f"Key initialization failed: {str(e)}")
            raise SecurityError("Failed to initialize keys")

    def generate_new_key(self) -> str:
        """生成新的对称密钥"""
        try:
            new_key = Fernet.generate_key()
            expiry_date = datetime.utcnow() + timedelta(days=90)

            self.key_repository.create({
                'key_type': 'symmetric',
                'key_value': new_key,
                'status': 'active',
                'expiry_date': expiry_date
            })

            self.current_key = new_key
            return new_key
        except Exception as e:
            bank_logger.error(f"Key generation failed: {str(e)}")
            raise SecurityError("Failed to generate new key")

    def generate_key_pair(self):
        """生成RSA密钥对"""
        try:
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
            )
            public_key = private_key.public_key()

            self.private_key = private_key
            self.public_key = public_key

            # 存储密钥
            self.key_repository.create({
                'key_type': 'asymmetric',
                'key_value': private_key.private_bytes(
                    encoding=serialization.Encoding.PEM,
                    format=serialization.PrivateFormat.PKCS8,
                    encryption_algorithm=serialization.NoEncryption()
                ),
                'status': 'active',
                'expiry_date': datetime.utcnow() + timedelta(days=365)
            })
        except Exception as e:
            bank_logger.error(f"Key pair generation failed: {str(e)}")
            raise SecurityError("Failed to generate key pair")