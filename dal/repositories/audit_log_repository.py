from sqlalchemy.orm import Session
from datetime import datetime
from .base_repository import BaseRepository
from ..models.audit_log import AuditLog
from utils.logger import bank_logger


class AuditLogRepository(BaseRepository[AuditLog]):
    def __init__(self, db: Session):
        super().__init__(AuditLog, db)

    def log_action(self, user_id: int, action: str, entity_type: str,
                   entity_id: int, details: str = None, ip_address: str = None) -> AuditLog:
        """记录审计日志"""
        try:
            log = AuditLog(
                user_id=user_id,
                action=action,
                entity_type=entity_type,
                entity_id=entity_id,
                details=details,
                ip_address=ip_address
            )
            self.db.add(log)
            self.db.commit()
            return log
        except Exception as e:
            bank_logger.error(f"Error creating audit log: {str(e)}")
            self.db.rollback()
            raise

    def get_user_logs(self, user_id: int, start_date: datetime = None,
                      end_date: datetime = None) -> list[AuditLog]:
        """获取用户的审计日志"""
        try:
            query = self.db.query(AuditLog).filter(AuditLog.user_id == user_id)

            if start_date:
                query = query.filter(AuditLog.created_at >= start_date)
            if end_date:
                query = query.filter(AuditLog.created_at <= end_date)

            return query.order_by(AuditLog.created_at.desc()).all()
        except Exception as e:
            bank_logger.error(f"Error getting user logs: {str(e)}")
            raise