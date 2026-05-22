# -*- coding: utf-8 -*-

import os
import logging
from logging.handlers import TimedRotatingFileHandler

CURRENT_PATH = os.path.dirname(os.path.abspath(__file__))
ROOT_PATH = os.path.abspath(os.path.join(CURRENT_PATH, "..", "..", ".."))
LOG_PATH = os.path.join(ROOT_PATH, 'logs')

if not os.path.exists(LOG_PATH):
    os.makedirs(LOG_PATH)


class LogHandler(logging.Logger):

    def __init__(self, name, level=logging.INFO, stream=True, file=True):
        self.name = name
        self.level = level
        logging.Logger.__init__(self, self.name, level=level)
        if stream:
            self._set_stream_handler()
        if file:
            self._set_file_handler()

    def _set_file_handler(self, level=None):
        file_name = os.path.join(LOG_PATH, f'{self.name}.log')
        file_handler = TimedRotatingFileHandler(
            filename=file_name, when='D', interval=1,
            backupCount=15, encoding="utf-8"
        )
        file_handler.suffix = '%Y%m%d.log'
        file_handler.setLevel(level or self.level)
        formatter = logging.Formatter(
            '%(asctime)s.%(msecs)03d %(levelname)s | [%(threadName)s] %(name)s [%(lineno)d] | %(filename)s %(funcName)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        self.file_handler = file_handler
        self.addHandler(file_handler)

    def _set_stream_handler(self, level=None):
        stream_handler = logging.StreamHandler()
        formatter = logging.Formatter(
            '%(asctime)s.%(msecs)03d %(levelname)s | [%(threadName)s] %(name)s [%(lineno)d] | %(filename)s %(funcName)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(level or self.level)
        self.addHandler(stream_handler)


log = LogHandler('app', level=logging.DEBUG)
