# -*- coding: utf-8 -*-

import json


def test_create_user(client, db):
    """测试创建用户"""
    response = client.post('/api/user/users', json={
        "username": "testuser",
        "password": "test123456",
        "email": "test@example.com"
    })
    data = json.loads(response.data)
    assert data["code"] == 200
    assert data["data"]["username"] == "testuser"
    assert data["data"]["email"] == "test@example.com"


def test_create_user_missing_fields(client, db):
    """测试创建用户 - 缺少字段"""
    response = client.post('/api/user/users', json={
        "username": "testuser"
    })
    data = json.loads(response.data)
    assert data["code"] == 400


def test_login(client, db):
    """测试用户登录"""
    client.post('/api/user/users', json={
        "username": "loginuser",
        "password": "test123456",
        "email": "login@example.com"
    })

    response = client.post('/api/user/login', json={
        "username": "loginuser",
        "password": "test123456"
    })
    data = json.loads(response.data)
    assert data["code"] == 200
    assert "token" in data["data"]


def test_login_wrong_credentials(client, db):
    """测试登录 - 密码错误"""
    client.post('/api/user/users', json={
        "username": "wrongpw",
        "password": "test123456",
        "email": "wrongpw@example.com"
    })

    response = client.post('/api/user/login', json={
        "username": "wrongpw",
        "password": "wrongvalue123"
    })
    data = json.loads(response.data)
    assert data["code"] == 401


def test_get_user_unauthorized(client, db):
    """测试未授权访问"""
    response = client.get('/api/user/users/1')
    data = json.loads(response.data)
    assert data["code"] == 401


def test_logout(client, db):
    """测试用户登出"""
    response = client.post('/api/user/logout')
    data = json.loads(response.data)
    assert data["code"] == 200


def test_health_check(client):
    """测试健康检查端点"""
    response = client.get('/health')
    data = json.loads(response.data)
    assert "status" in data
    assert "services" in data
