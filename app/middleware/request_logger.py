# -*- coding: utf-8 -*-

import time
from flask import request, g
from app.common.util.log_handler import log


def init_request_logger(app):
    """注册全局请求日志中间件"""

    @app.before_request
    def log_request_start():
        g.request_start_time = time.time()

    @app.after_request
    def log_request_end(response):
        duration = time.time() - getattr(g, 'request_start_time', time.time())
        duration_ms = round(duration * 1000, 2)

        request_id = getattr(g, 'request_id', '-')
        user_id = getattr(g, 'current_user', '-')

        log.info(
            f"[{request_id}] {request.method} {request.path} "
            f"-> {response.status_code} ({duration_ms}ms) "
            f"user={user_id} ip={request.remote_addr}"
        )
        return response
