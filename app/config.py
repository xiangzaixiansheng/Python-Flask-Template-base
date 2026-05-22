# -*- coding: utf-8 -*-

import os
import datetime
from urllib.parse import quote_plus

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
url_path_prefix = '/api'


def get_db_uri(host, user, password, db_name, port=3306):
    """生成数据库URI"""
    encoded_password = quote_plus(password)
    return f'mysql+pymysql://{user}:{encoded_password}@{host}:{port}/{db_name}'


class Config:
    """基础配置类 - 不在类加载时做验证，延迟到 create_app() 中"""

    SECRET_KEY = os.environ.get('KEY', '')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', '') or os.environ.get('KEY', '')

    DB_HOST = os.environ.get('DB_HOST', '')
    DB_USER = os.environ.get('DB_USER', '')
    DB_PASSWORD = os.environ.get('DB_PASSWORD', '')
    DB_NAME = os.environ.get('DB_NAME', '')
    DB_PORT = int(os.environ.get('DB_PORT', 3306))

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False

    REDIS_HOST = os.environ.get('REDIS_HOST', 'localhost')
    REDIS_PORT = int(os.environ.get('REDIS_PORT', 6379))

    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = datetime.timedelta(days=15)

    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER', 'uploads')
    MAX_CONTENT_LENGTH = int(os.environ.get('MAX_CONTENT_LENGTH', 16 * 1024 * 1024))

    RATE_LIMIT_DEFAULT = os.environ.get('RATE_LIMIT_DEFAULT', '100/minute')
    RATE_LIMIT_LOGIN = os.environ.get('RATE_LIMIT_LOGIN', '5/minute')

    @classmethod
    def validate(cls):
        """验证必要配置项，在 create_app() 中调用"""
        errors = []
        if not cls.SECRET_KEY:
            errors.append('KEY')
        required_db = {'DB_HOST': cls.DB_HOST, 'DB_USER': cls.DB_USER,
                       'DB_PASSWORD': cls.DB_PASSWORD, 'DB_NAME': cls.DB_NAME}
        for key, value in required_db.items():
            if not value:
                errors.append(key)
        if errors:
            raise ValueError(
                f"\n{'='*50}\n"
                f"  缺少必要的环境变量: {', '.join(errors)}\n"
                f"  请参考 .env.example 配置 .env 文件\n"
                f"{'='*50}"
            )

    @classmethod
    def get_sqlalchemy_uri(cls):
        """动态生成数据库 URI"""
        return get_db_uri(cls.DB_HOST, cls.DB_USER, cls.DB_PASSWORD, cls.DB_NAME, cls.DB_PORT)


class DevelopmentConfig(Config):
    ENV = 'development'
    DEBUG = True
    SQLALCHEMY_ECHO = True


class TestingConfig(Config):
    ENV = 'testing'
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

    @classmethod
    def validate(cls):
        """测试环境不强制要求数据库配置"""
        if not cls.SECRET_KEY:
            cls.SECRET_KEY = 'test-secret-key'
        if not cls.JWT_SECRET_KEY:
            cls.JWT_SECRET_KEY = cls.SECRET_KEY

    @classmethod
    def get_sqlalchemy_uri(cls):
        return 'sqlite:///:memory:'


class ProductionConfig(Config):
    ENV = 'production'
    DEBUG = False


config = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig
}


db_util = None


def get_db_util():
    """获取数据库连接工具类实例（延迟初始化）"""
    global db_util
    if db_util is None:
        from app.common.util.MySQLUtil import DBUtil
        env = os.environ.get('FLASK_ENV', 'development')
        config_cls = config.get(env, Config)
        db_util = DBUtil(
            config_cls.DB_HOST,
            config_cls.DB_USER,
            config_cls.DB_PASSWORD,
            config_cls.DB_NAME,
            config_cls.DB_PORT
        )
    return db_util
