# -*- coding: utf-8 -*-

import jwt
from flask import request, g
from functools import wraps

from app.common.result.result import Result
from app.common.util.jwt_util import decode_token


def token_required(f):
    """JWT 验证中间件"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.cookies.get('_ut')
        if not token:
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return Result.failed(401, "未提供认证 Token")

        try:
            data = decode_token(token)
            if data.get('type') != 'access':
                return Result.failed(401, "Token 类型无效")
            g.current_user = data['user_id']
        except jwt.ExpiredSignatureError:
            return Result.failed(401, "Token 已过期")
        except jwt.InvalidTokenError:
            return Result.failed(401, "Token 无效")

        return f(*args, **kwargs)

    return decorated_function
