# -*- coding: utf-8 -*-

from datetime import datetime, timezone
from app.extension import db
from app.common.util.snowflake import generate_id


class BaseModel(db.Model):
    """基础模型 - 包含公共字段和软删除

    所有业务模型都应继承此类:
        class Article(BaseModel):
            __tablename__ = 'articles'
            title = db.Column(db.String(200), nullable=False)
    """

    __abstract__ = True

    id = db.Column(db.BigInteger, primary_key=True, default=generate_id)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, nullable=False,
                           default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))
    is_deleted = db.Column(db.Boolean, default=False, nullable=False, index=True)
    deleted_at = db.Column(db.DateTime, nullable=True)

    def soft_delete(self):
        """软删除"""
        self.is_deleted = True
        self.deleted_at = datetime.now(timezone.utc)

    def restore(self):
        """恢复软删除"""
        self.is_deleted = False
        self.deleted_at = None

    @classmethod
    def query_active(cls):
        """查询未删除的记录"""
        return cls.query.filter_by(is_deleted=False)

    def to_dict(self):
        """转为字典 (子类应重写此方法)"""
        result = {}
        for column in self.__table__.columns:
            value = getattr(self, column.name)
            if isinstance(value, datetime):
                value = value.isoformat()
            result[column.name] = value
        result.pop('is_deleted', None)
        result.pop('deleted_at', None)
        return result


class TimestampMixin:
    """时间戳 Mixin (如果不需要软删除，可以单独使用)"""

    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, nullable=False,
                           default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))
