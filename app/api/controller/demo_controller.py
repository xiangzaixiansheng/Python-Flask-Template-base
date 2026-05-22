# -*- coding: utf-8 -*-

from flasgger import swag_from
from flask import Blueprint, request

from app.common.result.result import Result

demo_bp = Blueprint('demo', __name__)


@swag_from({
    'tags': ['Demo'],
    'description': '获取示例数据接口',
    'parameters': [],
    'responses': {
        200: {
            'description': '操作成功',
            'examples': {
                'application/json': {"code": 200, "msg": "操作成功", "data": {}}
            }
        },
    },
    'security': [{'APIKeyHeader': []}]
})
@demo_bp.route("/get", methods=['GET'])
def index():
    return Result.success()


@demo_bp.route("/post", methods=['POST'])
@swag_from({
    'tags': ['Demo'],
    'description': '示例 POST 请求接口',
    'parameters': [
        {'name': 'param1', 'in': 'formData', 'description': '参数1', 'type': 'string', 'required': True},
        {'name': 'param2', 'in': 'formData', 'description': '参数2', 'type': 'integer', 'required': True}
    ],
    'responses': {
        200: {
            'description': '操作成功',
            'examples': {
                'application/json': {"code": 200, "msg": "操作成功", "data": {}}
            }
        },
    },
    'security': [{'APIKeyHeader': []}]
})
def post_example():
    param1 = request.form.get('param1')
    param2 = request.form.get('param2')
    if not param1 or not param2:
        return Result.failed(400, '缺少必要参数 param1 或 param2')
    try:
        param2 = int(param2)
    except (ValueError, TypeError):
        return Result.failed(400, 'param2 必须为整数')
    return Result.success({"param1": param1, "param2": param2})


@demo_bp.route("/put", methods=['PUT'])
@swag_from({
    'tags': ['Demo'],
    'description': '示例 PUT 请求接口',
    'parameters': [
        {'name': 'param1', 'in': 'formData', 'description': '参数1', 'type': 'string', 'required': True},
        {'name': 'param2', 'in': 'formData', 'description': '参数2', 'type': 'integer', 'required': True}
    ],
    'responses': {
        200: {
            'description': '操作成功',
            'examples': {
                'application/json': {"code": 200, "msg": "操作成功", "data": {}}
            }
        },
    },
    'security': [{'APIKeyHeader': []}]
})
def put_example():
    param1 = request.form.get('param1')
    param2 = request.form.get('param2')
    if not param1 or not param2:
        return Result.failed(400, '缺少必要参数 param1 或 param2')
    try:
        param2 = int(param2)
    except (ValueError, TypeError):
        return Result.failed(400, 'param2 必须为整数')
    return Result.success({"param1": param1, "param2": param2})


@demo_bp.route("/delete", methods=['DELETE'])
@swag_from({
    'tags': ['Demo'],
    'description': '示例 DELETE 请求接口',
    'parameters': [
        {'name': 'id', 'in': 'query', 'description': 'ID', 'type': 'integer', 'required': True}
    ],
    'responses': {
        200: {
            'description': '操作成功',
            'examples': {
                'application/json': {"code": 200, "msg": "操作成功", "data": {}}
            }
        },
    },
    'security': [{'APIKeyHeader': []}]
})
def delete_example():
    id_str = request.args.get('id')
    if not id_str:
        return Result.failed(400, '缺少必要参数 id')
    try:
        id_val = int(id_str)
    except (ValueError, TypeError):
        return Result.failed(400, 'id 必须为整数')
    return Result.success({"id": id_val})
