# -*- coding: utf-8 -*-

import time
import threading


class SnowflakeIDGenerator:
    """雪花算法 ID 生成器

    生成 64 位唯一 ID:
    - 1 bit: 符号位
    - 41 bit: 时间戳 (毫秒级，可用约69年)
    - 5 bit: 数据中心 ID (0-31)
    - 5 bit: 机器 ID (0-31)
    - 12 bit: 序列号 (同毫秒内最多 4096 个)
    """

    EPOCH = 1704067200000  # 2024-01-01 00:00:00 UTC

    DATACENTER_BITS = 5
    WORKER_BITS = 5
    SEQUENCE_BITS = 12

    MAX_DATACENTER_ID = (1 << DATACENTER_BITS) - 1
    MAX_WORKER_ID = (1 << WORKER_BITS) - 1
    MAX_SEQUENCE = (1 << SEQUENCE_BITS) - 1

    WORKER_SHIFT = SEQUENCE_BITS
    DATACENTER_SHIFT = SEQUENCE_BITS + WORKER_BITS
    TIMESTAMP_SHIFT = SEQUENCE_BITS + WORKER_BITS + DATACENTER_BITS

    def __init__(self, datacenter_id=0, worker_id=0):
        if datacenter_id > self.MAX_DATACENTER_ID or datacenter_id < 0:
            raise ValueError(f"datacenter_id 范围: 0-{self.MAX_DATACENTER_ID}")
        if worker_id > self.MAX_WORKER_ID or worker_id < 0:
            raise ValueError(f"worker_id 范围: 0-{self.MAX_WORKER_ID}")

        self.datacenter_id = datacenter_id
        self.worker_id = worker_id
        self.sequence = 0
        self.last_timestamp = -1
        self._lock = threading.Lock()

    def _current_millis(self):
        return int(time.time() * 1000)

    def generate(self):
        """生成一个唯一 ID"""
        with self._lock:
            timestamp = self._current_millis()

            if timestamp == self.last_timestamp:
                self.sequence = (self.sequence + 1) & self.MAX_SEQUENCE
                if self.sequence == 0:
                    while timestamp <= self.last_timestamp:
                        timestamp = self._current_millis()
            else:
                self.sequence = 0

            self.last_timestamp = timestamp

            return (
                ((timestamp - self.EPOCH) << self.TIMESTAMP_SHIFT) |
                (self.datacenter_id << self.DATACENTER_SHIFT) |
                (self.worker_id << self.WORKER_SHIFT) |
                self.sequence
            )


# 默认实例
_generator = SnowflakeIDGenerator(datacenter_id=0, worker_id=0)


def generate_id():
    """生成唯一 ID (使用默认生成器)"""
    return _generator.generate()
