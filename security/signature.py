import hmac
import hashlib
from utils.logger import bank_logger
from utils.exceptions import SecurityError


class SignatureService:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key

    def generate_signature(self, data: str) -> str:
        """
        生成数据签名
        :param data: 要签名的数据
        :return: 签名
        """
        try:
            return hmac.new(
                self.secret_key.encode(),
                data.encode(),
                hashlib.sha256
            ).hexdigest()
        except Exception as e:
            bank_logger.error(f"Signature generation failed: {str(e)}")
            raise SecurityError("Failed to generate signature")

    def verify_signature(self, data: str, signature: str) -> bool:
        """
        验证数据签名
        :param data: 原始数据
        :param signature: 要验证的签名
        :return: 签名是否有效
        """
        try:
            calculated_signature = self.generate_signature(data)
            return hmac.compare_digest(calculated_signature, signature)
        except Exception as e:
            bank_logger.error(f"Signature verification failed: {str(e)}")
            return False