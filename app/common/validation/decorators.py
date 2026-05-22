# -*- coding: utf-8 -*-

import functools
from flask import request
from marshmallow import ValidationError
from app.common.result.result import Result


def validate_json(schema_cls):
    """请求 JSON 参数校验装饰器

    Usage:
        @validate_json(UserCreateSchema)
        def create_user():
            data = request.validated_data
            ...
    """
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            json_data = request.get_json(silent=True)
            if json_data is None:
                return Result.failed(400, '请求体必须为 JSON 格式')

            schema = schema_cls()
            try:
                validated = schema.load(json_data)
                request.validated_data = validated
            except ValidationError as e:
                errors = e.messages
                first_error = next(iter(errors.values()))[0] if errors else '参数验证失败'
                return Result.failed(422, first_error)

            return f(*args, **kwargs)
        return wrapper
    return decorator
