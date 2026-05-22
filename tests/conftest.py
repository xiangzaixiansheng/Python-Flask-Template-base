# -*- coding: utf-8 -*-

import os
import pytest

os.environ.setdefault('FLASK_ENV', 'testing')
os.environ.setdefault('KEY', 'test-*-key-for-testing')

from app import create_app
from app.extension import db as _db


@pytest.fixture(scope='session')
def app():
    """创建测试用 Flask 应用"""
    app = create_app('testing')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True
    app.config['JWT_*_KEY'] = 'test-jwt-*'

    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture(scope='function')
def db(app):
    """每个测试函数使用独立的数据库事务"""
    with app.app_context():
        _db.create_all()
        yield _db
        _db.session.rollback()
        _db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """Flask 测试客户端"""
    return app.test_client()


@pytest.fixture(scope='function')
def runner(app):
    """Flask CLI 测试运行器"""
    return app.test_cli_runner()
