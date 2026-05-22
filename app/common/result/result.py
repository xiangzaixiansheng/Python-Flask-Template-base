# -*- coding: utf-8 -*-

from flask import jsonify

from app.common.result.code import get_message


class Result:

    @staticmethod
    def success(data=None, message="操作成功"):
        """成功响应"""
        response = {
            "code": 200,
            "msg": message,
            "data": data if data is not None else {}
        }
        return jsonify(response), 200

    @staticmethod
    def failed(code, message=None):
        """失败响应"""
        msg = message or get_message(code)
        response = {
            "code": code,
            "msg": msg,
            "data": {}
        }
        http_status = 200
        if code == 401:
            http_status = 401
        elif code == 403:
            http_status = 403
        elif code == 404:
            http_status = 404
        elif code >= 500:
            http_status = 500
        return jsonify(response), http_status

    @staticmethod
    def page(items, total, page, per_page):
        """分页响应"""
        response = {
            "code": 200,
            "msg": "操作成功",
            "data": {
                "items": items,
                "total": total,
                "page": page,
                "per_page": per_page,
                "pages": (total + per_page - 1) // per_page if per_page > 0 else 0
            }
        }
        return jsonify(response), 200
