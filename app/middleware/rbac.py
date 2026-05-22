# -*- coding: utf-8 -*-

from functools import wraps
from flask import g
from app.common.result.result import Result


def role_required(*roles):
    """角色权限校验装饰器

    Usage:
        @role_required('admin')
        def admin_only_route():
            ...

        @role_required('admin', 'editor')
        def admin_or_editor():
            ...

    Note:
        需要在 token_required 之后使用，依赖 g.current_user 和 g.current_role
        在 User model 中添加 role 字段，并在 authMiddleware 中将 role 写入 g
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            current_role = getattr(g, 'current_role', None)
            if current_role is None:
                return Result.failed(403, '无法获取用户角色信息')
            if current_role not in roles:
                return Result.failed(403, f'权限不足，需要角色: {", ".join(roles)}')
            return f(*args, **kwargs)
        return wrapper
    return decorator


def permission_required(*permissions):
    """细粒度权限校验装饰器

    Usage:
        @permission_required('user:create')
        def create_user():
            ...

        @permission_required('order:read', 'order:write')
        def manage_order():
            ...

    Note:
        需要配合权限表使用，g.current_permissions 应为权限列表
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            current_permissions = getattr(g, 'current_permissions', [])
            missing = [p for p in permissions if p not in current_permissions]
            if missing:
                return Result.failed(403, f'缺少权限: {", ".join(missing)}')
            return f(*args, **kwargs)
        return wrapper
    return decorator
