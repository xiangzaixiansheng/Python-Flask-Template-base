# -*- coding: utf-8 -*-

from app.api.controller.demo_controller import demo_bp
from app.api.controller.user_controller import user_bp
from app.api.controller.health_controller import health_bp
from app.api.controller.upload_controller import upload_bp
from app.config import url_path_prefix

DEFAULT_BLUEPRINT = [
    (health_bp, '/health', False),
    (demo_bp, '/demo', True),
    (user_bp, '/user', True),
    (upload_bp, '/upload', True),
]


def config_blueprint(app):
    for blueprint, url_prefix, add_prefix in DEFAULT_BLUEPRINT:
        if add_prefix:
            url_prefix = url_path_prefix + url_prefix
        app.register_blueprint(blueprint, url_prefix=url_prefix)
