# -*- coding: utf-8 -*-

"""
Celery 异步任务配置

使用步骤:
1. 安装: pip install celery[redis]
2. 配置环境变量: CELERY_BROKER_URL=redis://localhost:6379/1
3. 启动 worker: celery -A app.common.celery_app.celery worker --loglevel=info
4. 启动 beat (定时任务): celery -A app.common.celery_app.celery beat --loglevel=info

使用示例:
    from app.common.celery_app import celery

    @celery.task
    def send_email_task(to, subject, body):
        from app.common.util.email import send_email
        return send_email(to, subject, body)

    # 调用
    send_email_task.delay('user@example.com', '标题', '内容')
"""

import os

try:
    from celery import Celery
    from celery.schedules import crontab
except ImportError:
    Celery = None
    crontab = None

CELERY_BROKER_URL = os.environ.get('CELERY_BROKER_URL', 'redis://localhost:6379/1')
CELERY_RESULT_BACKEND = os.environ.get('CELERY_RESULT_BACKEND', 'redis://localhost:6379/2')


def make_celery(app=None):
    """创建 Celery 实例"""
    if Celery is None:
        raise ImportError("请安装 celery: pip install celery[redis]")

    celery = Celery(
        'app',
        broker=CELERY_BROKER_URL,
        backend=CELERY_RESULT_BACKEND,
    )

    celery.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='Asia/Shanghai',
        enable_utc=True,
        task_track_started=True,
        task_time_limit=300,
        worker_max_tasks_per_child=1000,
    )

    # 定时任务示例
    celery.conf.beat_schedule = {
        # 'cleanup-expired-tokens': {
        #     'task': 'app.tasks.cleanup_expired_tokens',
        #     'schedule': crontab(hour=2, minute=0),  # 每天凌晨2点
        # },
    }

    if app:
        celery.conf.update(app.config)

        class ContextTask(celery.Task):
            def __call__(self, *args, **kwargs):
                with app.app_context():
                    return self.run(*args, **kwargs)

        celery.Task = ContextTask

    return celery


# 可直接 import 使用的实例 (worker 启动时加载)
if Celery is not None:
    celery = make_celery()
else:
    celery = None
