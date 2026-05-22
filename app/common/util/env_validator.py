# -*- coding: utf-8 -*-

import os
import sys


REQUIRED_VARS = [
    ('KEY', '应用密钥，用于 session 和 JWT 签名'),
    ('DB_HOST', '数据库主机地址'),
    ('DB_USER', '数据库用户名'),
    ('DB_*', '数据库密码'),
    ('DB_NAME', '数据库名称'),
]

OPTIONAL_VARS = [
    ('DB_PORT', '数据库端口', '3306'),
    ('REDIS_HOST', 'Redis 主机地址', 'localhost'),
    ('REDIS_PORT', 'Redis 端口', '6379'),
    ('JWT_*_KEY', 'JWT 签名密钥', '使用 KEY 的值'),
    ('ALLOWED_ORIGINS', 'CORS 允许的域名', '*'),
    ('UPLOAD_FOLDER', '文件上传目录', 'uploads'),
    ('MAX_CONTENT_LENGTH', '最大上传文件大小(bytes)', '16777216'),
]


def validate_env():
    """验证环境变量配置，返回缺失的必要变量列表"""
    missing = []
    for var_name, description in REQUIRED_VARS:
        if not os.environ.get(var_name):
            missing.append((var_name, description))
    return missing


def print_env_status():
    """打印环境变量配置状态"""
    missing = validate_env()

    if missing:
        print("\n" + "=" * 60)
        print("  环境变量配置检查失败")
        print("=" * 60)
        print("\n  缺少以下必要的环境变量:\n")
        for var_name, description in missing:
            print(f"    - {var_name}: {description}")
        print("\n  请参考 .env.example 配置 .env 文件")
        print("=" * 60 + "\n")
        sys.exit(1)
