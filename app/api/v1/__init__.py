# -*- coding: utf-8 -*-

"""
API v1 版本

使用方式:
    在 app/api/__init__.py 中注册:
        from app.api.v1 import v1_bp
        DEFAULT_BLUEPRINT = [
            (v1_bp, '/api/v1', False),
            ...
        ]

    在此文件中注册 v1 的子蓝图:
        v1_bp.register_blueprint(user_v1_bp, url_prefix='/user')
"""

from flask import Blueprint

v1_bp = Blueprint('v1', __name__)

# 注册 v1 版本的路由
# from app.api.v1.user import user_v1_bp
# v1_bp.register_blueprint(user_v1_bp, url_prefix='/user')
