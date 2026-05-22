# -*- coding: utf-8 -*-

import jwt


def test_create_jwt_token(app):
    """测试 JWT token 生成"""
    with app.app_context():
        from app.common.util.jwt_util import create_jwt_token
        token = create_jwt_token(1)
        assert token is not None
        assert isinstance(token, str)


def test_create_refresh_token(app):
    """测试 Refresh token 生成"""
    with app.app_context():
        from app.common.util.jwt_util import create_refresh_token
        token = create_refresh_token(1)
        assert token is not None


def test_decode_token(app):
    """测试 token 解码"""
    with app.app_context():
        from app.common.util.jwt_util import create_jwt_token, decode_token
        token = create_jwt_token(42)
        payload = decode_token(token)
        assert payload['user_id'] == 42
        assert payload['type'] == 'access'


def test_refresh_token_type(app):
    """测试 refresh token 类型标识"""
    with app.app_context():
        from app.common.util.jwt_util import create_refresh_token, decode_token
        token = create_refresh_token(42)
        payload = decode_token(token)
        assert payload['type'] == 'refresh'
        assert payload['user_id'] == 42


def test_invalid_token(app):
    """测试无效 token 解码"""
    with app.app_context():
        from app.common.util.jwt_util import decode_token
        try:
            decode_token("invalid.token.here")
            assert False, "Should have raised"
        except jwt.InvalidTokenError:
            pass
