from sqlalchemy import Column, Integer, String, Text, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from .base import BaseModel

class SecureMessage(BaseModel):
    __tablename__ = 'secure_messages'

    message_id = Column(Integer, primary_key=True, autoincrement=True)
    sender_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    recipient_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    encrypted_content = Column(Text, nullable=False)
    subject = Column(String(255))
    signature = Column(String(256))
    status = Column(Enum('sent', 'delivered', 'read'), default='sent')
    read_at = Column(DateTime, nullable=True)

    # relationships
    sender = relationship("User", foreign_keys=[sender_id])
    recipient = relationship("User", foreign_keys=[recipient_id])

    def __repr__(self):
        return f"<SecureMessage {self.message_id} from {self.sender_id} to {self.recipient_id}>"