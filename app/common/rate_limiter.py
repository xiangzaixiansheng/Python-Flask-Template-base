# -*- coding: utf-8 -*-

import os
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


def _get_storage_uri():
    """根据环境选择限流存储后端"""
    redis_host = os.environ.get('REDIS_HOST', 'localhost')
    redis_port = os.environ.get('REDIS_PORT', '6379')
    if os.environ.get('FLASK_ENV') == 'production':
        return f"redis://{redis_host}:{redis_port}/3"
    return "memory://"


limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute"],
    storage_uri=_get_storage_uri(),
)


def init_limiter(app):
    """初始化限流器"""
    if app.config.get('TESTING'):
        app.config['RATELIMIT_ENABLED'] = False

    limiter.init_app(app)
