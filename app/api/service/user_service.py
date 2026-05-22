# -*- coding: utf-8 -*-

import jwt
from flask import g
from werkzeug.security import generate_password_hash, check_password_hash

from app.api.dao.user_dao import UserDao
from app.common.util.jwt_util import create_jwt_token, create_refresh_token, decode_token
from app.common.util.log_handler import log


class UserService:

    @staticmethod
    def create_user(username, password, email):
        if not isinstance(password, str) or len(password) < 6:
            raise ValueError("密码必须为字符串且长度不少于6位")
        hashed_password = generate_password_hash(password)
        return UserDao.create_user(username, hashed_password, email)

    @staticmethod
    def get_user(user_id):
        user = UserDao.get_user_by_id(user_id)
        return user.to_dict() if user else None

    @staticmethod
    def get_all_users():
        current_user = g.get('current_user', None)
        log.info(f"current_user: {current_user}")
        users = UserDao.get_all_users()
        return [user.to_dict() for user in users]

    @staticmethod
    def update_user(user_id, data):
        if 'password' in data:
            data = {**data, 'password': generate_password_hash(data['password'])}
        else:
            data = {**data}
        user = UserDao.update_user(user_id, data)
        return user.to_dict() if user else None

    @staticmethod
    def delete_user(user_id):
        return UserDao.delete_user(user_id)

    @staticmethod
    def authenticate_user(username, password):
        if not isinstance(password, str) or not isinstance(username, str):
            raise ValueError("用户名和密码必须为字符串")

        user = UserDao.get_user_by_username(username)
        if user and check_password_hash(user.password, password):
            user_data = user.to_dict()
            user_data['token'] = create_jwt_token(user.id)
            user_data['refresh_token'] = create_refresh_token(user.id)
            return user_data
        return None

    @staticmethod
    def refresh_access_token(refresh_token):
        """使用 refresh token 生成新的 access token"""
        try:
            payload = decode_token(refresh_token)
            if payload.get('type') != 'refresh':
                return None
            user_id = payload.get('user_id')
            return {'token': create_jwt_token(user_id)}
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
