# -*- coding: utf-8 -*-

import random
import string
from app.extension import rd
from app.common.util.log_handler import log


class VerificationCode:
    """验证码工具

    支持:
    - 生成数字验证码 / 字母数字混合码
    - 存储到 Redis (带 TTL)
    - 验证后自动失效 (一次性)
    - 频率限制 (防刷)
    """

    PREFIX = "vcode:"
    RATE_PREFIX = "vcode_rate:"
    DEFAULT_TTL = 300       # 验证码有效期: 5分钟
    RATE_LIMIT_TTL = 60     # 发送频率限制: 60秒内只能发1次

    @staticmethod
    def generate(key, length=6, digits_only=True):
        """生成验证码并存储

        Args:
            key: 唯一标识 (如手机号、邮箱)
            length: 验证码长度
            digits_only: 是否纯数字

        Returns:
            str: 验证码, None 表示频率限制
        """
        if rd is None:
            log.error("Redis 未配置，验证码功能不可用")
            return None

        rate_key = f"{VerificationCode.RATE_PREFIX}{key}"
        if rd.exists(rate_key):
            log.warning(f"验证码发送过于频繁: {key}")
            return None

        if digits_only:
            code = ''.join(random.choices(string.digits, k=length))
        else:
            code = ''.join(random.choices(string.ascii_letters + string.digits, k=length))

        cache_key = f"{VerificationCode.PREFIX}{key}"
        rd.setex(cache_key, VerificationCode.DEFAULT_TTL, code)
        rd.setex(rate_key, VerificationCode.RATE_LIMIT_TTL, '1')

        log.info(f"验证码已生成: key={key}")
        return code

    @staticmethod
    def verify(key, code):
        """验证码校验 (验证后自动失效)

        Args:
            key: 唯一标识
            code: 用户输入的验证码

        Returns:
            bool: 验证是否通过
        """
        if rd is None:
            return False

        cache_key = f"{VerificationCode.PREFIX}{key}"
        stored_code = rd.get(cache_key)

        if stored_code and stored_code == code:
            rd.delete(cache_key)
            return True
        return False

    @staticmethod
    def get_ttl(key):
        """获取验证码剩余有效时间 (秒)"""
        if rd is None:
            return 0
        cache_key = f"{VerificationCode.PREFIX}{key}"
        ttl = rd.ttl(cache_key)
        return max(0, ttl)
