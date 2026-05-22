# -*- coding: utf-8 -*-

import functools
from datetime import datetime, timezone
from flask import request, g
from app.extension import db
from app.common.util.log_handler import log


class AuditLog(db.Model):
    """操作审计日志表"""

    __tablename__ = 'audit_logs'

    id = db.Column(db.BigInteger, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, nullable=True, index=True)
    action = db.Column(db.String(50), nullable=False, index=True)
    resource_type = db.Column(db.String(50), nullable=True)
    resource_id = db.Column(db.String(50), nullable=True)
    detail = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    request_id = db.Column(db.String(36), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'action': self.action,
            'resource_type': self.resource_type,
            'resource_id': str(self.resource_id) if self.resource_id else None,
            'detail': self.detail,
            'ip_address': self.ip_address,
            'request_id': self.request_id,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }


def record_audit(action, resource_type=None, resource_id=None, detail=None):
    """记录审计日志

    Args:
        action: 操作类型 (如 'create_user', 'delete_order', 'login')
        resource_type: 资源类型 (如 'user', 'order')
        resource_id: 资源 ID
        detail: 详情描述
    """
    try:
        audit = AuditLog(
            user_id=getattr(g, 'current_user', None),
            action=action,
            resource_type=resource_type,
            resource_id=str(resource_id) if resource_id else None,
            detail=detail,
            ip_address=request.remote_addr if request else None,
            request_id=getattr(g, 'request_id', None),
        )
        db.session.add(audit)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        log.error(f"审计日志记录失败: {e}")


def audit(action, resource_type=None):
    """审计日志装饰器

    Usage:
        @audit('create_user', 'user')
        def create_user():
            ...
    """
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            result = f(*args, **kwargs)
            resource_id = kwargs.get('user_id') or kwargs.get('id')
            record_audit(action, resource_type, resource_id)
            return result
        return wrapper
    return decorator
