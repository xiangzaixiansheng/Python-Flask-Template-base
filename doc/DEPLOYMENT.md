# 部署指南

## 本地开发

### 1. 环境准备

```bash
# Python 3.11+
python --version

# 复制环境变量配置
cp .env.example .env
# 编辑 .env 填入实际配置
```

### 2. 安装依赖

```bash
make install-dev
# 或
pip install -r requirements-dev.txt -i https://mirrors.aliyun.com/pypi/simple/
```

### 3. 启动服务

```bash
make run
# 或
python manage.py
```

访问:
- API: http://localhost:3000
- Swagger: http://localhost:3000/apidocs/
- 健康检查: http://localhost:3000/health

---

## Docker 部署 (推荐)

### 一键启动

```bash
# 编辑 .env 配置
cp .env.example .env

# 启动所有服务 (app + MySQL + Redis)
make docker-up

# 查看日志
make docker-logs

# 停止
make docker-down
```

### docker-compose 服务说明

| 服务 | 端口 | 说明 |
|------|------|------|
| app | 3000 | Flask 应用 (gunicorn, 4 workers) |
| mysql | 3306 | MySQL 8.0 |
| redis | 6379 | Redis 7 |

### 自定义配置

修改 `.env` 中的以下变量:

```bash
# Docker 内部数据库连接（使用 service 名称）
DB_HOST=mysql
DB_USER=flask_user
DB_*=your_secure_*
DB_NAME=flask_app

REDIS_HOST=redis
```

---

## 生产环境部署

### 方式一: Docker 单机

```bash
# 构建镜像
docker build -t flask-app:latest .

# 运行
docker run -d \
  --name flask-app \
  -p 3000:3000 \
  --env-file .env.production \
  --restart unless-stopped \
  flask-app:latest
```

### 方式二: Docker Compose

```bash
# 使用生产配置
FLASK_ENV=production docker-compose up -d
```

### 方式三: 直接部署

```bash
# 安装依赖
pip install -r requirements.txt

# 使用 gunicorn 启动
gunicorn --bind 0.0.0.0:3000 \
         --workers 4 \
         --timeout 120 \
         --access-logfile logs/access.log \
         --error-logfile logs/error.log \
         manage:app
```

### Nginx 反向代理配置

```nginx
upstream flask_app {
    server 127.0.0.1:3000;
}

server {
    listen 80;
    server_name your-domain.com;

    client_max_body_size 16M;

    location / {
        proxy_pass http://flask_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /app/static;
        expires 30d;
    }
}
```

---

## 数据库迁移

### 首次初始化

```bash
make migrate-init
# 等同于:
# flask db init
# flask db migrate -m "initial"
# flask db upgrade
```

### 后续迁移

```bash
# 生成迁移脚本
flask db migrate -m "描述变更"

# 执行迁移
make migrate
# 或: flask db upgrade

# 回滚
flask db downgrade
```

---

## 环境变量说明

| 变量 | 必填 | 默认值 | 说明 |
|------|------|--------|------|
| `FLASK_ENV` | 否 | development | 环境: development/testing/production |
| `KEY` | **是** | - | 应用密钥 |
| `DB_HOST` | **是** | - | 数据库主机 |
| `DB_USER` | **是** | - | 数据库用户名 |
| `DB_*` | **是** | - | 数据库密码 |
| `DB_NAME` | **是** | - | 数据库名 |
| `DB_PORT` | 否 | 3306 | 数据库端口 |
| `REDIS_HOST` | 否 | localhost | Redis 主机 |
| `REDIS_PORT` | 否 | 6379 | Redis 端口 |
| `JWT_*_KEY` | 否 | = KEY | JWT 签名密钥 |
| `ALLOWED_ORIGINS` | 否 | * | CORS 允许域名 |
| `UPLOAD_FOLDER` | 否 | uploads | 文件上传目录 |
| `MAX_CONTENT_LENGTH` | 否 | 16777216 | 最大上传大小 (16MB) |
| `RATE_LIMIT_DEFAULT` | 否 | 100/minute | 全局限流 |
| `RATE_LIMIT_LOGIN` | 否 | 5/minute | 登录限流 |

---

## 健康检查与监控

### 健康检查端点

```bash
curl http://localhost:3000/health
```

### Docker 健康检查

已在 `docker-compose.yml` 中配置，所有服务都有 healthcheck:
- app: HTTP GET /health
- mysql: mysqladmin ping
- redis: redis-cli ping

### 日志

- 位置: `logs/app.log`
- 轮转: 每天一个文件，保留 15 天
- 格式: `时间 级别 | [线程] 模块 [行号] | 文件 函数 | 消息`

---

## 常见问题

### Q: 启动报 "缺少必要的环境变量"

确保 `.env` 文件存在且包含所有必填变量。参考 `.env.example`。

### Q: Docker 中 app 连不上 mysql

检查 `.env` 中 `DB_HOST` 是否设为 `mysql` (docker-compose service name)，而非 `localhost`。

### Q: 测试时报数据库连接错误

测试使用 SQLite 内存数据库，不需要真实 MySQL。确保 `FLASK_ENV=testing`。

### Q: Rate limit 429 错误

登录接口限制 5次/分钟。等待 1 分钟后重试，或在开发环境设置 `RATELIMIT_ENABLED=False`。
