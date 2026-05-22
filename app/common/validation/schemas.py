# -*- coding: utf-8 -*-

from marshmallow import Schema, fields, validate


class UserCreateSchema(Schema):
    username = fields.String(
        required=True,
        validate=validate.Length(min=3, max=80),
        error_messages={"required": "用户名为必填项"}
    )
    password = fields.String(
        required=True,
        validate=validate.Length(min=6, max=128),
        error_messages={"required": "密码为必填项"}
    )
    email = fields.Email(
        required=True,
        error_messages={"required": "邮箱为必填项", "invalid": "邮箱格式不正确"}
    )


class LoginSchema(Schema):
    username = fields.String(
        required=True,
        validate=validate.Length(min=1),
        error_messages={"required": "用户名为必填项"}
    )
    password = fields.String(
        required=True,
        validate=validate.Length(min=1),
        error_messages={"required": "密码为必填项"}
    )


class UserUpdateSchema(Schema):
    username = fields.String(validate=validate.Length(min=3, max=80))
    email = fields.Email(error_messages={"invalid": "邮箱格式不正确"})
    is_active = fields.Boolean()


class PaginationSchema(Schema):
    page = fields.Integer(load_default=1, validate=validate.Range(min=1))
    per_page = fields.Integer(load_default=20, validate=validate.Range(min=1, max=100))
