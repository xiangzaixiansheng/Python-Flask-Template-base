# -*- coding: utf-8 -*-

"""
异步任务定义

所有 Celery 任务放在此目录下。

使用示例:
    from app.tasks import send_email_task
    send_email_task.delay('user@example.com', '标题', '内容')

启动 worker:
    celery -A app.common.celery_app.celery worker --loglevel=info
"""

try:
    from app.common.celery_app import celery

    if celery:
        @celery.task(bind=True, max_retries=3)
        def send_email_task(self, to, subject, body, html=False):
            """异步发送邮件"""
            try:
                from app.common.util.email import send_email
                return send_email(to, subject, body, html=html)
            except Exception as exc:
                self.retry(exc=exc, countdown=60)

        @celery.task
        def example_task(data):
            """示例任务"""
            return f"处理完成: {data}"
except ImportError:
    pass
