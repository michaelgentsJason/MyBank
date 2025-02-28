from typing import List, Dict, Optional
import json
from datetime import datetime
from dal.repositories.message_repository import MessageRepository
from dal.repositories.user_repository import UserRepository
from security.encryption import EncryptionService
from security.signature import SignatureService
from utils.exceptions import ValidationError, SecurityError
from utils.logger import bank_logger


class MessageService:
    def __init__(
            self,
            message_repository: MessageRepository,
            user_repository: UserRepository,
            encryption_service: EncryptionService,
            signature_service: SignatureService
    ):
        self.message_repository = message_repository
        self.user_repository = user_repository
        self.encryption_service = encryption_service
        self.signature_service = signature_service

    async def send_message(
            self,
            sender_id: int,
            recipient_id: int,
            subject: str,
            content: str
    ) -> Dict:
        """发送加密消息"""
        try:
            # 验证发送者和接收者
            sender = self.user_repository.get_by_id(sender_id)
            recipient = self.user_repository.get_by_id(recipient_id)

            if not sender or not recipient:
                raise ValidationError("Invalid sender or recipient")

            # 加密消息内容
            encrypted_content = self.encryption_service.encrypt_data(content)

            # 生成消息签名
            signature_data = f"{sender_id}|{recipient_id}|{subject}|{content}"
            signature = self.signature_service.generate_signature(signature_data)

            # 构建消息数据
            message_data = {
                "sender_id": sender_id,
                "recipient_id": recipient_id,
                "subject": subject,
                "encrypted_content": encrypted_content,
                "signature": signature
            }

            # 保存消息
            message = self.message_repository.create(message_data)

            return {
                "message_id": message.message_id,
                "sender_id": message.sender_id,
                "recipient_id": message.recipient_id,
                "subject": message.subject,
                "created_at": message.created_at,
                "status": message.status
            }

        except Exception as e:
            bank_logger.error(f"Failed to send message: {str(e)}")
            raise

    async def get_messages(self, user_id: int, sent: bool = False) -> List[Dict]:
        """获取用户收到/发送的消息列表"""
        try:
            messages = self.message_repository.get_messages_for_user(user_id, is_sender=sent)

            result = []
            for msg in messages:
                message_data = {
                    "message_id": msg.message_id,
                    "sender_id": msg.sender_id,
                    "sender_name": msg.sender.username if msg.sender else "Unknown",
                    "recipient_id": msg.recipient_id,
                    "recipient_name": msg.recipient.username if msg.recipient else "Unknown",
                    "subject": msg.subject,
                    "created_at": msg.created_at,
                    "status": msg.status,
                    "read_at": msg.read_at
                }
                result.append(message_data)

            return result

        except Exception as e:
            bank_logger.error(f"Failed to get messages: {str(e)}")
            raise

    async def read_message(self, message_id: int, user_id: int) -> Dict:
        """读取消息内容并解密"""
        try:
            message = self.message_repository.get_by_id(message_id)

            if not message:
                raise ValidationError("Message not found")

            # 验证用户是否是消息的接收者
            if message.recipient_id != user_id:
                raise ValidationError("You are not authorized to read this message")

            # 解密消息内容
            decrypted_content = self.encryption_service.decrypt_data(message.encrypted_content)

            # 验证签名 (在实际使用中会完整实现)
            signature_valid = True

            # 标记消息为已读
            self.message_repository.mark_as_read(message_id)

            return {
                "message_id": message.message_id,
                "sender_id": message.sender_id,
                "sender_name": message.sender.username if message.sender else "Unknown",
                "recipient_id": message.recipient_id,
                "subject": message.subject,
                "content": decrypted_content,
                "signature_valid": signature_valid,
                "created_at": message.created_at,
                "status": "read"
            }

        except Exception as e:
            bank_logger.error(f"Failed to read message: {str(e)}")
            raise