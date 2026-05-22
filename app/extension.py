
# -*- coding: utf-8 -*-

from flask_sqlalchemy import SQLAlchemy
import redis

db = SQLAlchemy()

# Redis 延迟初始化
rd = None


# 注册拓展
def config_extensions(app):
    db.init_app(app)

    # 初始化 Redis（使用应用配置）
    global rd
    if rd is None:
        pool = redis.ConnectionPool(
            host=app.config.get('REDIS_HOST', 'localhost'),
            port=app.config.get('REDIS_PORT', 6379),
            decode_responses=True
        )
        rd = redis.Redis(connection_pool=pool)


