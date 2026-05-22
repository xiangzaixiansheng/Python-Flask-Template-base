# -*- coding: utf-8 -*-

import uuid
from flask import request, g
from app.common.util.log_handler import log


def init_request_id(app):
    """注册请求 ID 中间件，用于链路追踪"""

    @app.before_request
    def set_request_id():
        request_id = request.headers.get('X-Request-ID', str(uuid.uuid4()))
        g.request_id = request_id

    @app.after_request
    def add_request_id_header(response):
        request_id = getattr(g, 'request_id', None)
        if request_id:
            response.headers['X-Request-ID'] = request_id
        return response
