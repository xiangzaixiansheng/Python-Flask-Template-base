# -*- coding: utf-8 -*-

import jwt
import datetime
from flask import current_app


def create_jwt_token(user_id):
    """生成 Access Token"""
    expires = current_app.config.get('JWT_ACCESS_TOKEN_EXPIRES', datetime.timedelta(hours=1))
    expiration = datetime.datetime.now(datetime.timezone.utc) + expires
    payload = {
        'user_id': user_id,
        'type': 'access',
        'exp': expiration,
        'iat': datetime.datetime.now(datetime.timezone.utc)
    }
    return jwt.encode(payload, current_app.config['JWT_*_KEY'], algorithm='HS256')


def create_refresh_token(user_id):
    """生成 Refresh Token"""
    expires = current_app.config.get('JWT_REFRESH_TOKEN_EXPIRES', datetime.timedelta(days=15))
    expiration = datetime.datetime.now(datetime.timezone.utc) + expires
    payload = {
        'user_id': user_id,
        'type': 'refresh',
        'exp': expiration,
        'iat': datetime.datetime.now(datetime.timezone.utc)
    }
    return jwt.encode(payload, current_app.config['JWT_*_KEY'], algorithm='HS256')


def decode_token(token):
    """解码并验证 Token"""
    return jwt.decode(token, current_app.config['JWT_*_KEY'], algorithms=['HS256'])
