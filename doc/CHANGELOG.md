# Changelog

## v2.0.0 (2026-05-22) - 全面优化重构

### 安全修复 (Critical)

- **修复 JWT 密钥不一致**: 签发 token 使用 `SECRET_KEY`，验证却用 `JWT_SECRET_KEY`，导致所有 token 验证失败。现统一使用 `JWT_SECRET_KEY`
- **移除硬编码密钥**: `config.py` 中 `JWT_SECRET_KEY = 'dsjkflk-5707-...'` 改为环境变量读取
- **清理泄露凭据**: `.env` 中的真实数据库凭据替换为占位符
- **移除数据库文件**: `flower.db` 从 git 追踪中移除

### 架构重构

- **Result 类重写**: 原来返回 `jsonify().get_json()` (dict)，现在返回 `(Response, status_code)` 元组，正确携带 HTTP 状态码
- **Config 延迟验证**: 不再在 `import` 时抛异常崩溃，改为 `create_app()` 中调用 `validate()` 方法
- **Blueprint 统一**: 
  - `demo_controller.py` 中 `app = Blueprint('app', ...)` 重命名为 `demo_bp = Blueprint('demo', ...)`
  - 所有路由统一添加 `/api` 前缀
- **登录响应统一**: 原来 login 用 `make_response(jsonify(...))` 与其他接口格式不同，现统一使用 `Result.success()`
- **错误码集成**: `code.py` 中定义的错误码现在被 `Result.failed()` 引用

### 代码质量

- **修复 Scheduler 逻辑**: `if not app.debug or app.testing` 导致开发环境永远不启动定时任务，改为 `WERKZEUG_RUN_MAIN` 检测
- **修复废弃 API**: `datetime.utcnow` (Python 3.12 废弃) 替换为 `datetime.now(timezone.utc)`
- **移除 print 语句**: `log_handler.py` 的 `print()` 和 `MySQLUtil.py` 的 `print()` 全部替换为 `log.error()`
- **输入校验**: `demo_controller.py` 中 `int(request.form.get('param2'))` 的空值崩溃问题修复
- **Model 表名**: `users_test` 改为 `users`

### 新增功能

- **全局异常处理器** (`app/common/error_handlers.py`): 统一处理 400/404/405/413/429/500/ValidationError
- **健康检查端点** (`/health`): 检测 DB + Redis 连通性，用于 Docker/K8s 探针
- **Token 刷新机制**: access_token (1h) + refresh_token (15d) 双 token 模式
- **登出端点**: `POST /api/user/logout` 清除 cookie
- **请求参数校验**: marshmallow schema + `@validate_json` 装饰器
- **请求限流**: flask-limiter，登录 5次/分钟，全局 100次/分钟
- **文件上传**: `POST /api/upload`，支持类型/大小校验
- **分页工具**: `paginate_query()` (ORM) + `paginate_list()` (列表) + `Result.page()` 响应
- **Redis 缓存装饰器**: `@cache(ttl=300)` 自动缓存函数返回值
- **环境变量校验工具**: 启动时友好提示缺失配置

### 依赖变更

| 操作 | 包 | 原因 |
|------|-----|------|
| 新增 | `PyJWT>=2.9.0` | 实际使用但未声明 |
| 新增 | `marshmallow>=3.21.0` | 请求参数校验 |
| 新增 | `flask-limiter>=3.5.1` | 请求限流 |
| 新增 | `gunicorn>=22.0.0` | 生产 WSGI 服务器 |
| 移除 | `flask-jwt-extended` | 从未使用 |
| 移除 | `Flask_HTTPAuth` | 从未使用 |

### DevOps

- **Dockerfile**: python:3.11-slim + gunicorn，4 workers
- **docker-compose.yml**: app + MySQL 8.0 + Redis 7，含健康检查
- **Makefile**: install / run / test / lint / format / docker-up / docker-down
- **GitHub Actions CI**: lint + pytest + coverage 门控
- **pyproject.toml**: pytest / black / isort / flake8 统一配置

### 测试

- pytest 基础设施 (SQLite 内存数据库，无需真实 DB)
- 22 个测试用例，覆盖: Result 类 / JWT 工具 / 分页 / 用户 CRUD / 认证流程 / 健康检查

---

## v1.0.0 - 初始版本

- Flask 分层架构模板 (Controller -> Service -> DAO -> Model)
- 基础 JWT 认证
- Swagger API 文档
- MySQL + Redis 支持
- APScheduler 定时任务
