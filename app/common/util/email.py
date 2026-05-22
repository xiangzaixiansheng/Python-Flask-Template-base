# -*- coding: utf-8 -*-

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from app.common.util.log_handler import log


class EmailSender:
    """邮件发送工具

    配置环境变量:
        MAIL_HOST: SMTP 服务器地址
        MAIL_PORT: SMTP 端口 (默认 465 SSL)
        MAIL_USER: 发送者邮箱
        MAIL_*: 邮箱密码或授权码
        MAIL_FROM_NAME: 发送者名称
    """

    def __init__(self):
        self.host = os.environ.get('MAIL_HOST', 'smtp.qq.com')
        self.port = int(os.environ.get('MAIL_PORT', 465))
        self.user = os.environ.get('MAIL_USER', '')
        self.passwd = os.environ.get('MAIL_*', '')
        self.from_name = os.environ.get('MAIL_FROM_NAME', 'System')

    def send(self, to, subject, body, html=False, attachments=None):
        """发送邮件

        Args:
            to: 收件人 (str 或 list)
            subject: 邮件主题
            body: 邮件正文
            html: 是否为 HTML 格式
            attachments: 附件文件路径列表

        Returns:
            bool: 是否发送成功
        """
        if not self.user or not self.passwd:
            log.error("邮件配置不完整，请设置 MAIL_USER 和 MAIL_* 环境变量")
            return False

        if isinstance(to, str):
            to = [to]

        msg = MIMEMultipart()
        msg['From'] = f"{self.from_name} <{self.user}>"
        msg['To'] = ', '.join(to)
        msg['Subject'] = subject

        content_type = 'html' if html else 'plain'
        msg.attach(MIMEText(body, content_type, 'utf-8'))

        if attachments:
            for filepath in attachments:
                if os.path.exists(filepath):
                    with open(filepath, 'rb') as f:
                        part = MIMEBase('application', 'octet-stream')
                        part.set_payload(f.read())
                        encoders.encode_base64(part)
                        part.add_header(
                            'Content-Disposition',
                            f'attachment; filename={os.path.basename(filepath)}'
                        )
                        msg.attach(part)

        try:
            server = smtplib.SMTP_SSL(self.host, self.port)
            server.login(self.user, self.passwd)
            server.sendmail(self.user, to, msg.as_string())
            server.quit()
            log.info(f"邮件发送成功: to={to}, subject={subject}")
            return True
        except Exception as e:
            log.error(f"邮件发送失败: {e}")
            return False


# 默认实例
email_sender = EmailSender()


def send_email(to, subject, body, html=False):
    """快捷发送邮件"""
    return email_sender.send(to, subject, body, html=html)
