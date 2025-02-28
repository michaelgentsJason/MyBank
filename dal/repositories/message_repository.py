from sqlalchemy.orm import Session
from datetime import datetime
from .base_repository import BaseRepository
from ..models.message import SecureMessage

class MessageRepository(BaseRepository[SecureMessage]):
    def __init__(self, db: Session):
        super().__init__(SecureMessage, db)

    def get_messages_for_user(self, user_id: int, is_sender: bool = False):
        """获取用户的消息"""
        query = self.db.query(SecureMessage)
        if is_sender:
            return query.filter(SecureMessage.sender_id == user_id).all()
        else:
            return query.filter(SecureMessage.recipient_id == user_id).all()

    def mark_as_read(self, message_id: int):
        """将消息标记为已读"""
        message = self.get_by_id(message_id)
        if message:
            message.status = 'read'
            message.read_at = datetime.utcnow()
            self.db.commit()
            return True
        return False