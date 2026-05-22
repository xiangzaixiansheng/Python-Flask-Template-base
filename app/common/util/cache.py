# -*- coding: utf-8 -*-

import json
import functools
from app.extension import rd
from app.common.util.log_handler import log


def cache(ttl=300, key_prefix=''):
    """Redis 缓存装饰器

    Args:
        ttl: 缓存过期时间（秒），默认 5 分钟
        key_prefix: 缓存 key 前缀
    """
    def decorator(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            if rd is None:
                return f(*args, **kwargs)

            cache_key = f"{key_prefix}:{f.__name__}:{str(args)}:{str(kwargs)}"
            try:
                cached = rd.get(cache_key)
                if cached:
                    return json.loads(cached)
            except Exception as e:
                log.error(f"Cache read error: {e}")

            result = f(*args, **kwargs)

            try:
                rd.setex(cache_key, ttl, json.dumps(result, ensure_ascii=False, default=str))
            except Exception as e:
                log.error(f"Cache write error: {e}")

            return result
        return wrapper
    return decorator


def clear_cache(pattern='*'):
    """清除匹配模式的缓存"""
    if rd is None:
        return
    try:
        keys = rd.keys(pattern)
        if keys:
            rd.delete(*keys)
    except Exception as e:
        log.error(f"Cache clear error: {e}")
