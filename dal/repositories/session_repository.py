from sqlalchemy.orm import Session
from datetime import datetime
from .base_repository import BaseRepository
from ..models.session import Session as UserSession
from utils.logger import bank_logger

class SessionRepository(BaseRepository[UserSession]):
    def __init__(self, db: Session):
        super().__init__(UserSession, db)

    def create_session(self, user_id: int, token: str, expires_at: datetime,
                      ip_address: str = None, user_agent: str = None) -> UserSession:
        """创建新会话"""
        try:
            session = UserSession(
                user_id=user_id,
                token=token,
                expires_at=expires_at,
                ip_address=ip_address,
                user_agent=user_agent
            )
            self.db.add(session)
            self.db.commit()
            return session
        except Exception as e:
            bank_logger.error(f"Error creating session: {str(e)}")
            self.db.rollback()
            raise

    def get_active_session(self, token: str) -> UserSession:
        """获取有效的会话"""
        try:
            return self.db.query(UserSession).filter(
                UserSession.token == token,
                UserSession.is_active == True,
                UserSession.expires_at > datetime.utcnow()
            ).first()
        except Exception as e:
            bank_logger.error(f"Error getting active session: {str(e)}")
            raise

    def invalidate_session(self, session_id: int) -> bool:
        """使会话失效"""
        try:
            session = self.get_by_id(session_id)
            if session:
                session.is_active = False
                self.db.commit()
                return True
            return False
        except Exception as e:
            bank_logger.error(f"Error invalidating session: {str(e)}")
            self.db.rollback()
            raise

    def clean_expired_sessions(self) -> int:
        """清理过期会话"""
        try:
            result = self.db.query(UserSession).filter(
                UserSession.expires_at < datetime.utcnow()
            ).delete()
            self.db.commit()
            return result
        except Exception as e:
            bank_logger.error(f"Error cleaning expired sessions: {str(e)}")
            self.db.rollback()
            raise