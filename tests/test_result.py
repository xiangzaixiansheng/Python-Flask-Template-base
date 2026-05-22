# -*- coding: utf-8 -*-

import json


def test_result_success(app):
    """测试成功响应格式"""
    with app.test_request_context():
        from app.common.result.result import Result
        response, status_code = Result.success({"key": "value"})
        data = json.loads(response.get_data(as_text=True))

        assert status_code == 200
        assert data["code"] == 200
        assert data["msg"] == "操作成功"
        assert data["data"] == {"key": "value"}


def test_result_success_empty(app):
    """测试无数据的成功响应"""
    with app.test_request_context():
        from app.common.result.result import Result
        response, status_code = Result.success()
        data = json.loads(response.get_data(as_text=True))

        assert status_code == 200
        assert data["data"] == {}


def test_result_failed(app):
    """测试失败响应格式"""
    with app.test_request_context():
        from app.common.result.result import Result
        response, status_code = Result.failed(400, "参数错误")
        data = json.loads(response.get_data(as_text=True))

        assert status_code == 200
        assert data["code"] == 400
        assert data["msg"] == "参数错误"


def test_result_failed_401(app):
    """测试 401 错误返回对应 HTTP 状态码"""
    with app.test_request_context():
        from app.common.result.result import Result
        response, status_code = Result.failed(401, "未授权")
        assert status_code == 401


def test_result_failed_404(app):
    """测试 404 错误返回对应 HTTP 状态码"""
    with app.test_request_context():
        from app.common.result.result import Result
        response, status_code = Result.failed(404, "不存在")
        assert status_code == 404


def test_result_page(app):
    """测试分页响应格式"""
    with app.test_request_context():
        from app.common.result.result import Result
        response, status_code = Result.page(
            items=[{"id": 1}, {"id": 2}],
            total=10,
            page=1,
            per_page=2
        )
        data = json.loads(response.get_data(as_text=True))

        assert status_code == 200
        assert data["data"]["total"] == 10
        assert data["data"]["page"] == 1
        assert data["data"]["per_page"] == 2
        assert data["data"]["pages"] == 5
        assert len(data["data"]["items"]) == 2
