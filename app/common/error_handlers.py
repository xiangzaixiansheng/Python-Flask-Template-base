# -*- coding: utf-8 -*-

from flask import jsonify
from marshmallow import ValidationError
from app.common.util.log_handler import log


def register_error_handlers(app):
    """注册全局异常处理器"""

    @app.errorhandler(400)
    def bad_request(e):
        return jsonify({"code": 400, "msg": "请求参数错误", "data": {}}), 400

    @app.errorhandler(404)
    def not_found(e):
        return jsonify({"code": 404, "msg": "请求的资源不存在", "data": {}}), 404

    @app.errorhandler(405)
    def method_not_allowed(e):
        return jsonify({"code": 405, "msg": "请求方法不允许", "data": {}}), 405

    @app.errorhandler(413)
    def request_entity_too_large(e):
        return jsonify({"code": 413, "msg": "上传文件过大", "data": {}}), 413

    @app.errorhandler(429)
    def too_many_requests(e):
        return jsonify({"code": 429, "msg": "请求过于频繁，请稍后重试", "data": {}}), 429

    @app.errorhandler(ValidationError)
    def validation_error(e):
        return jsonify({"code": 422, "msg": "参数验证失败", "data": e.messages}), 422

    @app.errorhandler(500)
    def internal_error(e):
        log.error(f"Internal Server Error: {e}")
        return jsonify({"code": 500, "msg": "服务器内部错误", "data": {}}), 500

    @app.errorhandler(Exception)
    def unhandled_exception(e):
        log.error(f"Unhandled Exception: {type(e).__name__}: {e}", exc_info=True)
        return jsonify({"code": 500, "msg": "服务器内部错误", "data": {}}), 500
