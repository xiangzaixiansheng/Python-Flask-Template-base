# -*- coding: utf-8 -*-

import datetime
from flask import Blueprint, request, make_response, g
from app.api.service.user_service import UserService
from app.middleware.authMiddleware import token_required
from app.common.result.result import Result
from app.common.util.log_handler import log
from app.common.rate_limiter import limiter

user_bp = Blueprint('user', __name__)


@user_bp.route('/users', methods=['POST'])
def create_user():
    """创建用户"""
    data = request.get_json()
    if not data:
        return Result.failed(400, '请求体不能为空')

    username = data.get('username')
    password = data.get('password')
    email = data.get('email')

    if not all([username, password, email]):
        return Result.failed(400, '缺少必要参数: username, password, email')

    try:
        user = UserService.create_user(username=username, password=password, email=email)
        return Result.success(user.to_dict())
    except ValueError as e:
        return Result.failed(400, str(e))
    except Exception as e:
        log.error(f"创建用户失败: {e}")
        return Result.failed(500, '创建用户失败')


@user_bp.route('/users/<int:user_id>', methods=['GET'])
@token_required
def get_user(user_id):
    """获取单个用户"""
    user = UserService.get_user(user_id)
    if user:
        return Result.success(user)
    return Result.failed(404, '用户不存在')


@user_bp.route('/users', methods=['GET'])
@token_required
def get_all_users():
    """获取所有用户"""
    users = UserService.get_all_users()
    return Result.success(users)


@user_bp.route('/users/<int:user_id>', methods=['PUT'])
@token_required
def update_user(user_id):
    """更新用户"""
    data = request.get_json()
    if not data:
        return Result.failed(400, '请求体不能为空')
    user = UserService.update_user(user_id, data)
    if user:
        return Result.success(user)
    return Result.failed(404, '用户不存在')


@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
@token_required
def delete_user(user_id):
    """删除用户"""
    if UserService.delete_user(user_id):
        return Result.success()
    return Result.failed(404, '用户不存在')


@user_bp.route('/login', methods=['POST'])
@limiter.limit("5/minute")
def login():
    """用户登录"""
    data = request.get_json()
    if not data:
        return Result.failed(400, '请求体不能为空')

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return Result.failed(400, '缺少必要参数: username, password')

    try:
        user = UserService.authenticate_user(username=username, password=password)
        if not user:
            return Result.failed(401, '用户名或密码错误')

        log.info(f'用户登录成功: {username}')
        response_data = {
            "token": user.get("token"),
            "refresh_token": user.get("refresh_token"),
            "user": {k: v for k, v in user.items() if k not in ('token', 'refresh_token')}
        }
        resp = make_response(Result.success(response_data))
        resp.set_cookie(
            '_ut', user.get('token'),
            httponly=True, secure=True, samesite='Lax',
            max_age=int(datetime.timedelta(hours=1).total_seconds())
        )
        resp.set_cookie(
            '_rt', user.get('refresh_token'),
            httponly=True, secure=True, samesite='Lax',
            max_age=int(datetime.timedelta(days=15).total_seconds())
        )
        return resp
    except ValueError as e:
        return Result.failed(400, str(e))


@user_bp.route('/refresh', methods=['POST'])
def refresh_token():
    """刷新 Access Token"""
    token = request.cookies.get('_rt')
    if not token:
        return Result.failed(401, '缺少 Refresh Token')

    result = UserService.refresh_access_token(token)
    if not result:
        return Result.failed(401, 'Refresh Token 无效或已过期')

    resp = make_response(Result.success({"token": result['token']}))
    resp.set_cookie(
        '_ut', result['token'],
        httponly=True, secure=True, samesite='Lax',
        max_age=int(datetime.timedelta(hours=1).total_seconds())
    )
    return resp


@user_bp.route('/logout', methods=['POST'])
def logout():
    """用户登出"""
    resp = make_response(Result.success(message="登出成功"))
    resp.delete_cookie('_ut')
    resp.delete_cookie('_rt')
    return resp
