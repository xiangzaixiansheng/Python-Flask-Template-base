# 架构设计文档

## 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                      Client (Browser/App)                │
└────────────────────────────┬────────────────────────────┘
                             │ HTTP Request
                             ▼
┌─────────────────────────────────────────────────────────┐
│                      Nginx / LB                          │
└────────────────────────────┬────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────┐
│                    Flask Application                      │
│  ┌───────────────────────────────────────────────────┐  │
│  │  Middleware Layer (Rate Limiter / Auth / CORS)     │  │
│  └───────────────────────────┬───────────────────────┘  │
│                              │                           │
│  ┌───────────────────────────▼───────────────────────┐  │
│  │  Controller Layer (Blueprint Routes)              │  │
│  │  - 请求参数校验 (@validate_json)                    │  │
│  │  - 响应格式化 (Result.success / Result.failed)     │  │
│  └───────────────────────────┬───────────────────────┘  │
│                              │                           │
│  ┌───────────────────────────▼───────────────────────┐  │
│  │  Service Layer (Business Logic)                   │  │
│  │  - 业务规则处理                                     │  │
│  │  - 事务协调                                        │  │
│  └───────────────────────────┬───────────────────────┘  │
│                              │                           │
│  ┌───────────────────────────▼───────────────────────┐  │
│  │  DAO Layer (Data Access)                          │  │
│  │  - SQLAlchemy ORM (主要)                           │  │
│  │  - MySQLUtil 原生 SQL (复杂查询)                    │  │
│  └───────────────────────────┬───────────────────────┘  │
│                              │                           │
└──────────────────────────────┼───────────────────────────┘
                               │
              ┌────────────────┼────────────────┐
              ▼                ▼                ▼
        ┌──────────┐   ┌──────────┐   ┌──────────┐
        │  MySQL   │   │  Redis   │   │  File    │
        │  (Data)  │   │  (Cache) │   │  System  │
        └──────────┘   └──────────┘   └──────────┘
```

## 目录结构

```
Python-Flask-Template/
├── app/
│   ├── __init__.py              # 应用工厂 (create_app)
│   ├── config.py                # 配置类 (Dev/Test/Prod)
│   ├── extension.py             # Flask 扩展初始化 (db, redis)
│   ├── api/
│   │   ├── __init__.py          # Blueprint 注册中心
│   │   ├── controller/          # 控制器层 (路由 + 参数校验)
│   │   │   ├── user_controller.py
│   │   │   ├── demo_controller.py
│   │   │   ├── health_controller.py
│   │   │   └── upload_controller.py
│   │   ├── service/             # 服务层 (业务逻辑)
│   │   │   └── user_service.py
│   │   ├── dao/                 # 数据访问层 (数据库操作)
│   │   │   └── user_dao.py
│   │   └── models/              # 数据模型 (表定义)
│   │       └── user.py
│   ├── common/
│   │   ├── error_handlers.py    # 全局异常处理
│   │   ├── rate_limiter.py      # 请求限流
│   │   ├── result/
│   │   │   ├── result.py        # 统一响应格式
│   │   │   └── code.py          # 业务错误码
│   │   ├── util/
│   │   │   ├── jwt_util.py      # JWT 工具
│   │   │   ├── pagination.py    # 分页工具
│   │   │   ├── cache.py         # Redis 缓存装饰器
│   │   │   ├── log_handler.py   # 日志处理器
│   │   │   ├── MySQLUtil.py     # 原生 SQL 连接池
│   │   │   └── env_validator.py # 环境变量校验
│   │   └── validation/
│   │       ├── schemas.py       # marshmallow 校验规则
│   │       └── decorators.py    # @validate_json 装饰器
│   └── middleware/
│       └── authMiddleware.py    # JWT 认证中间件
├── tests/                       # 测试目录
├── doc/                         # 文档目录
├── logs/                        # 日志目录 (gitignore)
├── uploads/                     # 上传目录 (gitignore)
├── manage.py                    # 入口文件
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── requirements.txt
├── requirements-dev.txt
└── pyproject.toml
```

## 核心设计决策

### 1. 应用工厂模式

```python
def create_app(config_name='development'):
    app = Flask(__name__)
    configure_app(app, config_name)        # 加载配置 + 初始化扩展
    register_error_handlers(app)           # 全局异常处理
    config_blueprint(app)                  # 注册路由
    return app
```

**优势**: 支持多实例、方便测试、延迟初始化

### 2. 配置延迟验证

```python
class Config:
    DB_HOST = os.environ.get('DB_HOST', '')  # 不在这里崩溃

    @classmethod
    def validate(cls):                       # 在 create_app 中调用
        if not cls.DB_HOST:
            raise ValueError("缺少 DB_HOST")
```

**原因**: 避免 `import app.config` 就崩溃，使得测试和 CLI 命令可以正常执行

### 3. 双 Token 认证

```
登录 → 返回 access_token (1h) + refresh_token (15d)
请求 → Cookie: _ut=<access_token>
过期 → POST /refresh + Cookie: _rt=<refresh_token> → 新 access_token
```

**优势**: access_token 短期有效减少泄露风险，refresh_token 长期有效减少重新登录频率

### 4. 统一响应格式

```json
{
    "code": 200,
    "msg": "操作成功",
    "data": { ... }
}
```

分页响应:
```json
{
    "code": 200,
    "msg": "操作成功",
    "data": {
        "items": [...],
        "total": 100,
        "page": 1,
        "per_page": 20,
        "pages": 5
    }
}
```

### 5. 数据库双通道

| 方式 | 适用场景 | 文件 |
|------|---------|------|
| SQLAlchemy ORM | 标准 CRUD、关联查询 | `app/extension.py` |
| MySQLUtil 原生 SQL | 复杂报表、批量操作、性能敏感 | `app/common/util/MySQLUtil.py` |

## 请求生命周期

```
1. Client 发起请求
2. ProxyFix 处理代理头
3. CORS 检查
4. Rate Limiter 限流检查
5. Blueprint 路由匹配
6. @token_required 认证 (如需要)
7. @validate_json 参数校验 (如需要)
8. Controller 处理请求
9. Service 执行业务逻辑
10. DAO 操作数据库
11. Result 格式化响应
12. 全局异常处理 (如果异常)
13. 返回 JSON Response
```

## 扩展指南

### 添加新模块

1. 创建 Model: `app/api/models/xxx.py`
2. 创建 DAO: `app/api/dao/xxx_dao.py`
3. 创建 Service: `app/api/service/xxx_service.py`
4. 创建 Controller: `app/api/controller/xxx_controller.py`
5. 注册 Blueprint: 在 `app/api/__init__.py` 的 `DEFAULT_BLUEPRINT` 添加

### 添加中间件

在 `app/middleware/` 下创建装饰器，在 Controller 中使用:

```python
@xxx_bp.route('/protected', methods=['GET'])
@token_required
@your_new_middleware
def protected_route():
    ...
```

### 添加定时任务

在 `manage.py` 的 `start_scheduler()` 中添加:

```python
scheduler.add_job(func=your_task, trigger="interval", seconds=60)
```
