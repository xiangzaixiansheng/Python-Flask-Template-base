# 工具类使用指南

## 目录

- [请求链路追踪 (Request ID)](#请求链路追踪)
- [Base Model (软删除 + 雪花ID)](#base-model)
- [HTTP Client](#http-client)
- [加解密工具](#加解密工具)
- [雪花 ID 生成器](#雪花-id-生成器)
- [Excel/CSV 导出](#excelcsv-导出)
- [邮件发送](#邮件发送)
- [验证码](#验证码)
- [审计日志](#审计日志)
- [RBAC 权限控制](#rbac-权限控制)
- [API 版本管理](#api-版本管理)
- [Celery 异步任务](#celery-异步任务)
- [Redis 缓存装饰器](#redis-缓存装饰器)
- [分页工具](#分页工具)
- [请求参数校验](#请求参数校验)

---

## 请求链路追踪

每个请求自动生成唯一 `X-Request-ID`，贯穿日志和下游调用。

```python
# 响应头自动携带
# X-Request-ID: 550e8400-e29b-41d4-a716-446655440000

# 在代码中获取
from flask import g
request_id = g.request_id
```

客户端可通过请求头传入自定义 ID:
```
X-Request-ID: my-custom-trace-id
```

---

## Base Model

所有业务 Model 应继承 `BaseModel`，自动获得:
- 雪花 ID (分布式唯一)
- created_at / updated_at (自动维护)
- 软删除 (is_deleted + deleted_at)

```python
from app.api.models.base import BaseModel
from app.extension import db

class Article(BaseModel):
    __tablename__ = 'articles'
    
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text)
    author_id = db.Column(db.Integer, nullable=False)
```

### 软删除操作

```python
# 软删除
article.soft_delete()
db.session.commit()

# 恢复
article.restore()
db.session.commit()

# 查询 (自动排除已删除)
articles = Article.query_active().filter_by(author_id=1).all()
```

---

## HTTP Client

封装外部 API 调用，自动传递 Request ID。

```python
from app.common.util.http_client import HttpClient

# 创建实例
client = HttpClient(base_url='https://api.example.com', timeout=10)

# GET
data = client.get('/users', params={'page': 1})

# POST
result = client.post('/orders', json={'item': 'book', 'qty': 1})

# 带自定义 Header
result = client.get('/private', headers={'Authorization': 'Bearer xxx'})
```

---

## 加解密工具

```python
from app.common.util.crypto import AESCipher, md5, sha256, generate_random_string

# AES 加解密 (需 pip install pycryptodome)
cipher = AESCipher('your-*-key')
encrypted = cipher.encrypt('敏感数据')
decrypted = cipher.decrypt(encrypted)

# 哈希
hash_val = md5('hello')
hash_val = sha256('hello')

# 随机字符串
token = generate_random_string(32)
```

---

## 雪花 ID 生成器

```python
from app.common.util.snowflake import generate_id, SnowflakeIDGenerator

# 使用默认生成器
uid = generate_id()  # 如: 7234567890123456789

# 自定义 datacenter + worker
gen = SnowflakeIDGenerator(datacenter_id=1, worker_id=3)
uid = gen.generate()
```

---

## Excel/CSV 导出

```python
from app.common.util.export import export_csv, export_excel

headers = [
    {'key': 'id', 'label': 'ID'},
    {'key': 'username', 'label': '用户名'},
    {'key': 'email', 'label': '邮箱'},
]

# CSV 导出
users = [{'id': 1, 'username': 'admin', 'email': 'a@b.com'}]
return export_csv(users, headers, filename='users.csv')

# Excel 导出 (需 pip install openpyxl)
return export_excel(users, headers, filename='users.xlsx')
```

---

## 邮件发送

配置环境变量:
```bash
MAIL_HOST=smtp.qq.com
MAIL_PORT=465
MAIL_USER=your@qq.com
MAIL_*=your_auth_code
```

```python
from app.common.util.email import send_email

# 纯文本
send_email('user@example.com', '标题', '邮件内容')

# HTML
send_email('user@example.com', '标题', '<h1>Hello</h1>', html=True)

# 异步发送 (Celery)
from app.tasks import send_email_task
send_email_task.delay('user@example.com', '标题', '内容')
```

---

## 验证码

基于 Redis 存储，支持频率限制和一次性验证。

```python
from app.common.util.verification_code import VerificationCode

# 生成验证码 (返回 None 表示频率限制，60秒内只能发1次)
code = VerificationCode.generate('13800138000')  # 如: '843921'
if code is None:
    return Result.failed(429, '验证码发送过于频繁')

# 发送验证码 (通过邮件或短信)
send_sms(phone, f'您的验证码是: {code}')

# 验证 (验证后自动失效)
is_valid = VerificationCode.verify('13800138000', user_input_code)
if not is_valid:
    return Result.failed(400, '验证码错误或已过期')

# 查询剩余有效时间
ttl = VerificationCode.get_ttl('13800138000')  # 秒
```

---

## 审计日志

记录关键业务操作，便于追溯。

```python
from app.common.util.audit_log import record_audit, audit

# 手动记录
record_audit(
    action='create_order',
    resource_type='order',
    resource_id=order.id,
    detail=f'创建订单，金额: {amount}'
)

# 装饰器自动记录
@user_bp.route('/users/<int:user_id>', methods=['DELETE'])
@token_required
@audit('delete_user', 'user')
def delete_user(user_id):
    ...
```

审计日志表字段:
- user_id: 操作人
- action: 操作类型
- resource_type: 资源类型
- resource_id: 资源 ID
- detail: 详情
- ip_address: IP
- request_id: 链路 ID
- created_at: 操作时间

---

## RBAC 权限控制

### 角色权限

```python
from app.middleware.rbac import role_required, permission_required
from app.middleware.authMiddleware import token_required

# 仅管理员
@user_bp.route('/admin/users', methods=['GET'])
@token_required
@role_required('admin')
def admin_list_users():
    ...

# 管理员或编辑
@article_bp.route('/articles', methods=['POST'])
@token_required
@role_required('admin', 'editor')
def create_article():
    ...
```

### 细粒度权限

```python
@order_bp.route('/orders/<int:id>', methods=['DELETE'])
@token_required
@permission_required('order:delete')
def delete_order(id):
    ...
```

**前置条件**: 在 `authMiddleware.py` 的 token 解码后，将用户角色写入 `g.current_role`。

---

## API 版本管理

```
app/api/
├── __init__.py          # 当前版本路由 (默认)
├── v1/
│   ├── __init__.py      # v1 蓝图注册
│   └── user.py          # v1 用户接口
└── v2/
    ├── __init__.py
    └── user.py          # v2 用户接口 (新字段/新逻辑)
```

注册方式 (在 `app/api/__init__.py`):
```python
from app.api.v1 import v1_bp

DEFAULT_BLUEPRINT = [
    ...
    (v1_bp, '/api/v1', False),  # /api/v1/user/...
]
```

---

## Celery 异步任务

### 安装

```bash
pip install celery[redis]
```

### 定义任务

```python
# app/tasks/__init__.py
from app.common.celery_app import celery

@celery.task(bind=True, max_retries=3)
def process_data(self, data):
    try:
        # 耗时操作
        result = heavy_computation(data)
        return result
    except Exception as exc:
        self.retry(exc=exc, countdown=60)
```

### 调用

```python
from app.tasks import process_data
process_data.delay({'key': 'value'})  # 异步执行
```

### 启动 Worker

```bash
celery -A app.common.celery_app.celery worker --loglevel=info
celery -A app.common.celery_app.celery beat --loglevel=info  # 定时任务
```

---

## Redis 缓存装饰器

```python
from app.common.util.cache import cache, clear_cache

@cache(ttl=300, key_prefix='user')
def get_user_info(user_id):
    # 5分钟内相同参数会返回缓存结果
    return db.session.get(User, user_id).to_dict()

# 清除缓存
clear_cache('user:*')
```

---

## 分页工具

```python
from app.common.util.pagination import paginate_query, get_page_params
from app.common.result.result import Result

@user_bp.route('/users', methods=['GET'])
def list_users():
    page, per_page = get_page_params()  # 从 ?page=1&per_page=20 获取
    
    query = User.query_active().order_by(User.created_at.desc())
    result = paginate_query(query, page, per_page)
    
    items = [u.to_dict() for u in result['items']]
    return Result.page(items, result['total'], page, per_page)
```

---

## 请求参数校验

```python
from app.common.validation.decorators import validate_json
from marshmallow import Schema, fields, validate

class CreateOrderSchema(Schema):
    product_id = fields.Integer(required=True)
    quantity = fields.Integer(required=True, validate=validate.Range(min=1))
    address = fields.String(required=True, validate=validate.Length(min=5))

@order_bp.route('/orders', methods=['POST'])
@validate_json(CreateOrderSchema)
def create_order():
    data = request.validated_data  # 已校验的数据
    ...
```

校验失败自动返回:
```json
{
    "code": 422,
    "msg": "quantity: 数值必须大于等于1",
    "data": {}
}
```
