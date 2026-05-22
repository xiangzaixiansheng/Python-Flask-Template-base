# -*- coding: utf-8 -*-

import os

from flask import Flask
from flasgger import Swagger
from flask_cors import CORS
from flask_migrate import Migrate
from werkzeug.middleware.proxy_fix import ProxyFix

from app.config import config
from app.extension import db
from app.common.util.log_handler import log
from app.extension import config_extensions

swagger_config = {
    "headers": [],
    "specs": [
        {
            "endpoint": 'apispec_1',
            "route": '/apispec_1.json',
            "rule_filter": lambda rule: True,
            "model_filter": lambda tag: True,
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/apidocs/"
}

swagger_template = {
    "securityDefinitions": {"APIKeyHeader": {"type": "apiKey", "name": "Authorization", "in": "header"}},
    "info": {
        "description": "Python Flask Template API",
        "version": "1.0.0",
        "title": "API Docs",
        "contact": {
            "email": "769323156@qq.com",
            "name": "xiangzai",
        },
        "license": {
            "name": "MIT",
        }
    }
}


def configure_app(app, config_name):
    """配置应用"""
    config_cls = config.get(config_name, config['default'])

    config_cls.validate()

    app.config.from_object(config_cls)

    if 'SQLALCHEMY_DATABASE_URI' not in app.config or not app.config['SQLALCHEMY_DATABASE_URI']:
        app.config['SQLALCHEMY_DATABASE_URI'] = config_cls.get_sqlalchemy_uri()

    log.info(f"加载配置: {config_name}")

    config_extensions(app)

    Migrate(app, db)

    Swagger(app, config=swagger_config, template=swagger_template)

    from app.common.rate_limiter import init_limiter
    init_limiter(app)

    allowed_origins = os.environ.get('ALLOWED_ORIGINS', '*')
    origins_list = allowed_origins if allowed_origins == '*' else allowed_origins.split(',')
    CORS(app, resources={r'/*': {'origins': origins_list}}, supports_credentials=True)

    app.wsgi_app = ProxyFix(app.wsgi_app)

    log.info("Flask 应用配置完成")


def log_routes(app):
    """打印所有注册的路由"""
    log.info("=== 已注册的路由列表 ===")
    with app.app_context():
        routes = []
        for rule in app.url_map.iter_rules():
            methods = ','.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
            if methods:
                routes.append(f"  {methods:10} {rule.rule}")
        for route in sorted(routes):
            log.info(route)
    log.info("=== 路由列表结束 ===")


def create_app(config_name='development'):
    """Flask 应用工厂"""
    app = Flask(__name__)

    configure_app(app, config_name)

    from app.middleware.request_id import init_request_id
    from app.middleware.request_logger import init_request_logger
    init_request_id(app)
    init_request_logger(app)

    from app.common.error_handlers import register_error_handlers
    register_error_handlers(app)

    from app.api import config_blueprint
    config_blueprint(app)

    log_routes(app)

    return app
