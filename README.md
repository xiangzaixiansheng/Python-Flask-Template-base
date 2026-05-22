# Python-Flask-Template

Production-ready Flask RESTful API template with layered MVC+ architecture.

## Features

- **分层架构**: Controller → Service → DAO → Model
- **JWT 认证**: Access + Refresh 双 Token，支持 Cookie 和 Header
- **请求校验**: marshmallow schema + `@validate_json` 装饰器
- **限流保护**: flask-limiter (登录 5次/分钟，全局 100次/分钟)
- **链路追踪**: 自动生成 X-Request-ID 贯穿日志和下游调用
- **审计日志**: 操作审计记录 + 装饰器
- **RBAC 权限**: `@role_required` / `@permission_required`
- **软删除**: BaseModel 内置 is_deleted + 雪花ID
- **缓存**: Redis 缓存装饰器 `@cache(ttl=300)`
- **分页**: 通用分页工具 + `Result.page()` 响应
- **文件上传**: 类型/大小校验
- **数据导出**: CSV + Excel 导出
- **异步任务**: Celery 集成
- **健康检查**: `/health` 端点 (DB + Redis)
- **Docker**: 一键 docker-compose 启动

## Tech Stack

| 类别 | 技术 |
|------|------|
| 框架 | Flask 3.0 |
| ORM | SQLAlchemy 2.0 + Flask-Migrate |
| 认证 | PyJWT |
| 校验 | marshmallow |
| 限流 | flask-limiter |
| 缓存 | Redis |
| 文档 | Flasgger (Swagger UI) |
| 定时任务 | APScheduler |
| 异步任务 | Celery (可选) |
| 部署 | Gunicorn + Docker |
| 测试 | pytest + pytest-cov |

## Quick Start

### 1. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 填入数据库等配置
```

### 2. 安装依赖

```bash
make install
# 或
pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/
```

### 3. 启动

```bash
make run
# 或
python manage.py
```

访问：
- API: http://localhost:3000
- Swagger 文档: http://localhost:3000/apidocs/
- 健康检查: http://localhost:3000/health

### Docker 方式

```bash
make docker-up    # 启动 app + MySQL + Redis
make docker-down  # 停止
```

## Project Structure

```
Python-Flask-Template/
├── app/
│   ├── __init__.py              # 应用工厂 create_app()
│   ├── config.py                # 配置类 (Dev/Test/Prod)
│   ├── extension.py             # Flask 扩展 (db, redis)
│   ├── api/
│   │   ├── __init__.py          # Blueprint 注册
│   │   ├── controller/          # 路由 + 参数校验
│   │   ├── service/             # 业务逻辑
│   │   ├── dao/                 # 数据访问
│   │   ├── models/              # 数据模型 (BaseModel 带软删除)
│   │   └── v1/                  # API 版本管理
│   ├── common/
│   │   ├── error_handlers.py    # 全局异常处理
│   │   ├── rate_limiter.py      # 限流
│   │   ├── celery_app.py        # Celery 配置
│   │   ├── result/              # 统一响应 + 错误码
│   │   ├── util/                # 工具集
│   │   │   ├── jwt_util.py      # JWT
│   │   │   ├── pagination.py    # 分页
│   │   │   ├── cache.py         # Redis 缓存装饰器
│   │   │   ├── snowflake.py     # 雪花 ID
│   │   │   ├── crypto.py        # 加解密
│   │   │   ├── http_client.py   # HTTP 客户端
│   │   │   ├── export.py        # Excel/CSV 导出
│   │   │   ├── email.py         # 邮件发送
│   │   │   ├── verification_code.py  # 验证码
│   │   │   ├── audit_log.py     # 审计日志
│   │   │   └── ...
│   │   └── validation/          # marshmallow 校验
│   ├── middleware/              # 中间件
│   │   ├── authMiddleware.py    # JWT 认证
│   │   ├── rbac.py             # 角色权限
│   │   ├── request_id.py       # 链路追踪
│   │   └── request_logger.py   # 请求日志
│   └── tasks/                   # Celery 异步任务
├── tests/                       # pytest 测试
├── doc/                         # 项目文档
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── requirements.txt
└── pyproject.toml
```

## Architecture

```
Client Request
    │
    ▼
┌──────────────────────────────────────────┐
│  Middleware (Request ID → Logger → CORS) │
└──────────────────────┬───────────────────┘
                       ▼
┌──────────────────────────────────────────┐
│  Rate Limiter → Auth → RBAC             │
└──────────────────────┬───────────────────┘
                       ▼
┌──────────────────────────────────────────┐
│  Controller (校验 → 路由处理)             │
└──────────────────────┬───────────────────┘
                       ▼
┌──────────────────────────────────────────┐
│  Service (业务逻辑)                       │
└──────────────────────┬───────────────────┘
                       ▼
┌──────────────────────────────────────────┐
│  DAO (SQLAlchemy ORM / MySQLUtil 原生SQL) │
└──────────────────────┬───────────────────┘
                       ▼
              MySQL / Redis / File
```

## API Overview

| Method | Path | Description | Auth |
|--------|------|-------------|------|
| GET | `/health` | 健康检查 | No |
| POST | `/api/user/login` | 登录 | No |
| POST | `/api/user/logout` | 登出 | No |
| POST | `/api/user/refresh` | 刷新 Token | Cookie |
| POST | `/api/user/users` | 创建用户 | No |
| GET | `/api/user/users` | 用户列表 | Yes |
| GET | `/api/user/users/:id` | 用户详情 | Yes |
| PUT | `/api/user/users/:id` | 更新用户 | Yes |
| DELETE | `/api/user/users/:id` | 删除用户 | Yes |
| POST | `/api/upload` | 文件上传 | Yes |
| GET/POST/PUT/DELETE | `/api/demo/*` | 示例接口 | No |

## Commands

```bash
make install       # 安装生产依赖
make install-dev   # 安装开发依赖 (含 pytest, black, flake8)
make run           # 启动开发服务器
make test          # 运行测试 + 覆盖率
make lint          # 代码检查
make format        # 代码格式化
make docker-up     # Docker 启动
make docker-down   # Docker 停止
make migrate       # 数据库迁移
```

## Adding a New Module

1. 创建 Model: `app/api/models/xxx.py` (继承 `BaseModel`)
2. 创建 DAO: `app/api/dao/xxx_dao.py`
3. 创建 Service: `app/api/service/xxx_service.py`
4. 创建 Controller: `app/api/controller/xxx_controller.py`
5. 注册 Blueprint: `app/api/__init__.py` 的 `DEFAULT_BLUEPRINT`

## Documentation

- [架构设计](doc/ARCHITECTURE.md)
- [API 接口文档](doc/API.md)
- [部署指南](doc/DEPLOYMENT.md)
- [工具类使用指南](doc/UTILITIES.md)
- [变更记录](doc/CHANGELOG.md)

## License

MIT
