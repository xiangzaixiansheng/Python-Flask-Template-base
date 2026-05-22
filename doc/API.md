# API 接口文档

> 完整的交互式文档请访问: http://127.0.0.1:3000/apidocs/

## 基础信息

- Base URL: `http://localhost:3000`
- 认证方式: JWT (Cookie `_ut` 或 Header `Authorization: Bearer <token>`)
- 响应格式: JSON

## 通用响应结构

### 成功
```json
{
    "code": 200,
    "msg": "操作成功",
    "data": { ... }
}
```

### 失败
```json
{
    "code": 400,
    "msg": "错误描述",
    "data": {}
}
```

### HTTP 状态码映射

| 业务 code | HTTP Status | 含义 |
|-----------|-------------|------|
| 200 | 200 | 成功 |
| 400 | 200 | 参数错误 |
| 401 | 401 | 未认证 |
| 403 | 403 | 无权限 |
| 404 | 404 | 资源不存在 |
| 422 | 422 | 参数校验失败 |
| 429 | 429 | 请求过于频繁 |
| 500 | 500 | 服务器错误 |

---

## 健康检查

### GET /health

检查服务及依赖状态。

**响应示例:**
```json
{
    "status": "healthy",
    "services": {
        "database": "up",
        "redis": "up"
    }
}
```

| status | HTTP | 含义 |
|--------|------|------|
| healthy | 200 | 所有依赖正常 |
| degraded | 503 | 部分依赖不可用 |

---

## 用户认证

### POST /api/user/login

用户登录，获取 token。

**限流**: 5 次/分钟

**请求体:**
```json
{
    "username": "admin",
    "*": "123456"
}
```

**成功响应:**
```json
{
    "code": 200,
    "msg": "操作成功",
    "data": {
        "token": "eyJ...",
        "refresh_token": "eyJ...",
        "user": {
            "id": 1,
            "username": "admin",
            "email": "admin@example.com"
        }
    }
}
```

**Cookie 设置:**
- `_ut`: access token (httponly, secure, 1小时)
- `_rt`: refresh token (httponly, secure, 15天)

---

### POST /api/user/refresh

刷新 access token (需要 `_rt` cookie)。

**成功响应:**
```json
{
    "code": 200,
    "msg": "操作成功",
    "data": {
        "token": "eyJ..."
    }
}
```

---

### POST /api/user/logout

登出，清除 token cookie。

**成功响应:**
```json
{
    "code": 200,
    "msg": "登出成功",
    "data": {}
}
```

---

## 用户管理

### POST /api/user/users

创建用户。

**请求体:**
```json
{
    "username": "newuser",
    "*": "secure123",
    "email": "user@example.com"
}
```

**校验规则:**
- username: 3-80 字符
- *: 最少 6 字符
- email: 合法邮箱格式

**成功响应:**
```json
{
    "code": 200,
    "msg": "操作成功",
    "data": {
        "id": 1,
        "username": "newuser",
        "email": "user@example.com",
        "created_at": "2026-05-22T10:30:00",
        "updated_at": "2026-05-22T10:30:00",
        "is_active": true
    }
}
```

---

### GET /api/user/users

获取所有用户列表。**需要认证**

---

### GET /api/user/users/:id

获取单个用户。**需要认证**

---

### PUT /api/user/users/:id

更新用户信息。**需要认证**

**可更新字段:**
```json
{
    "username": "newname",
    "email": "new@example.com",
    "is_active": false
}
```

---

### DELETE /api/user/users/:id

删除用户。**需要认证**

---

## 文件上传

### POST /api/upload

上传文件。**需要认证**

**Content-Type:** `multipart/form-data`

**字段:**
- `file`: 文件 (必填)

**支持的文件类型:** png, jpg, jpeg, gif, pdf, doc, docx, xlsx, csv

**大小限制:** 16MB

**成功响应:**
```json
{
    "code": 200,
    "msg": "操作成功",
    "data": {
        "filename": "20260522103000_example.png",
        "original_name": "example.png",
        "size": 102400,
        "path": "uploads/20260522103000_example.png"
    }
}
```

---

## Demo 接口

### GET /api/demo/get

示例 GET 请求。

### POST /api/demo/post

示例 POST 请求。

**参数 (form-data):**
- `param1`: string (必填)
- `param2`: integer (必填)

### PUT /api/demo/put

示例 PUT 请求。参数同 POST。

### DELETE /api/demo/delete

示例 DELETE 请求。

**参数 (query):**
- `id`: integer (必填)

---

## 认证说明

需要认证的接口会检查以下位置的 token (优先级从高到低):

1. Cookie: `_ut`
2. Header: `Authorization: Bearer <token>`

Token 过期返回:
```json
{
    "code": 401,
    "msg": "Token 已过期",
    "data": {}
}
```

**处理流程:**
1. 检测到 401 响应
2. 调用 `POST /api/user/refresh` 获取新 token
3. 如果 refresh 也失败，跳转登录页
